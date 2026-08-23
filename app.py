# =====================================================
# app.py (SentinelMind AI v2.0 - Production Engine)
# Multilingual Sarcasm, Threat Intelligence & Safety Guard
# =====================================================
import os
import io
import re
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from deep_translator import GoogleTranslator
import pymupdf
from PIL import Image
import pytesseract

from language_detector import detect_language
from toxicity_model import analyze_harm_and_moderation, censor_text
from explainability import generate_intelligence_summary
from sarcasm_detector import detect_sarcasm, predict_trained_ml
from models.deberta_engine import deberta_emotion
from models.fusion_engine import fusion

app = FastAPI(
    title="SentinelMind AI Engine",
    description="Multilingual Sarcasm & Threat Intelligence Studio",
    version="2.0.0"
)

# -------------------------------------------------
# CORS Configuration
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# CODE-MIXED GLOSSARY & NORMALIZATION DICTIONARY
# -------------------------------------------------
CODE_MIX_GLOSSARY = {
    # Kannada / Kanglish
    "maga": "bro / friend",
    "guru": "master / buddy",
    "machha": "friend / buddy",
    "ivattu": "today",
    "alli": "there / at",
    "nanage": "to me / for me",
    "sikthu": "got / received",
    "beku": "want / need",
    "beda": "do not want",
    "kelsa": "work / task",
    "hegidya": "how are you",
    "yenu": "what",
    "illa": "no / not",
    "sakkat": "super / awesome",
    "chindi": "mind-blowing",
    "tumba": "very / much",
    "helthiya": "saying / telling",
    "buddhivantha": "genius / smart person",
    "madde": "did / made",
    "madbittya": "you went and did",

    # Tamil / Tanglish
    "romba": "very / extremely",
    "machan": "friend / brother",
    "seri": "okay / all right",
    "enna": "what",
    "inga": "here",
    "irukken": "am / present",
    "irukku": "is there / exists",
    "nalla": "good / fine",
    "velai": "work / task",
    "arumaiyaana": "wonderful / splendid",
    "sonnadhu": "what was said",
    "pannitu": "having done",
    "solre": "telling / saying",
    "theriyum": "known",
    "varala": "did not come",

    # Hindi / Hinglish
    "kya": "what",
    "baat": "matter / thing",
    "kamaal": "wonder / masterpiece",
    "kar": "do",
    "diya": "did / done",
    "shabash": "well done / bravo",
    "bohot": "very / much",
    "badhiya": "great / wonderful",
    "arey": "hey / oh",
    "wah": "wow / bravo",
    "bhai": "brother",
    "yaar": "friend / buddy",
    "aaj": "today",
    "toh": "then / indeed",
    "tumne": "you",
    "itni": "this much",
    "der": "late / delay",
    "se": "from / with",
    "shuru": "start / begin",
    "teer": "arrow",
    "maar": "hit / shoot",
    "mujhe": "I / to me",
    "tumhare": "your",
    "tumhara": "your",
    "tumhari": "your",
    "thoda": "a little / slightly",
    "thodi": "a little / slightly",
    "hua": "felt / happened / became",
    "hui": "felt / happened / became",
    "hai": "is",
    "hain": "are",
    "tha": "was",
    "thi": "was",
    "bahut": "very / much",
    "nahi": "not / no",
    "karna": "to do",
    "kyun": "why",
    "kaise": "how",

    # Telugu / Tenglish
    "mowa": "bro / buddy",
    "babu": "boy / mister",
    "bagunara": "are you fine",
    "cheppu": "tell / speak",
    "endi": "what is this",
    "enti": "what",
    "chesav": "you did",
    "chala": "very",
    "manchi": "good",
    "ledu": "not there / no",
    "undhi": "is there",

    # Malayalam / Manglish
    "entha": "what",
    "eda": "hey buddy",
    "machane": "friend / bro",
    "adipoli": "awesome / fantastic",
    "sheriyanu": "that is right",
    "nokku": "look / see"
}

