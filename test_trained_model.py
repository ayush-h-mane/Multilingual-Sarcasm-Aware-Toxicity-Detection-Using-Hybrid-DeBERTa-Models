# =====================================================
# test_trained_model.py
# Verification Test Suite for the Newly Trained Model
# =====================================================
from sarcasm_detector import detect_sarcasm, predict_trained_ml
from models.fusion_engine import fusion
from models.deberta_engine import deberta_emotion

TEST_CASES = [
    {
        "name": "English Sarcasm (Birthday Irony)",
        "text": "I'm really happy you remembered my birthday after forgetting it for three years.",
        "expected_sarcasm": "Sarcastic"
    },
    {
        "name": "Kanglish Sarcasm (Database Delete)",
        "text": "Wow maga, database delete maadi great job anta helthiya?",
        "expected_sarcasm": "Sarcastic"
    },
    {
        "name": "Tanglish Sarcasm (Project Delete)",
        "text": "Project-a delete pannitu, super job nu sollariya? Amazing!",
        "expected_sarcasm": "Sarcastic"
    },
    {
        "name": "Hinglish Sarcasm (Server Crash)",
        "text": "Bhai, kya amazing work kiya hai, server crash kar diya!",
        "expected_sarcasm": "Sarcastic"
    },
    {
        "name": "Sincere Safe Praise (Team Project)",
        "text": "I am extremely happy that our team completed the project successfully.",
        "expected_sarcasm": "Not Sarcastic"
    },
    {
        "name": "Violent Threat",
        "text": "If you come near me again, I will seriously hurt you.",
        "expected_sarcasm": "Not Sarcastic",
        "expected_content": "threat"
    },
    {
        "name": "Toxic Abusive Comment",
        "text": "You are completely useless and nobody wants you on this team.",
        "expected_sarcasm": "Not Sarcastic",
        "expected_content": "toxic"
    }
]

def run_tests():
    print("=" * 70)
    print("🧪 SENTINELMIND AI - TRAINED MODEL VERIFICATION TEST SUITE")
    print("=" * 70)
    
    passed = 0
    total = len(TEST_CASES)

    for idx, case in enumerate(TEST_CASES, 1):
        text = case["text"]
        ml_pred = predict_trained_ml(text)
        deberta = deberta_emotion(text)
        sarcasm, score = detect_sarcasm(text, deberta)
        fused = fusion("Neutral", deberta, sarcasm_status=sarcasm, content=text, ml_prediction=ml_pred)

        sarcasm_pass = (sarcasm == case["expected_sarcasm"])
        content_pass = True
        if "expected_content" in case:
            content_pass = (ml_pred.get("content_type") == case["expected_content"])

        is_success = sarcasm_pass and content_pass
        if is_success:
            passed += 1

        status = "✅ PASS" if is_success else "❌ FAIL"
        print(f"\n[Test #{idx}] {case['name']} -> {status}")
        print(f"   Input: \"{text}\"")
        print(f"   Sarcasm Verdict: {sarcasm} (Score: {score}%)")
        print(f"   ML Content Type: {ml_pred.get('content_type')}")
        print(f"   ML Hybrid Emotion: {ml_pred.get('hybrid_emotion')}")
        print(f"   Fused System Emotion: {fused.get('emotion')}")

    print("\n" + "=" * 70)
    print(f"📊 Results: {passed}/{total} Tests Passed ({(passed/total)*100:.1f}% Accuracy)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
