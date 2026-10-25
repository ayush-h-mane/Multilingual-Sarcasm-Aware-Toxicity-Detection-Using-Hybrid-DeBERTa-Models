# =====================================================
# models/deberta_engine.py
# SentinelMind AI v2.0 - High-Precision DeBERTa Engine
# =====================================================
import logging
from transformers import pipeline

logger = logging.getLogger("deberta_engine")

# -----------------------------------------------------
# 1. Pipeline Initializations
# -----------------------------------------------------
# Deep Natural Language Inference & Zero-Shot Semantic Engine (Microsoft DeBERTa-v3)
try:
    deberta_nli = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
    )
except Exception as e:
    logger.warning(f"Could not load DeBERTa-v3 NLI: {e}")
    deberta_nli = None

# Fine-grained 28-Emotion Multi-Class Neural Classifier
try:
    emotion_pipeline = pipeline(
        "text-classification",
        model="SamLowe/roberta-base-go_emotions",
        top_k=5
    )
except Exception as e:
    logger.warning(f"Could not load GoEmotions pipeline: {e}")
    emotion_pipeline = None

# Emotion polarity mappings for nuance resolution
POSITIVE_EMOTIONS = {
    "admiration", "amusement", "approval", "caring", "desire",
    "excitement", "gratitude", "joy", "love", "optimism", "pride", "relief"
}

NEGATIVE_EMOTIONS = {
    "anger", "annoyance", "disappointment", "disapproval", "disgust",
    "embarrassment", "fear", "grief", "nervousness", "remorse", "sadness"
}

AMBIGUOUS_EMOTIONS = {"confusion", "curiosity", "realization", "surprise"}


def analyze_deberta_sentiment_and_sarcasm(text: str):
    """
    Leverages DeBERTa-v3 Natural Language Inference to evaluate semantic tone,
    irony/sarcasm probability, and intent hypotheses.
    """
    if not deberta_nli or not text.strip():
        return {
            "is_sarcastic": False,
            "sarcasm_score": 0.0,
            "semantic_tone": "neutral",
            "polarity": "Neutral"
        }

    try:
        # Sarcasm / Irony Hypothesis Test
        sarcasm_candidates = [
            "sarcastic, mocking, or ironic statement",
            "sincere, authentic, or direct statement"
        ]
        sarc_res = deberta_nli(text[:512], candidate_labels=sarcasm_candidates, multi_label=False)
        top_label = sarc_res["labels"][0].lower()
        is_sarc_top = "sarcastic" in top_label
        if is_sarc_top:
            sarcasm_score = round(sarc_res["scores"][0] * 100, 2)
        else:
            sarcasm_score = round((1.0 - sarc_res["scores"][0]) * 100, 2)

        # Polarity Hypothesis Test
        polarity_candidates = ["positive tone", "negative tone", "neutral tone"]
        pol_res = deberta_nli(text[:512], candidate_labels=polarity_candidates, multi_label=False)
        top_polarity = pol_res["labels"][0].replace(" tone", "").capitalize()

        # Semantic Category Evaluation
        intent_candidates = [
            "praise and celebration",
            "anger, frustration, and hostility",
            "mockery, sarcasm, and criticism",
            "love, affection, and gratitude",
            "fear, panic, and threat",
            "sadness and grief",
            "neutral everyday information"
        ]
        intent_res = deberta_nli(text[:512], candidate_labels=intent_candidates, multi_label=False)
        top_intent = intent_res["labels"][0]

        is_sarcastic = is_sarc_top and sarcasm_score >= 70.0

        return {
            "is_sarcastic": is_sarcastic,
            "sarcasm_score": sarcasm_score,
            "semantic_tone": top_intent,
            "polarity": top_polarity
        }

    except Exception as e:
        logger.error(f"DeBERTa NLI error: {e}")
        return {
            "is_sarcastic": False,
            "sarcasm_score": 0.0,
            "semantic_tone": "neutral",
            "polarity": "Neutral"
        }


