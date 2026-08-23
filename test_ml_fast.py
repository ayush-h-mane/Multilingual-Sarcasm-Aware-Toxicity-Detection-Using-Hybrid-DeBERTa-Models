# =====================================================
# test_ml_fast.py
# Fast Pure ML Model Evaluation on Test Set
# =====================================================
import pandas as pd
from sarcasm_detector import predict_trained_ml

df = pd.read_csv("data/training_dataset.csv")

# Select 15 diverse benchmark test cases
sample_indices = [0, 1, 5, 6, 10, 11, 21, 23, 29, 310, 311, 390, 391, 470, 480]

print("=" * 75)
print("🚀 BENCHMARKING TRAINED ML MODEL INFERENCE")
print("=" * 75)

correct_sarc = 0
correct_content = 0

for idx in sample_indices:
    row = df.iloc[idx]
    text = row["text"]
    expected_sarc = row["sarcasm"]
    expected_content = row["content_type"]
    
    pred = predict_trained_ml(text)
    pred_sarc = "sarcastic" if pred.get("is_sarcastic") else "not_sarcastic"
    pred_content = pred.get("content_type")
    
    sarc_ok = (pred_sarc == expected_sarc)
    cont_ok = (pred_content == expected_content)
    
    if sarc_ok: correct_sarc += 1
    if cont_ok: correct_content += 1
    
    print(f"Row {row['id']:3d} | Sarcasm: {'✅' if sarc_ok else '❌'} ({pred_sarc}) | Content: {'✅' if cont_ok else '❌'} ({pred_content:8s}) | Text: {text[:45]}...")

print("\n" + "=" * 75)
print(f"Sarcasm Accuracy:  {correct_sarc}/{len(sample_indices)} ({(correct_sarc/len(sample_indices))*100:.1f}%)")
print(f"Content Accuracy:  {correct_content}/{len(sample_indices)} ({(correct_content/len(sample_indices))*100:.1f}%)")
print("=" * 75)
