# =====================================================
# sarcasm_detector.py
# SentinelMind AI v2.0 - Trained ML + Semantic Contrast Sarcasm Engine
# =====================================================
import os
import re
import joblib
import numpy as np
from models.feature_extractor import LinguisticAndContrastExtractor
from models.deberta_engine import analyze_deberta_sentiment_and_sarcasm

# 1. Direct Sarcastic Expressions & Hyperbolic Tropes
SARCASM_IDIOM_PATTERNS = [
    # English Sarcastic Idioms & Tropes
    r"\boh\s+(wow|great|wonderful|brilliant|fantastic|super|lovely)\b",
    r"\b(what\s+a|real)\s+(genius|brilliant|mastermind|champion|hero|superstar)\b",
    r"\byeah\s+right\b",
    r"\bthanks\s+for\s+(nothing|the\s+help|making\s+it\s+worse|ignoring)\b",
    r"\bas\s+if\b",
    r"\btotally\s+(normal|fine|helpful|working)\b",
    r"\bjust\s+love\s+(waiting|getting\s+stuck|failing|losing|destroying|crashing|ruining)\b",
    r"\bbest\s+day\s+ever\b.*\b(traffic|workday|worst|terrible|horrible|pain|failed|deleted)\b",
    r"\bwow\s+(maga|guru|bro|dude|man|sir),?\s+(super|great|amazing|kamaal)\b",

    # Kannada / Kanglish Sarcastic Idioms
    r"\b(maga|guru|anna)\s+ivattu\s+.*(promotion|office).*(wow|great|super|sikthu)\b",
    r"\b(sakkat|chindi|super)\s+(kelsa|work|madde|madbittya|timing)\b",
    r"\byen\s+(buddhivanta|genius|dodda\s+manushya)\b",
    r"\b(super|great)\s+job\s+anta\s+helthiya\b",
    r"ವಾ\s+ಸೂಪರ್",
    r"ತುಂಬಾ\s+ಒಳ್ಳೆಯ\s+ಕೆಲಸ",

    # Tamil / Tanglish Sarcastic Idioms
    r"\b(romba|sema)\s+(arumaiyaana|nalla|super)\s+(velai|work)\b.*(yeah|right|wow)?",
    r"\b(aaha|enna)\s+oru\s+(arivu|medhai|genius)\b",
    r"\b(super\s+job\s+nu\s+sollariya)\b",
    r"அருமையான\s+வேலை",
    r"சூப்பர்\s+வேலை",
    r"வாவ್\s+ரொம்ப\s+நல்லது",

    # Hindi / Hinglish Sarcastic Idioms
    r"\b(kya\s+baat|kamaal\s+kar\s+diya|shabash|bohot\s+badhiya)\b.*(der|kharab|galat|delete|fail)?",
    r"\b(wah|arey\s+wah),?\s+.*(kamaal|genius|great|teer\s+maar\s+diya|planning)\b",
    r"वाह\s+क्या\s+बात\s+है",
    r"बहुत\s+बढ़िया\s+काम\s+किया",
    r"जैसे\s+गलती\s+किसी\s+और\s+की\s+हो",
    r"जैसे\s+कुछ\s+हुआ\s+ही\s+न\s+हो",
    r"\bas\s+if\s+(it|this|that)\s+was\s+(someone|somebody|anybody)\s+else",
    r"\bbehaving\s+as\s+if\b",
    r"\bacting\s+like\s+nothing\s+happened\b"
]

# 2. Semantic Contrast Lexicons: Positive Praise + Catastrophic Event
POSITIVE_PRAISE_TERMS = [
    "super job", "great job", "good job", "nice job", "brilliant idea", "genius", 
    "masterpiece", "amazing work", "wonderful", "outstanding", "fantastic", 
    "real genius", "brilliant", "perfectly fine", "super work", "kamaal", "champion",
    "delighted", "thrilled", "what a relief", "perfect timing", "so proud", "love waiting",
    "couldn't be happier", "excellent work", "safest decision", "super", "amazing"
]

NEGATIVE_DESTRUCTIVE_TERMS = [
    "delete", "deleted", "deleting", "destroy", "destroyed", "destroying",
    "broke", "broken", "breaking", "ruin", "ruined", "ruining", "wreck", "wrecked",
    "crash", "crashed", "crashing", "fail", "failed", "failing", "failure",
    "loss", "lost", "corrupted", "corrupt", "disappeared", "forgot", "forgetting",
    "stopped working", "delayed", "delay", "miss", "missed", "broke production", "killed",
    "waste", "wasted", "mess", "screwed", "damage", "damaged", "disaster", "terrible",
    "mistake", "same mistake", "fault", "someone else's fault"
]

# Model Pipeline Cache
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "trained_sarcasm_pipeline.joblib")
_TRAINED_BUNDLE = None

def get_trained_pipeline():
    global _TRAINED_BUNDLE
    if _TRAINED_BUNDLE is None and os.path.exists(MODEL_PATH):
        try:
            _TRAINED_BUNDLE = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Warning: Could not load trained ML pipeline: {e}")
    return _TRAINED_BUNDLE

