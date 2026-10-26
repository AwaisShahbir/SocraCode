import os
import torch
import joblib
from typing import Optional, Tuple
from app.categories import BugCategory
from app.ml.features import CodeFeatureExtractor
from app.ml.model import BugClassifierNN
from app.ml.baseline import INDEX_CATEGORY_MAP

DEFAULT_MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_WEIGHTS_PATH = os.path.join(DEFAULT_MODEL_DIR, "model.pt")
VECTORIZER_PATH = os.path.join(DEFAULT_MODEL_DIR, "vectorizer.joblib")


class MLClassifierService:
    """Inference service for classifying bug categories with confidence scores."""

    def __init__(self, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold
        self.model: Optional[BugClassifierNN] = None
        self.feature_extractor: Optional[CodeFeatureExtractor] = None
        self.is_loaded = False
        self.load_if_available()

    def load_if_available(self) -> bool:
        if os.path.exists(MODEL_WEIGHTS_PATH) and os.path.exists(VECTORIZER_PATH):
            try:
                extractor: CodeFeatureExtractor = joblib.load(VECTORIZER_PATH)
                self.feature_extractor = extractor
                dummy_feat = extractor.extract_single("x = 1", "", "")
                input_dim = len(dummy_feat)

                model = BugClassifierNN(input_dim=input_dim, num_classes=len(BugCategory))
                model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=torch.device("cpu"), weights_only=True))
                model.eval()
                self.model = model
                self.is_loaded = True
                return True
            except Exception as e:
                self.is_loaded = False
                return False
        return False

    def predict(
        self, code: str, error_type: str, message: str
    ) -> Tuple[BugCategory, float, bool]:
        """
        Returns (predicted_category, confidence_score, is_low_confidence).
        If confidence < threshold, is_low_confidence is True (Constraint 8).
        """
        if not self.is_loaded or self.model is None or self.feature_extractor is None:
            # Fallback if model not yet trained
            return BugCategory.SYNTAX_ERROR, 0.5, True

        feat = self.feature_extractor.extract_single(code, error_type, message)
        tensor_feat = torch.tensor(feat, dtype=torch.float32).unsqueeze(0)

        class_idx, confidence = self.model.predict_with_confidence(tensor_feat)
        predicted_category = INDEX_CATEGORY_MAP.get(class_idx, BugCategory.SYNTAX_ERROR)

        is_low_confidence = confidence < self.confidence_threshold
        return predicted_category, confidence, is_low_confidence


_default_classifier = MLClassifierService()

def classify_bug(code: str, error_type: str, message: str) -> Tuple[BugCategory, float, bool]:
    return _default_classifier.predict(code, error_type, message)
