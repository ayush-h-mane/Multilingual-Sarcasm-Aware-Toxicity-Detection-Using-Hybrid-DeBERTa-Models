# =====================================================
# toxicity_model.py
# SentinelMind AI v2.0 - Multilingual Harm Moderation & Content Guard
# =====================================================
import re

# 1. High-Hazard Threat & Violence Triggers (English + Code-Mixed Indic)
THREAT_KEYWORDS = {
    # English Threat & Violence
    "kill", "murder", "bomb", "blast", "attack", "shoot", "stab", "kidnap",
    "weapon", "weapons", "gun", "guns", "rifle", "explosive", "explosives",
    "grenade", "poison", "hijack", "hostage", "threaten", "execute",
    "massacre", "assassinate", "slaughter", "destroy", "annihilate", "hurt",
    "torture", "arson", "detonate",

    # Code-Mixed / Indic Threat Lexicon
    "kollu", "konna", "mar", "marna", "goli", "jaan", "uda", "khatam",
    "veppan", "kannu", "kuthu", "kolai", "vettu", "adi"
}

# 2. Severe Profanity & Vulgarity Lexicon (Multilingual & Code-Mixed)
PROFANITY_KEYWORDS = {
    # English Profanities
    "fuck", "fucking", "fucked", "fucker", "shit", "bitch", "bitches",
    "asshole", "assholes", "bastard", "bastards", "motherfucker", "cunt",
    "dick", "pussy", "bullshit", "dammit", "slut", "whore",

    # Indic Romanized / Code-Mixed Profanities
    "chutiya", "bhosdike", "madarchod", "behenchod", "harami", "kamina",
    "gandu", "saala", "kutta", "thevidiya", "badava", "bewarse", "boli"
}

# 3. Hate Speech & Identity Attack Triggers
HATE_SPEECH_KEYWORDS = {
    "nigger", "faggot", "retard", "terrorist", "subhuman", "filth", "scum",
    "die all", "wipe out", "inferior race"
}

# 4. Severe Harassment & Insult Triggers
HARASSMENT_KEYWORDS = {
    "useless", "worthless", "nobody wants you", "kill yourself", "loser",
    "pathetic", "disgusting pig", "get lost forever", "trash person"
}

def censor_text(text: str) -> str:
    """
    Sanitizes profanity and severe abusive tokens by replacing characters with asterisks.
    """
    if not text:
        return ""

    result = text
    all_censor_words = PROFANITY_KEYWORDS.union(HATE_SPEECH_KEYWORDS)

    for word in all_censor_words:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        def repl(match):
            found = match.group(0)
            return found[0] + ("*" * (len(found) - 1)) if len(found) > 2 else "*" * len(found)
        result = pattern.sub(repl, result)

    return result

def analyze_harm_and_moderation(text: str, ml_prediction: dict = None, emotion: str = "Neutral") -> dict:
    """
    Evaluates multi-category safety guardrails:
    - Toxicity Score
    - Threat & Violence Score
    - Profanity & Abuse Score
    - Hate Speech Score
    - Harassment Score
    - Overall Harm Severity Level (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
    - Moderation Action (APPROVED, FLAGGED FOR REVIEW, BLOCKED / QUARANTINED)
    """
    if not text or not text.strip():
        return {
            "is_harmful": False,
            "illegal_activity": False,
            "risk_level": "LOW",
            "moderation_action": "APPROVED",
            "moderation_status": "Content Approved • Safe Communication",
            "threat_score": 0.0,
            "toxicity_score": 0.0,
            "profanity_score": 0.0,
            "hate_speech_score": 0.0,
            "harassment_score": 0.0,
            "flagged_categories": [],
            "flagged_tokens": [],
            "clean_text": ""
        }

    t_lower = text.lower()
    words = set(re.findall(r'\b[a-zA-Z]+\b', t_lower))

    threat_matches = words.intersection(THREAT_KEYWORDS)
    profanity_matches = words.intersection(PROFANITY_KEYWORDS)
    hate_matches = words.intersection(HATE_SPEECH_KEYWORDS)
    harassment_matches = [h for h in HARASSMENT_KEYWORDS if h in t_lower]

    ml_content = ml_prediction.get("content_type", "safe") if ml_prediction else "safe"
    ml_risk = ml_prediction.get("risk_level", "low") if ml_prediction else "low"

    # Category Scoring
    threat_score = min(99.0, len(threat_matches) * 45.0 + (50.0 if ml_content == "threat" or ml_risk == "critical" else 0.0))
    profanity_score = min(99.0, len(profanity_matches) * 40.0)
    hate_score = min(99.0, len(hate_matches) * 55.0)
    harassment_score = min(99.0, len(harassment_matches) * 45.0 + (35.0 if ml_content == "toxic" or ml_risk == "high" else 0.0))
    
    # Toxicity aggregate (0.0 for clean safe text)
    if ml_content == "toxic":
        toxicity_score = 85.0
    elif "hostil" in emotion.lower() or "abus" in emotion.lower():
        toxicity_score = 65.0
    elif profanity_score > 0 or harassment_score > 0 or hate_score > 0:
        toxicity_score = max(profanity_score * 0.85, harassment_score, hate_score * 0.9)
    else:
        toxicity_score = 0.0

    # Flagged Categories
    flagged_categories = []
    flagged_tokens = list(threat_matches.union(profanity_matches).union(hate_matches))

    if threat_matches or ml_content == "threat" or threat_score >= 40.0:
        flagged_categories.append("Violent Threat & Physical Danger")
    if profanity_matches or profanity_score >= 30.0:
        flagged_categories.append("Vulgarity & Profane Language")
    if hate_matches or hate_score >= 30.0:
        flagged_categories.append("Hate Speech & Identity Attack")
    if harassment_matches or harassment_score >= 30.0 or ml_content == "toxic":
        flagged_categories.append("Hostile Harassment & Abuse")

    is_illegal = len(threat_matches) > 0 or ml_content == "threat" or threat_score >= 60.0

    # Risk Level & Moderation Action Determination
    if is_illegal or threat_score >= 60.0 or hate_score >= 60.0 or ml_risk == "critical":
        risk_level = "CRITICAL"
        moderation_action = "BLOCKED / QUARANTINED"
        moderation_status = "Critical Security Hazard • Automatic Quarantine Triggered"
    elif toxicity_score >= 60.0 or harassment_score >= 50.0 or profanity_score >= 60.0 or ml_risk == "high":
        risk_level = "HIGH"
        moderation_action = "FLAGGED FOR REVIEW"
        moderation_status = "Elevated Toxicity Flagged • Human Review Recommended"
    elif profanity_score > 0.0 or ml_risk == "medium":
        risk_level = "MEDIUM"
        moderation_action = "FLAGGED FOR REVIEW"
        moderation_status = "Mild Profanity / Sarcastic Irony Detected"
    else:
        risk_level = "LOW"
        moderation_action = "APPROVED"
        moderation_status = "Safe Content • Policy Verified"

    clean_text = censor_text(text)

    return {
        "is_harmful": risk_level in ["HIGH", "CRITICAL"],
        "illegal_activity": is_illegal,
        "risk_level": risk_level,
        "moderation_action": moderation_action,
        "moderation_status": moderation_status,
        "threat_score": round(threat_score, 1),
        "toxicity_score": round(toxicity_score, 1),
        "profanity_score": round(profanity_score, 1),
        "hate_speech_score": round(hate_score, 1),
        "harassment_score": round(harassment_score, 1),
        "flagged_categories": flagged_categories,
        "flagged_tokens": flagged_tokens,
        "clean_text": clean_text
    }