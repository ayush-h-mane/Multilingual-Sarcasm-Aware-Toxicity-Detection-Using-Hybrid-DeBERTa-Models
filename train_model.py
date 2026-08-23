# =====================================================================
# train_model.py
# SentinelMind AI v2.0 - Multi-Task Sarcasm, Risk & Emotion Training Pipeline
# =====================================================================
import os
import json
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MaxAbsScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support
)

warnings.filterwarnings("ignore")

from models.feature_extractor import LinguisticAndContrastExtractor

def train_sentinel_model(dataset_path: str = "data/training_dataset.csv"):
    print("=" * 70)
    print("🚀 SENTINELMIND AI v2.0 - ML MODEL TRAINING PIPELINE")
    print("=" * 70)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"📊 Loaded Dataset: {len(df)} samples across {df.shape[1]} features.")
    print(f"   Target Distributions:")
    print(f"   - Sarcasm: {dict(df['sarcasm'].value_counts())}")
    print(f"   - Content Type: {dict(df['content_type'].value_counts())}")
    print(f"   - Risk Level: {dict(df['risk_level'].value_counts())}")
    print(f"   - Hybrid Emotion: {len(df['hybrid_emotion'].unique())} unique classes")

    X = df["text"].values
    y_sarcasm = df["sarcasm"].values
    y_content = df["content_type"].values
    y_risk = df["risk_level"].values
    y_emotion = df["hybrid_emotion"].values

    # Train/Test Split (80% Train, 20% Test stratified by sarcasm)
    X_train, X_test, y_sarc_train, y_sarc_test, y_cont_train, y_cont_test, y_risk_train, y_risk_test, y_emo_train, y_emo_test = train_test_split(
        X, y_sarcasm, y_content, y_risk, y_emotion, test_size=0.20, random_state=42, stratify=y_sarcasm
    )

    print(f"\n📂 Train Samples: {len(X_train)} | Test Samples: {len(X_test)}")

    # 2. Multi-Tier Feature Union & Scaler
    print("\n⚙️ Building Feature Representation Pipeline...")
    raw_feature_union = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=3000,
            sublinear_tf=True,
            strip_accents="unicode"
        )),
        ("char_tfidf", TfidfVectorizer(
            ngram_range=(3, 5),
            analyzer="char_wb",
            max_features=3000,
            sublinear_tf=True
        )),
        ("linguistic", LinguisticAndContrastExtractor())
    ])

    feature_pipeline = Pipeline([
        ("union", raw_feature_union),
        ("scaler", MaxAbsScaler())
    ])

    # Fit feature extractor on training data
    X_train_features = feature_pipeline.fit_transform(X_train)
    X_test_features = feature_pipeline.transform(X_test)
    print(f"   ✓ Feature Vector Dimensions: {X_train_features.shape[1]} normalized features.")

    # 3. Model 1: Sarcasm Classifier
    print("\n🎯 Training Task 1: Sarcasm Classification (Calibrated Logistic Classifier)...")
    sarcasm_clf = LogisticRegression(C=3.0, max_iter=500, solver="lbfgs", random_state=42)
    sarcasm_clf.fit(X_train_features, y_sarc_train)
    y_sarc_pred = sarcasm_clf.predict(X_test_features)
    sarc_acc = accuracy_score(y_sarc_test, y_sarc_pred)
    print(f"   ✓ Sarcasm Test Accuracy: {sarc_acc * 100:.2f}%")
    print(classification_report(y_sarc_test, y_sarc_pred, digits=4))

    # 4. Model 2: Content Type Classifier (sarcasm, safe, threat, toxic)
    print("\n🎯 Training Task 2: Content Type Multi-Class Classification...")
    content_clf = LogisticRegression(C=3.0, max_iter=500, class_weight="balanced", solver="lbfgs", random_state=42)
    content_clf.fit(X_train_features, y_cont_train)
    y_cont_pred = content_clf.predict(X_test_features)
    cont_acc = accuracy_score(y_cont_test, y_cont_pred)
    print(f"   ✓ Content Type Test Accuracy: {cont_acc * 100:.2f}%")
    print(classification_report(y_cont_test, y_cont_pred, digits=4))

    # 5. Model 3: Risk Level Classifier (low, medium, high, critical)
    print("\n🎯 Training Task 3: Threat Risk Level Classifier...")
    risk_clf = LogisticRegression(C=3.0, max_iter=500, class_weight="balanced", solver="lbfgs", random_state=42)
    risk_clf.fit(X_train_features, y_risk_train)
    y_risk_pred = risk_clf.predict(X_test_features)
    risk_acc = accuracy_score(y_risk_test, y_risk_pred)
    print(f"   ✓ Risk Level Test Accuracy: {risk_acc * 100:.2f}%")
    print(classification_report(y_risk_test, y_risk_pred, digits=4))

    # 6. Model 4: Hybrid Emotion Classifier
    print("\n🎯 Training Task 4: Fine-Grained Hybrid Emotion Synthesizer...")
    emotion_clf = LogisticRegression(C=2.0, max_iter=500, solver="lbfgs", random_state=42)
    emotion_clf.fit(X_train_features, y_emo_train)
    y_emo_pred = emotion_clf.predict(X_test_features)
    emo_acc = accuracy_score(y_emo_test, y_emo_pred)
    print(f"   ✓ Hybrid Emotion Test Accuracy: {emo_acc * 100:.2f}%")

    # 7. Perform 5-Fold Stratified Cross-Validation for Sarcasm
    print("\n🔬 Performing 5-Fold Stratified Cross-Validation on Full Dataset...")
    full_features = feature_pipeline.fit_transform(X)
    cv_scores = cross_val_score(sarcasm_clf, full_features, y_sarcasm, cv=5, scoring="accuracy")
    print(f"   ✓ 5-Fold CV Scores: {[round(s, 4) for s in cv_scores]}")
    print(f"   ✓ Mean CV Accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")

    # Retrain on full dataset for maximum production power
    sarcasm_clf.fit(full_features, y_sarcasm)
    content_clf.fit(full_features, y_content)
    risk_clf.fit(full_features, y_risk)
    emotion_clf.fit(full_features, y_emotion)

    # 8. Package & Save the Pipeline Bundle
    os.makedirs("models", exist_ok=True)
    bundle = {
        "feature_pipeline": feature_pipeline,
        "sarcasm_classifier": sarcasm_clf,
        "content_classifier": content_clf,
        "risk_classifier": risk_clf,
        "emotion_classifier": emotion_clf,
        "classes": {
            "sarcasm": list(sarcasm_clf.classes_),
            "content": list(content_clf.classes_),
            "risk": list(risk_clf.classes_),
            "emotion": list(emotion_clf.classes_)
        },
        "metrics": {
            "sarcasm_test_accuracy": float(sarc_acc),
            "content_test_accuracy": float(cont_acc),
            "risk_test_accuracy": float(risk_acc),
            "emotion_test_accuracy": float(emo_acc),
            "cv_mean_accuracy": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std())
        }
    }
    model_save_path = "models/trained_sarcasm_pipeline.joblib"
    joblib.dump(bundle, model_save_path)
    print(f"\n💾 Production Model Pipeline successfully saved to: {model_save_path}")

    # 9. Save metrics report JSON
    report_save_path = "models/training_report.json"
    with open(report_save_path, "w") as f:
        json.dump(bundle["metrics"], f, indent=2)
    print(f"📄 Training Report saved to: {report_save_path}")

    print("\n" + "=" * 70)
    print("✅ MODEL TRAINING COMPLETE & SAVED!")
    print("=" * 70)
    return bundle

if __name__ == "__main__":
    train_sentinel_model()
