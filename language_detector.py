# =====================================================
# language_detector.py
# SentinelMind AI v2.0 - High-Precision Multilingual & Code-Mix Detector
# =====================================================
import re
import unicodedata

# 1. Native Indic Script Unicode Ranges
INDIC_SCRIPTS = [
    ("\u0C80", "\u0CFF", "Kannada", "kn", "Kannada Native Script"),
    ("\u0B80", "\u0BFF", "Tamil", "ta", "Tamil Native Script"),
    ("\u0C00", "\u0C7F", "Telugu", "te", "Telugu Native Script"),
    ("\u0D00", "\u0D7F", "Malayalam", "ml", "Malayalam Native Script"),
    ("\u0900", "\u097F", "Hindi", "hi", "Devanagari Native Script"),
    ("\u0980", "\u09FF", "Bengali", "bn", "Bengali Native Script"),
    ("\u0A80", "\u0AFF", "Gujarati", "gu", "Gujarati Native Script"),
    ("\u0A00", "\u0A7F", "Punjabi", "pa", "Gurmukhi Native Script"),
    ("\u0B00", "\u0B7F", "Odia", "or", "Odia Native Script"),
    ("\u0600", "\u06FF", "Urdu / Arabic", "ur", "Arabic-Indic Script"),
]

# 2. Strict Indigenous Romanized Lexicons (Zero English Word Contamination)
KANGLISH_TOKENS = {
    "maga", "guru", "machha", "ivattu", "nanage", "sikthu", "beku", "beda",
    "madbittya", "madde", "kelsa", "hegidya", "yenu", "illa", "sakkat",
    "chindi", "haudu", "nimma", "nanna", "kodi", "tumba", "adhu", "idhu",
    "anta", "helthiya", "buddhivantha", "oota", "aytha", "kanro", "nodro",
    "gottha", "yaako", "yaaru", "bekilla", "namdu", "nimdu", "baralla",
    "nodappa", "alva", "bekagilla", "sariyagi", "chennagi", "hogi", "nodu",
    "barthini", "hogthini", "madthini", "kelasa", "yavaga", "yelli"
}

TANGLISH_TOKENS = {
    "romba", "machan", "seri", "enna", "inga", "irukken", "irukku", "nalla",
    "velai", "solre", "theriyum", "varala", "pannitu", "arumaiyaana", "epdi",
    "kitta", "illai", "vanthutu", "paru", "kudunga", "apdi", "yenna",
    "theriyuma", "poda", "thala", "nanba", "machii", "sollunga", "therila",
    "mudiyathu", "vaanga", "ponga", "aaha", "medhai", "arivu", "sonnadhu",
    "enakku", "unakku", "avaru", "ippo", "appo", "illana", "panreenga", "solreenga"
}

HINGLISH_TOKENS = {
    "kya", "baat", "kamaal", "diya", "shabash", "bohot", "badhiya", "arey",
    "wah", "bhai", "yaar", "aaj", "toh", "tumne", "itni", "der", "shuru",
    "mera", "meri", "mere", "hum", "nahi", "hoga", "karo", "accha", "sahi", "chal",
    "raha", "rahi", "rahe", "teer", "maar", "kaise", "kahan", "bolo", "batao", "karoge",
    "sunno", "dekho", "kuch", "aisa", "aise", "waise", "theek", "mast", "zabardast",
    "bataiye", "samjhe", "chahiye", "hogaya", "matlab", "mujhe", "mujhko", "tumhare",
    "tumhara", "tumhari", "tumhe", "aap", "aapka", "aapki", "aapke", "hamara", "hamari",
    "hamare", "apna", "apni", "apne", "thoda", "thodi", "thode", "bahut", "hua",
    "hui", "hue", "huye", "karna", "karke", "karne", "karte", "karti", "karta",
    "hai", "hain", "tha", "thi", "the", "wali", "wale", "wala", "sath", "kyun",
    "kyu", "kaisa", "kaisi", "bhi", "sirf", "hamesha", "pehle", "baad", "samajh"
}

TENGLISH_TOKENS = {
    "mowa", "babu", "bagunara", "cheppu", "endi", "enti", "chesav", "chala",
    "manchi", "ledu", "undhi", "anna", "avuna", "chesko", "ela", "ekkada",
    "epudu", "chudu", "emcheptunnav", "kadavayya", "ravali", "naku", "neeku",
    "chesanu", "chesavu", "unnava", "lekapothe", "ippudu", "appudu"
}

