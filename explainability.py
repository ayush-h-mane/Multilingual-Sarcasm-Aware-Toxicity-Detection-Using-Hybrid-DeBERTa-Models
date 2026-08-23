# =====================================================
# explainability.py
# SentinelMind AI v2.0 - Semantic Contrast & Explainability Engine
# =====================================================
import re

POSITIVE_PRAISE_TERMS = [
    "super job", "great job", "good job", "nice job", "brilliant idea", "genius",
    "masterpiece", "amazing work", "wonderful", "outstanding", "fantastic",
    "real genius", "brilliant", "perfectly fine", "super work", "kamaal", "champion",
    "delighted", "thrilled", "what a relief", "perfect timing", "so proud", "love waiting",
    "couldn't be happier", "excellent work", "safest decision", "super", "amazing",
    "great", "wow", "arumaiyaana", "sakkat", "chindi", "shabash", "bohot badhiya"
]

NEGATIVE_DESTRUCTIVE_TERMS = [
    "delete", "deleted", "deleting", "destroy", "destroyed", "destroying",
    "broke", "broken", "breaking", "ruin", "ruined", "ruining", "wreck", "wrecked",
    "crash", "crashed", "crashing", "fail", "failed", "failing", "failure",
    "loss", "lost", "corrupted", "corrupt", "disappeared", "forgot", "forgetting",
    "stopped working", "delayed", "delay", "miss", "missed", "broke production", "killed",
    "waste", "wasted", "mess", "screwed", "damage", "damaged", "disaster", "terrible",
    "late", "worst", "pain", "horrible"
]

def find_matched_terms(text: str, lexicon: list) -> list:
    """Finds multi-word and single-word phrases matching a lexicon."""
    t = text.lower()
    matched = []
    for term in lexicon:
        if re.search(r'\b' + re.escape(term) + r'\b', t):
            matched.append(term)
    return matched