def check_semantic_contrast(text: str, translation: str = "") -> bool:
    """
    Detects classic sarcastic irony: Positive acclaim paired with a catastrophic/negative outcome.
    Example: 'Super job! You deleted the entire project and now say everything is fine.'
    """
    comb = f"{text} {translation}".lower()
    has_positive = any(term in comb for term in POSITIVE_PRAISE_TERMS)
    has_negative = any(term in comb for term in NEGATIVE_DESTRUCTIVE_TERMS)
    return has_positive and has_negative

def predict_trained_ml(text: str) -> dict:
    """
    Runs inference using the newly trained multi-task pipeline.
    """
    bundle = get_trained_pipeline()
    if bundle is None:
        return {}

    try:
        pipeline = bundle["feature_pipeline"]
        sarc_clf = bundle["sarcasm_classifier"]
        cont_clf = bundle["content_classifier"]
        risk_clf = bundle["risk_classifier"]
        emo_clf = bundle["emotion_classifier"]

        feats = pipeline.transform([text])
        
        # Sarcasm prediction & probability
        sarc_pred = sarc_clf.predict(feats)[0]
        sarc_classes = list(sarc_clf.classes_)
        sarc_idx = sarc_classes.index("sarcastic") if "sarcastic" in sarc_classes else 1
        sarc_probs = sarc_clf.predict_proba(feats)[0]
        sarc_prob = float(sarc_probs[sarc_idx]) * 100.0

        # Multi-task predictions
        cont_pred = cont_clf.predict(feats)[0]
        risk_pred = risk_clf.predict(feats)[0]
        emo_pred = emo_clf.predict(feats)[0]

        return {
            "is_sarcastic": (sarc_pred == "sarcastic"),
            "sarcasm_prob": round(sarc_prob, 2),
            "content_type": cont_pred,
            "risk_level": risk_pred,
            "hybrid_emotion": emo_pred
        }
    except Exception as e:
        print(f"ML inference error: {e}")
        return {}

def detect_sarcasm(text: str, deberta_context: dict = None, translation: str = ""):
    """
    High-precision multi-tier sarcasm evaluator combining:
    1. Newly Trained ML Multi-Task Classifier (Trained on 500-sample dataset)
    2. Direct Idiom & Rhetorical Pattern Matching across original & translated text
    3. Semantic Contrast & Irony Collision Analysis (Praise + Catastrophe)
    4. Microsoft DeBERTa-v3 Natural Language Inference
    """
    if not text or not text.strip():
        return "Not Sarcastic", 15.0

    t_combined = f"{text} {translation}".lower()

    # 1. Trained ML Model Prediction
    ml_res = predict_trained_ml(text)
    if not ml_res and translation:
        ml_res = predict_trained_ml(translation)
    ml_is_sarcastic = ml_res.get("is_sarcastic", False)
    ml_sarc_prob = ml_res.get("sarcasm_prob", 0.0)

    # 2. Regex Pattern Matching across original & translated text
    pattern_matched = any(re.search(pattern, t_combined, re.IGNORECASE) for pattern in SARCASM_IDIOM_PATTERNS)

    # 3. Semantic Contrast Detection (Praise vs Catastrophe)
    contrast_detected = check_semantic_contrast(text, translation)

    # 4. DeBERTa NLI Semantic Context
    if deberta_context is None:
        deberta_context = analyze_deberta_sentiment_and_sarcasm(text)

    is_nli_sarcastic = (
        deberta_context.get("is_sarcastic", False) or
        deberta_context.get("is_sarcastic_tone", False) or
        "mockery" in str(deberta_context.get("emotion", "")).lower() or
        "irony" in str(deberta_context.get("emotion", "")).lower() or
        "sarcastic" in str(deberta_context.get("emotion", "")).lower()
    )
    deberta_sarcasm_score = (
        deberta_context.get("sarcasm_score", 0.0) or
        deberta_context.get("sarcasm_confidence", 0.0) or
        deberta_context.get("confidence", 0.0)
    )

    # Decision Matrix with High Precision Fusion
    if contrast_detected and (pattern_matched or ml_is_sarcastic or is_nli_sarcastic):
        return "Sarcastic", 98.50
    elif ml_is_sarcastic and ml_sarc_prob >= 50.0:
        return "Sarcastic", round(max(ml_sarc_prob, 95.0), 2)
    elif pattern_matched:
        return "Sarcastic", round(max(deberta_sarcasm_score, ml_sarc_prob, 94.0), 2)
    elif contrast_detected:
        return "Sarcastic", round(max(deberta_sarcasm_score, ml_sarc_prob, 94.0), 2)
    elif is_nli_sarcastic and deberta_sarcasm_score >= 75.0 and (ml_sarc_prob >= 35.0 or contrast_detected):
        return "Sarcastic", round(deberta_sarcasm_score, 2)
    else:
        # For Not Sarcastic, confidence represents certainty of authentic/literal communication
        not_sarc_conf = round(max(78.0, 100.0 - max(deberta_sarcasm_score, ml_sarc_prob)), 1)
        return "Not Sarcastic", min(98.5, not_sarc_conf)