def deberta_emotion(text: str):
    """
    High-precision emotion & semantic analysis combining:
    1. Microsoft DeBERTa-v3 NLI context evaluation
    2. Deep multi-emotion distribution scoring
    3. Sarcasm-aware contextual emotion disambiguation
    """
    if not text or not text.strip():
        return {
            "emotion": "Neutral",
            "confidence": 0,
            "primary_emotion": "Neutral",
            "secondary_emotion": "None",
            "polarity": "Neutral",
            "emotion_scores": {},
            "is_sarcastic_tone": False
        }

    # 1. Neural Emotion Inference
    raw_emotions = []
    if emotion_pipeline:
        try:
            raw_emotions = emotion_pipeline(text[:512])[0]
        except Exception as e:
            logger.error(f"GoEmotions inference error: {e}")

    top_emotion = raw_emotions[0]["label"] if raw_emotions else "neutral"
    top_score = round(raw_emotions[0]["score"] * 100, 2) if raw_emotions else 50.0

    second_emotion = raw_emotions[1]["label"] if len(raw_emotions) > 1 else "none"
    second_score = round(raw_emotions[1]["score"] * 100, 2) if len(raw_emotions) > 1 else 0.0

    # Build emotion distribution dictionary
    emotion_scores = {
        item["label"]: round(item["score"] * 100, 2) for item in raw_emotions[:5]
    }

    # 2. DeBERTa-v3 Semantic & Sarcasm Context
    nli_data = analyze_deberta_sentiment_and_sarcasm(text)
    
    # Check contrast heuristics directly
    t_lower = text.lower()
    positive_terms = ["super job", "great job", "good job", "nice job", "brilliant idea", "genius", "masterpiece", "amazing work", "wonderful", "perfectly fine", "kamaal", "shabash", "bohot badhiya"]
    destructive_terms = ["delete", "deleted", "destroy", "destroyed", "broke", "broken", "ruin", "ruined", "crash", "crashed", "fail", "failed", "loss", "lost", "waste", "wasted", "damage"]
    has_contrast = any(p in t_lower for p in positive_terms) and any(d in t_lower for d in destructive_terms)
    
    # If text has clear negative emotions without praise, it is sincere negative, not sarcastic
    is_direct_negative = top_emotion in NEGATIVE_EMOTIONS and not any(p in t_lower for p in positive_terms)
    
    is_sarcastic = (nli_data["is_sarcastic"] or has_contrast) and not is_direct_negative
    polarity = nli_data["polarity"]

    # 3. Contextual Sarcasm Inversion & Precision Calibration
    final_emotion = top_emotion
    final_confidence = top_score

    if is_sarcastic and top_emotion in POSITIVE_EMOTIONS:
        # Resolve true latent sarcastic emotion
        final_emotion = "mockery / sarcastic disapproval"
        polarity = "Negative"
        final_confidence = max(nli_data["sarcasm_score"], top_score, 88.50)
    elif is_sarcastic and has_contrast:
        final_emotion = f"sarcastic {top_emotion}" if top_emotion != "neutral" else "mockery / irony"
        polarity = "Negative"
        final_confidence = max(nli_data["sarcasm_score"], 85.0)
    elif top_emotion in POSITIVE_EMOTIONS:
        polarity = "Positive"
    elif top_emotion in NEGATIVE_EMOTIONS:
        polarity = "Negative"

    return {
        "emotion": final_emotion,
        "confidence": final_confidence,
        "primary_emotion": final_emotion,
        "secondary_emotion": second_emotion,
        "polarity": polarity,
        "semantic_tone": nli_data["semantic_tone"],
        "is_sarcastic_tone": is_sarcastic,
        "sarcasm_confidence": nli_data["sarcasm_score"],
        "emotion_scores": emotion_scores
    }