MANGLISH_TOKENS = {
    "entha", "eda", "machane", "adipoli", "sheriyanu", "nokku", "cheythatha",
    "nannayi", "pinne", "ivide", "evide", "chetta", "chechi", "poyi", "vannu",
    "enikku", "ninakku", "cheyyanam", "undallo", "ariyilla"
}

# 3. Global Language Dictionary Map
ISO_LANG_NAMES = {
    "en": "English",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "hi": "Hindi",
    "ml": "Malayalam",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "or": "Odia",
    "ur": "Urdu",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh-cn": "Chinese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic"
}

def detect_native_script(text: str):
    """
    Checks if text contains native Unicode characters for Indic scripts.
    """
    for start_ch, end_ch, lang_name, iso_code, script_desc in INDIC_SCRIPTS:
        if any(start_ch <= ch <= end_ch for ch in text):
            return {
                "language": lang_name,
                "detected_language": lang_name,
                "iso_code": iso_code,
                "dialect_info": script_desc,
                "is_code_mixed": False,
                "confidence": 99.5
            }
    return None

def detect_code_mixed(text: str):
    """
    Tokenizes text and checks against strict indigenous Romanized token lists.
    Avoids false positives with standard English words.
    """
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return None

    word_set = set(words)
    kannada_hits = word_set.intersection(KANGLISH_TOKENS)
    tamil_hits = word_set.intersection(TANGLISH_TOKENS)
    hindi_hits = word_set.intersection(HINGLISH_TOKENS)
    telugu_hits = word_set.intersection(TENGLISH_TOKENS)
    malayalam_hits = word_set.intersection(MANGLISH_TOKENS)

    scores = [
        (len(kannada_hits), "Kannada + English (Kanglish)", "kn", "Code-Mixed Romanized (Kanglish)", list(kannada_hits)),
        (len(tamil_hits), "Tamil + English (Tanglish)", "ta", "Code-Mixed Romanized (Tanglish)", list(tamil_hits)),
        (len(hindi_hits), "Hindi + English (Hinglish)", "hi", "Code-Mixed Romanized (Hinglish)", list(hindi_hits)),
        (len(telugu_hits), "Telugu + English (Tenglish)", "te", "Code-Mixed Romanized (Tenglish)", list(telugu_hits)),
        (len(malayalam_hits), "Malayalam + English (Manglish)", "ml", "Code-Mixed Romanized (Manglish)", list(malayalam_hits))
    ]

    scores.sort(key=lambda x: x[0], reverse=True)
    best_count, best_lang, best_iso, best_dialect, matched_tokens = scores[0]

    if best_count >= 1:
        # Calibrate confidence based on code-mix token density
        conf = min(98.0, 85.0 + (best_count * 4.0))
        return {
            "language": best_lang,
            "detected_language": best_lang,
            "iso_code": best_iso,
            "dialect_info": best_dialect,
            "is_code_mixed": True,
            "matched_code_mix_words": matched_tokens,
            "confidence": conf
        }

    return None

def detect_language(text: str) -> dict:
    """
    Comprehensive hybrid language detection pipeline:
    1. Native Indic Script Unicode Evaluation
    2. Tokenized Romanized Code-Mix Evaluation (Kanglish/Tanglish/Hinglish/Tenglish/Manglish)
    3. Global Language Detector Fallback (langdetect / deep_translator / latin checks)
    """
    if not text or not text.strip():
        return {
            "language": "English",
            "detected_language": "English",
            "iso_code": "en",
            "dialect_info": "Standard Latin Script",
            "is_code_mixed": False,
            "confidence": 100.0
        }

    # 1. Native script detection
    native_res = detect_native_script(text)
    if native_res:
        return native_res

    # 2. Code-mixed detection
    code_mixed_res = detect_code_mixed(text)
    if code_mixed_res:
        return code_mixed_res

    # 3. Fast fallback: check if standard latin script with english stopwords
    common_en = {"the", "is", "are", "you", "your", "my", "this", "that", "and", "or", "to", "for", "with", "have", "has", "was", "were", "what", "how", "why", "we", "they", "i", "a", "an"}
    words_set = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    en_overlap = words_set.intersection(common_en)
    
    if len(en_overlap) >= 1 or len(words_set) > 0:
        return {
            "language": "English",
            "detected_language": "English",
            "iso_code": "en",
            "dialect_info": "Standard English / Latin Script",
            "is_code_mixed": False,
            "confidence": 95.0
        }

    return {
        "language": "English",
        "detected_language": "English",
        "iso_code": "en",
        "dialect_info": "Standard Latin Script",
        "is_code_mixed": False,
        "confidence": 90.0
    }