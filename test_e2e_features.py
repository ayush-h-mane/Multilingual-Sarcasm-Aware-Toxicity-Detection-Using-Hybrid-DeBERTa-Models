import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

test_cases = [
    ("English Sarcasm", "Oh wow, what a brilliant idea to delete the entire production database right before launch. You're a real genius!"),
    ("Kanglish Sarcasm", "Maga ivattu office alli nanage promotion sikthu, wow great amazing work!"),
    ("Tanglish Sarcasm", "Naan romba happy irukken, aana avar sonnadhu romba arumaiyaana velai, yeah right!"),
    ("Hinglish Sarcasm", "Arey wah! Aaj toh tumne kamaal hi kar diya, itni der se aakar party shuru ki!"),
    ("Violent Threat", "We are planning to shoot and attack the building tomorrow with weapons and bomb."),
    ("Profanity & Toxicity", "This bastard is talking shit and spreading fucking lies about our entire department!"),
    ("Kannada Native Script", "ನೀವು ನಿಜವಾಗಿಯೂ ತುಂಬಾ ಬುದ್ಧಿವಂತರು!")
]

all_passed = True

for label, text in test_cases:
    print(f"================ {label} ================")
    print(f"Input: \"{text}\"")
    res = client.post("/analyze", data={"text": text})
    if res.status_code != 200:
        print("FAILED with status", res.status_code, res.text)
        all_passed = False
        continue

    data = res.json()
    
    # 1. Language identification verification
    lang = data.get("language")
    dialect = data.get("dialect_info")
    print(f"1. Language Identified: {lang} (Dialect: {dialect})")
    assert lang is not None, "Language missing!"
    
    # 2. Model Confidence & Engine Breakdown verification
    eb = data.get("engine_breakdown", [])
    overall_conf = data.get("confidence")
    print(f"2. Calibrated Confidence: {overall_conf}% | Engine Breakdown ({len(eb)} engines):")
    for engine in eb:
        print(f"   * {engine['name']}: {engine['confidence']}% ({engine['verdict']})")
    assert len(eb) == 4, f"Expected 4 engines, got {len(eb)}"
    assert 0 <= overall_conf <= 100, f"Invalid confidence {overall_conf}"
    
    # 3. Dynamic Analysis Summary verification
    print(f"3. Summary Title: {data.get('summary_title')}")
    print(f"   Summary: {data.get('summary')}")
    print(f"   Contrast Rationale: {data.get('contrast_rationale')}")
    print(f"   Linguistic Cues: {data.get('linguistic_cues')}")
    assert data.get("summary"), "Summary missing!"
    
    # 4. Multilingual Cross-Translation Matrix verification
    tm = data.get("translation_matrix", [])
    gloss = data.get("code_mixed_glossary", {})
    print(f"4. Translation Matrix ({len(tm)} languages):")
    for t in tm:
        print(f"   * [{t['language']} - {t['native_name']}] {t['translation']}")
    print(f"   Code-Mix Glossary: {gloss}")
    assert len(tm) >= 5, f"Expected at least 5 matrix translations, got {len(tm)}"
    
    # 5. Harm Moderation & Content Guard verification
    harm = data.get("harm_moderation", {})
    mod_act = data.get("moderation_action")
    print(f"5. Harm Moderation: {harm}")
    print(f"   Action: {mod_act} | Status: {data.get('moderation_status')}")
    print(f"   Clean Text: {data.get('clean_text')}")
    assert mod_act in ["APPROVED", "FLAGGED FOR REVIEW", "BLOCKED / QUARANTINED"], f"Invalid action {mod_act}"
    print("-> ALL CHECKS PASSED FOR THIS TEST CASE\n")

print("=================================================")
if all_passed:
    print("ALL 7 TEST CASES COMPLETED SUCCESSFULLY!")
else:
    print("SOME TEST CASES FAILED!")