def extract_code_mixed_glossary(text: str) -> dict:
    """Extracts slang/code-mixed terms with their English semantic gloss."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    found = {}
    for w in words:
        if w in CODE_MIX_GLOSSARY and w not in found:
            found[w] = CODE_MIX_GLOSSARY[w]
    return found

def normalize_code_mixed_to_english(text: str) -> str:
    """Pre-normalizes known code-mix slang terms for enhanced translator comprehension."""
    normalized = text
    for token, gloss in CODE_MIX_GLOSSARY.items():
        pattern = re.compile(r'\b' + re.escape(token) + r'\b', re.IGNORECASE)
        # Use simple primary translation term
        primary_gloss = gloss.split("/")[0].strip()
        normalized = pattern.sub(primary_gloss, normalized)
    return normalized

from concurrent.futures import ThreadPoolExecutor

def safe_translate(text: str, target: str) -> str:
    """Safely translates text to a target language with error guarding."""
    if not text or not text.strip():
        return ""
    try:
        translated = GoogleTranslator(source="auto", target=target).translate(text)
        if not translated or "Error 500" in translated or "<html" in translated or "That’s an error" in translated:
            return text
        return translated
    except Exception:
        return text

def build_cross_translation_matrix(text: str, lang_info: dict) -> dict:
    """
    Builds a complete multi-lingual translation matrix concurrently:
    - English Semantic Translation
    - Kannada (ಕನ್ನಡ)
    - Tamil (தமிழ்)
    - Hindi (हिन्दी)
    - Telugu (తెలుగు)
    - Code-Mixed Romanized Glossary
    """
    is_code_mixed = lang_info.get("is_code_mixed", False)
    glossary = extract_code_mixed_glossary(text)

    # 1. Determine English translation
    if lang_info.get("iso_code") == "en" and not is_code_mixed:
        english_trans = text
    else:
        english_trans = safe_translate(text, "en")
        if english_trans == text and is_code_mixed:
            norm_text = normalize_code_mixed_to_english(text)
            english_trans = safe_translate(norm_text, "en")

    # 2. Parallel translation for other target Indic languages
    base_for_indic = english_trans if is_code_mixed else text
    targets = [("kn", "Kannada"), ("ta", "Tamil"), ("hi", "Hindi"), ("te", "Telugu")]
    translations = {"en": english_trans}

    def fetch_single(code, lang_name):
        if lang_info.get("language") == lang_name:
            return code, text
        return code, safe_translate(base_for_indic, code)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_single, code, name) for code, name in targets]
        for f in futures:
            try:
                code, res = f.result(timeout=4.0)
                translations[code] = res
            except Exception:
                pass

    kn_trans = translations.get("kn", base_for_indic)
    ta_trans = translations.get("ta", base_for_indic)
    hi_trans = translations.get("hi", base_for_indic)
    te_trans = translations.get("te", base_for_indic)

    matrix_list = [
        {"language": "English", "native_name": "English", "code": "en", "translation": english_trans, "is_source": (lang_info.get("iso_code") == "en" and not is_code_mixed)},
        {"language": "Kannada", "native_name": "ಕನ್ನಡ", "code": "kn", "translation": kn_trans, "is_source": (lang_info.get("language") == "Kannada")},
        {"language": "Tamil", "native_name": "தமிழ்", "code": "ta", "translation": ta_trans, "is_source": (lang_info.get("language") == "Tamil")},
        {"language": "Hindi", "native_name": "हिन्दी", "code": "hi", "translation": hi_trans, "is_source": (lang_info.get("language") == "Hindi")},
        {"language": "Telugu", "native_name": "తెలుగు", "code": "te", "translation": te_trans, "is_source": (lang_info.get("language") == "Telugu")}
    ]

    return {
        "english_translation": english_trans,
        "kannada_translation": kn_trans,
        "tamil_translation": ta_trans,
        "hindi_translation": hi_trans,
        "telugu_translation": te_trans,
        "matrix": matrix_list,
        "code_mixed_glossary": glossary
    }

# -------------------------------------------------
# SOCIAL RELATIONSHIP DETECTION
# -------------------------------------------------
def relationship_detector(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["dad", "father", "appa", "mom", "mother", "papa", "amma", "thathaa", "aunt", "uncle"]):
        return "Parent / Child / Family"
    if any(w in t for w in ["bro", "friend", "maga", "dude", "machha", "machan", "yaar", "mowa", "buddy"]):
        return "Peer / Friends"
    if any(w in t for w in ["sir", "teacher", "madam", "professor", "boss", "manager", "colleague"]):
        return "Professional / Academic"
    if any(w in t for w in ["love", "baby", "dear", "darling", "honey", "sweetheart"]):
        return "Close Personal / Romantic"
    return "Neutral / General Context"

# -------------------------------------------------
# EMOTION HEURISTIC
# -------------------------------------------------
def rule_emotion_detector(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["hate", "angry", "furious", "annoyed", "disgusted", "irritated", "rage"]):
        return "Angry"
    if any(w in t for w in ["happy", "love", "great", "good", "proud", "delighted", "joy", "excited", "blessed"]):
        return "Positive"
    if any(w in t for w in ["sad", "depressed", "unhappy", "crying", "sorrow", "grief"]):
        return "Sadness"
    if any(w in t for w in ["fear", "scared", "terrified", "panic", "worried"]):
        return "Fear"
    return "Neutral"

# -------------------------------------------------
# PDF & IMAGE OCR EXTRACTORS
# -------------------------------------------------
def read_pdf(raw: bytes) -> str:
    text = ""
    try:
        pdf = pymupdf.open(stream=raw, filetype="pdf")
        for page in pdf:
            text += page.get_text()
    except Exception:
        pass
    return text

def read_image(raw: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(raw))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""

# -------------------------------------------------
# HOME ROUTE (Serves Studio Web UI)
# -------------------------------------------------
@app.get("/")
def home():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "SentinelMind AI Engine Running", "version": "2.0"}

# -------------------------------------------------
# API ANALYSIS PIPELINE
# -------------------------------------------------
@app.post("/analyze")
async def analyze(
    text: str = Form(""),
    file: UploadFile = File(None)
):
    content = text

    # Read Attached File if Provided (PDF/OCR)
    if file:
        try:
            raw = await file.read()
            name = file.filename.lower()
            if name.endswith(".pdf"):
                content += " " + read_pdf(raw)
            elif any(name.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                content += " " + read_image(raw)
            else:
                try:
                    content += " " + raw.decode("utf-8", errors="ignore")
                except Exception:
                    pass
        except Exception:
            pass

    content = content.strip()
    if not content:
        content = "Empty input stream"

    # 1. High-Precision Language & Dialect Detection
    lang_info = detect_language(content)
    language = lang_info["language"]
    dialect_info = lang_info["dialect_info"]
    iso_code = lang_info["iso_code"]

    # 2. Multilingual Cross-Translation Matrix & Code-Mix Glossary
    trans_matrix_data = build_cross_translation_matrix(content, lang_info)
    translation = trans_matrix_data["english_translation"]

    # 3. Context & Social Dynamics
    relationship = relationship_detector(content)
    rule_emotion = rule_emotion_detector(content)

    # 4. Multi-Tier AI Analysis: DeBERTa-v3 + Trained ML + Rule Engine
    eval_text = translation if (lang_info.get("is_code_mixed") or iso_code != "en") and translation else content
    deberta = deberta_emotion(eval_text)
    ml_pred = predict_trained_ml(content)
    if (not ml_pred or not ml_pred.get("is_sarcastic")) and translation and translation != content:
        alt_ml = predict_trained_ml(translation)
        if alt_ml and alt_ml.get("is_sarcastic"):
            ml_pred = alt_ml
    sarcasm, rule_score = detect_sarcasm(content, deberta, translation=translation)

    # 5. Hybrid Decision Fusion Engine
    fusion_result = fusion(rule_emotion, deberta, sarcasm_status=sarcasm, content=content, ml_prediction=ml_pred)
    emotion = fusion_result["emotion"]
    polarity = fusion_result.get("polarity", "Neutral")

    # 6. Multilingual Harm Moderation & Safety Guardrails
    harm_data = analyze_harm_and_moderation(content, ml_prediction=ml_pred, emotion=emotion)
    illegal = harm_data["illegal_activity"]
    risk_level = harm_data["risk_level"]
    clean_text = harm_data["clean_text"]

    # If sarcasm is detected and risk is currently LOW, escalate only if hostile/mocking
    if sarcasm == "Sarcastic" and risk_level == "LOW":
        if any(h in emotion.lower() for h in ["mockery", "disapproval", "hostil", "angry", "anger"]):
            risk_level = "MEDIUM"
            harm_data["risk_level"] = "MEDIUM"
            harm_data["moderation_status"] = "Sarcastic Irony Detected • Tone Inversion Flagged"
        else:
            harm_data["moderation_status"] = "Benign / Playful Sarcasm • Policy Approved"

    # 7. Calibrated Multi-Engine Breakdown Metrics (0.0 - 100.0%)
    deberta_conf = round(float(deberta.get("confidence", 92.0)), 1) if isinstance(deberta, dict) else 92.0
    
    # Correct scaling for trained ML probability:
    raw_ml_prob = ml_pred.get("sarcasm_prob", 90.0) if ml_pred else 90.0
    trained_ml_conf = round(float(raw_ml_prob), 1)
    # Clamp to valid 0-100% range
    if trained_ml_conf > 100.0:
        trained_ml_conf = round(trained_ml_conf / 100.0, 1)
    trained_ml_conf = min(99.5, max(10.0, trained_ml_conf))

    rule_conf = round(float(rule_score if sarcasm == "Sarcastic" else 78.0), 1)
    calibrated_conf = round(max(fusion_result["confidence"], rule_score if sarcasm == "Sarcastic" else 75.0), 1)

    # 4 Structured Engine Breakdown Cards
    engine_breakdown = [
        {
            "id": "deberta_v3",
            "name": "Microsoft DeBERTa-v3 Transformer",
            "type": "Zero-Shot Neural NLI & Emotion",
            "confidence": deberta_conf,
            "verdict": deberta.get("emotion", "Neutral").capitalize() if isinstance(deberta, dict) else "Processed",
            "status": "Active (Local Weights)"
        },
        {
            "id": "trained_ml",
            "name": "Trained Multi-Task ML Pipeline",
            "type": "TF-IDF + Scaled Classifier",
            "confidence": trained_ml_conf,
            "verdict": ml_pred.get("content_type", "safe").capitalize() if ml_pred else "Safe Content",
            "status": "Active (Calibrated ML)"
        },
        {
            "id": "contrast_rules",
            "name": "Linguistic Pattern & Contrast Engine",
            "type": "Idioms & Semantic Collision",
            "confidence": rule_conf,
            "verdict": "Semantic Contrast Flagged" if sarcasm == "Sarcastic" else "Literal Rule Alignment",
            "status": "Active (Heuristic Engine)"
        },
        {
            "id": "hybrid_fusion",
            "name": "Hybrid Decision Fusion Engine",
            "type": "Unified Multi-Model Calibration",
            "confidence": calibrated_conf,
            "verdict": f"{sarcasm} ({emotion})",
            "status": "Active (Decision Fusion)"
        }
    ]

    # 8. Dynamic Intelligence Verdict & Explainability Report
    intel_report = generate_intelligence_summary(
        text=content,
        sarcasm=sarcasm,
        emotion=emotion,
        risk=risk_level,
        language=language,
        dialect=dialect_info,
        confidence=calibrated_conf,
        harm_data=harm_data,
        ml_pred=ml_pred
    )

    # 9. Output Unified Production Payload
    return {
        # Core Clean Text & Metadata
        "clean_text": clean_text,
        "original_text": content,
        "language": language,
        "detected_language": language,
        "dialect_info": dialect_info,
        "iso_code": iso_code,
        "is_code_mixed": lang_info.get("is_code_mixed", False),

        # Multilingual Translation Matrix & Glossary
        "translation": translation,
        "translated_text": translation,
        "translation_matrix": trans_matrix_data["matrix"],
        "code_mixed_glossary": trans_matrix_data["code_mixed_glossary"],

        # Sarcasm & Nuance Verdicts
        "sarcasm": sarcasm,
        "is_sarcastic": (sarcasm == "Sarcastic"),
        "relationship": relationship,
        "rule_based_emotion": rule_emotion,
        "deberta_emotion": deberta,
        "hybrid_emotion": emotion,
        "polarity": polarity,
        "semantic_tone": fusion_result.get("semantic_tone", ""),

        # Calibrated Confidence Scores & 4-Engine Breakdown
        "confidence": calibrated_conf,
        "calibrated_confidence": calibrated_conf,
        "ml_confidence": deberta_conf,
        "deberta_confidence": deberta_conf,
        "trained_ml_confidence": trained_ml_conf,
        "rule_based_confidence": rule_conf,
        "engine_breakdown": engine_breakdown,

        # Harm Moderation & Content Guard
        "illegal_activity": illegal,
        "risk_level": risk_level,
        "moderation_action": harm_data["moderation_action"],
        "moderation_status": harm_data["moderation_status"],
        "harm_moderation": harm_data,
        "content_type": ml_pred.get("content_type", "safe") if ml_pred else "safe",

        # Dynamic Analysis Summary & Explainability
        "summary": intel_report["summary"],
        "explanation": intel_report["explanation"],
        "summary_title": intel_report["summary_title"],
        "contrast_rationale": intel_report["contrast_rationale"],
        "emotion_inversion_note": intel_report["emotion_inversion_note"],
        "linguistic_cues": intel_report["linguistic_cues"],
        "praise_anchors": intel_report["praise_anchors"],
        "destructive_anchors": intel_report["destructive_anchors"],
        "actionable_guidance": intel_report["actionable_guidance"],

        "model": "SentinelMind AI v2.0 (DeBERTa-v3 + Trained ML + Semantic Contrast)"
    }