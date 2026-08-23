from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "microsoft/deberta-v3-base"

print("Downloading Microsoft DeBERTa v3 Base...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

tokenizer.save_pretrained("models/microsoft_deberta")
model.save_pretrained("models/microsoft_deberta")

print("Download Complete!")