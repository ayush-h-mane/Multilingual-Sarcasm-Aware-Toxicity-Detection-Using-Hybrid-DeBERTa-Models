# =====================================================
# models/fusion_engine.py
# SentinelMind AI v2.0 - Hybrid Decision Fusion Engine
# =====================================================

POSITIVE_MASK_EMOTIONS = {
    "admiration", "joy", "approval", "pride", "optimism", "excitement", "gratitude", "positive", "love", "caring"
}

THREAT_TERMS = {
    "shoot", "attack", "bomb", "kill", "weapons", "weapon", "murder", "harm", "destroy", "gun", "blast", "threat"
}

def fusion(rule_emotion: str, deberta_result: dict, sarcasm_status: str = "Not Sarcastic", content: str = "", ml_prediction: dict = None) -> dict:
    """
    Intelligently fuses:
    1. Trained ML Multi-Task Model (from 500-sample dataset)
    2. Deep DeBERTa-v3 Neural Transformer Inference
    3. Heuristic Rule Engine
    4. Sarcasm Tone Inversion & Threat Context
    """
    if not isinstance(deberta_result, dict):
        deberta_result = {"emotion": str(deberta_result), "confidence": 75.0}

    deberta_emotion_label = deberta_result.get("emotion", "Neutral")
    deberta_confidence = float(deberta_result.get("confidence", 75.0))
    is_sarcastic = (sarcasm_status == "Sarcastic") or deberta_result.get("is_sarcastic_tone", False)
    semantic_tone = deberta_result.get("semantic_tone", "")
    
    t_lower = content.lower() if content else ""
    is_threat = any(term in t_lower for term in THREAT_TERMS) or (ml_prediction and ml_prediction.get("content_type") == "threat")
    is_toxic = (ml_prediction and ml_prediction.get("content_type") == "toxic")

    # Extract ML emotion if available
    ml_emotion = ml_prediction.get("hybrid_emotion", "") if ml_prediction else ""

    # 1. Threat & Violent Hazard Priority
    if is_threat and not is_sarcastic:
        final_emotion = "Threatening Hostility / Aggression"
        confidence = 98.5
        polarity = "Negative"

    # 2. Toxic Abuse Priority
    elif is_toxic and not is_sarcastic:
        final_emotion = "Toxic / Abusive Hostility"
        confidence = 95.0
        polarity = "Negative"

    # 3. Sarcasm Tone Inversion (e.g. False Praise -> Mockery)
    elif is_sarcastic:
        if ml_emotion and "_" in ml_emotion:
            parts = [p.capitalize() for p in ml_emotion.split("_")]
            final_emotion = f"{' / '.join(parts)} (Sarcastic Mockery)"
            confidence = 96.0
            polarity = "Negative"
        elif any(p in deberta_emotion_label.lower() for p in POSITIVE_MASK_EMOTIONS) or rule_emotion.lower() in POSITIVE_MASK_EMOTIONS:
            final_emotion = "Mockery / Sarcastic Disapproval"
            confidence = max(deberta_confidence, 94.0)
            polarity = "Negative"
        else:
            final_emotion = deberta_emotion_label
            confidence = max(deberta_confidence, 88.0)
            polarity = "Negative"

    # 4. Sincere Positive / Love / Admiration Context
    elif any(p in deberta_emotion_label.lower() for p in POSITIVE_MASK_EMOTIONS) or rule_emotion.lower() in POSITIVE_MASK_EMOTIONS:
        final_emotion = deberta_emotion_label.capitalize() if deberta_confidence >= 50.0 else rule_emotion
        confidence = max(deberta_confidence, 92.0)
        polarity = "Positive"

    # 5. Trained ML Multi-Class Prediction
    elif ml_emotion and ml_prediction.get("content_type") != "sarcasm":
        if "_" in ml_emotion:
            parts = [p.capitalize() for p in ml_emotion.split("_")]
            final_emotion = " & ".join(parts)
        else:
            final_emotion = ml_emotion.capitalize()
        confidence = max(deberta_confidence, 90.0)
        polarity = "Positive" if any(p in ml_emotion for p in ["joy", "pride", "relief", "gratitude", "hope", "love"]) else "Negative"

    # 6. High-Confidence DeBERTa
    elif deberta_confidence >= 50.0:
        final_emotion = deberta_emotion_label
        confidence = deberta_confidence
        polarity = deberta_result.get("polarity", "Neutral")

    # 7. Fallback Heuristic
    elif rule_emotion != "Neutral":
        final_emotion = rule_emotion
        confidence = 75.0
        polarity = "Positive" if rule_emotion == "Positive" else "Negative"
    else:
        final_emotion = deberta_emotion_label
        confidence = deberta_confidence
        polarity = deberta_result.get("polarity", "Neutral")

    return {
        "emotion": final_emotion,
        "confidence": round(confidence, 2),
        "polarity": polarity,
        "semantic_tone": semantic_tone
    }