def generate_intelligence_summary(
    text: str,
    sarcasm: str = "Not Sarcastic",
    emotion: str = "Neutral",
    risk: str = "LOW",
    language: str = "English",
    dialect: str = "Standard Latin Script",
    confidence: float = 90.0,
    harm_data: dict = None,
    ml_pred: dict = None
) -> dict:
    """
    Generates a rich, dynamic multi-tiered explainability and intelligence report:
    1. Executive Intelligence Summary (Multi-sentence contextual narrative)
    2. Semantic Contrast Rationale (Highlighting positive vs negative collision)
    3. Emotion Inversion Note (Surface vs Latent Polarity)
    4. Key Linguistic Cues
    5. Actionable Guidance
    """
    is_sarcastic = (sarcasm == "Sarcastic")
    praise_terms = find_matched_terms(text, POSITIVE_PRAISE_TERMS)
    destructive_terms = find_matched_terms(text, NEGATIVE_DESTRUCTIVE_TERMS)
    
    flagged_tokens = harm_data.get("flagged_tokens", []) if harm_data else []
    illegal = harm_data.get("illegal_activity", False) if harm_data else False
    moderation_action = harm_data.get("moderation_action", "APPROVED") if harm_data else "APPROVED"

    linguistic_cues = []
    if is_sarcastic:
        linguistic_cues.append("Ironic Tone Inversion")
    if praise_terms and destructive_terms:
        linguistic_cues.append(f"Semantic Contrast Collision ({', '.join(praise_terms[:2])} vs {', '.join(destructive_terms[:2])})")
    elif praise_terms:
        linguistic_cues.append(f"Hyperbolic Acclaim ({', '.join(praise_terms[:2])})")
    if dialect and "Code-Mixed" in dialect:
        linguistic_cues.append(f"{dialect} Ingestion")
    if illegal or risk == "CRITICAL":
        linguistic_cues.append("Physical Violence / Threat Markers")
    if harm_data and harm_data.get("profanity_score", 0) > 0:
        linguistic_cues.append("Vulgarity / Expletive Anchors")

    # Construct Dynamic Narrative Summary
    paragraphs = []
    
    if illegal or risk == "CRITICAL":
        summary_title = "CRITICAL THREAT & SECURITY HAZARD"
        p1 = f"CRITICAL SECURITY ALERT: High-severity hazardous intent identified matching physical violence or illegal endangerment in the linguistic stream (Confidence: {confidence}%)."
        p2 = f"Input ingested in {language} ({dialect}). Unlawful aggression cues detected ({', '.join(flagged_tokens) if flagged_tokens else 'Violent threat markers'}). Immediate moderation escalation ({moderation_action}) required."
        contrast_rationale = "Non-literal contrast overridden by direct, overt threat indicators requiring immediate containment."
        emotion_inversion = f"Negative aggressive polarity detected. Surface emotion: {emotion}."
        guidance = "Block communication, alert moderation queue, and flag associated user ID for security compliance."
    
    elif risk == "HIGH":
        summary_title = "HIGH HOSTILITY & ABUSIVE TOXICITY"
        p1 = f"HIGH-RISK HOSTILITY: Toxic, abusive, or hostile language detected in {language} communication (Confidence: {confidence}%)."
        p2 = f"Sentiment evaluation indicates severe negative hostility overriding standard conversational norms. Flagged markers: {', '.join(flagged_tokens) if flagged_tokens else 'Aggressive polarity'}."
        contrast_rationale = "Overt hostility and abusive vernacular detected without positive mitigating context."
        emotion_inversion = f"Hostile negative polarity. Dominant emotional state: {emotion}."
        guidance = "Filter vulgarities, restrict visibility, and issue standard community guidelines warning."
    
    elif is_sarcastic:
        summary_title = "SARCASTIC TONE INVERSION DETECTED"
        p1 = f"SARCASTIC TONE INVERSION: The input presents overt positive or superficial praise phrases that conflict with underlying negative/catastrophic realities (Confidence: {confidence}%)."
        if praise_terms and destructive_terms:
            p2 = f"Semantic Contrast Engine identified praise terms ({', '.join(praise_terms)}) paired directly against adverse outcomes ({', '.join(destructive_terms)}). Analyzed under {language} ({dialect})."
            contrast_rationale = f"Irony Collision: Overt praise ('{', '.join(praise_terms)}') is used to satirize a negative outcome ('{', '.join(destructive_terms)}')."
        else:
            p2 = f"Synthesized as ironic discourse where superficial acclaim conveys mocking criticism. Ingested under {language} ({dialect})."
            contrast_rationale = "Pragmatic irony detected through stylistic exaggeration and semantic incongruity."
        
        emotion_inversion = f"Surface literal praise is inverted to true latent intent: Mockery / Sarcastic Disapproval ({emotion})."
        guidance = "Treat message as ironic/satirical rather than literal compliment in customer feedback and sentiment reporting."
    
    elif any(pos in str(emotion).lower() for pos in ["love", "joy", "gratitude", "admiration", "pride", "optimism"]):
        summary_title = "AUTHENTIC POSITIVE EXPRESSION"
        p1 = f"AUTHENTIC POSITIVE COMMUNICATION: Sincere positive emotion ({emotion}) detected with authentic literal alignment (Confidence: {confidence}%)."
        p2 = f"Linguistic stream analyzed in {language} ({dialect}). No threat, hostility, or deceptive irony detected (Risk Level: {risk}, Moderation: {moderation_action})."
        contrast_rationale = "Literal positive semantics match authentic contextual sentiment with zero destructive contrast."
        emotion_inversion = f"Harmonious alignment: Positive surface semantics match genuine positive state ({emotion})."
        guidance = "Approved for standard processing with positive engagement routing."
    
    else:
        summary_title = "STANDARD LITERAL COMMUNICATION"
        p1 = f"STANDARD COMMUNICATION: Statement analyzed as authentic and non-sarcastic with neutral or context-aligned sentiment (Confidence: {confidence}%)."
        p2 = f"Linguistic markers confirm literal semantic integrity in {language} ({dialect}) with no safety violations detected."
        contrast_rationale = "Literal semantic interpretation confirmed without rhetorical inversion."
        emotion_inversion = f"Direct alignment: Statement expresses {emotion} polarity."
        guidance = "Safe for general publication and routine processing."

    paragraphs.append(p1)
    paragraphs.append(p2)
    full_summary = " ".join(paragraphs)

    return {
        "summary_title": summary_title,
        "summary": full_summary,
        "explanation": full_summary,
        "contrast_rationale": contrast_rationale,
        "emotion_inversion_note": emotion_inversion,
        "linguistic_cues": linguistic_cues,
        "praise_anchors": praise_terms,
        "destructive_anchors": destructive_terms,
        "actionable_guidance": guidance
    }
