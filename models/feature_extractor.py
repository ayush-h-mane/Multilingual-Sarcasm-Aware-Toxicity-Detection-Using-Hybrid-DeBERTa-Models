# =====================================================
# models/feature_extractor.py
# Shared Feature Extractor for Model Serialization
# =====================================================
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class LinguisticAndContrastExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.positive_praise = [
            "super job", "great job", "good job", "nice job", "brilliant idea", "genius",
            "masterpiece", "amazing work", "wonderful", "outstanding", "fantastic",
            "real genius", "brilliant", "perfectly fine", "super work", "kamaal", "champion",
            "delighted", "thrilled", "what a relief", "perfect timing", "so proud", "love waiting",
            "couldn't be happier", "excellent work", "safest decision", "super", "amazing"
        ]
        self.negative_destructive = [
            "delete", "deleted", "deleting", "destroy", "destroyed", "destroying",
            "broke", "broken", "breaking", "ruin", "ruined", "ruining", "wreck", "wrecked",
            "crash", "crashed", "crashing", "fail", "failed", "failing", "failure",
            "loss", "lost", "corrupted", "corrupt", "disappeared", "forgot", "forgetting",
            "stopped working", "delayed", "delay", "miss", "missed", "broke production",
            "shoot", "attack", "bomb", "kill", "weapons", "threaten", "hurt", "harm",
            "useless", "abusive", "toxic", "worthless", "harassing", "offensive", "insulting", "hate"
        ]
        self.dravidian_markers = [
            "maga", "guru", "chennagittu", "madbittya", "madtidya", "madidru", "helthiya",
            "avanu", "ivattu", "enakku", "romba", "arumaiyaana", "velai", "sollariya",
            "aayiduchu", "bhai", "kya", "kar diya", "karte hain", "bahut", "khushi", "aana"
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            t = str(text).lower()
            
            praise_count = sum(1 for phrase in self.positive_praise if phrase in t)
            destructive_count = sum(1 for phrase in self.negative_destructive if phrase in t)
            contrast_collision = 1.0 if (praise_count > 0 and destructive_count > 0) else 0.0
            
            dravidian_count = sum(1 for token in self.dravidian_markers if token in t)
            
            exclamation_count = min(t.count("!"), 5)
            question_count = min(t.count("?"), 5)
            caps_ratio = sum(1 for c in str(text) if c.isupper()) / (len(str(text)) + 1e-5)
            char_len = len(t)
            word_count = len(t.split())
            
            features.append([
                float(praise_count),
                float(destructive_count),
                float(contrast_collision),
                float(dravidian_count),
                float(exclamation_count),
                float(question_count),
                float(caps_ratio),
                float(word_count),
                float(char_len)
            ])
        return np.array(features, dtype=np.float32)
