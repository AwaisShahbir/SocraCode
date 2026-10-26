import pytest
from app.categories import BugCategory
from app.ml.classifier import classify_bug, MLClassifierService


def test_classifier_loaded():
    service = MLClassifierService()
    assert service.is_loaded is True
    assert service.model is not None


def test_classifier_prediction():
    code = "for i in range(10)\n    print(i)"
    category, confidence, is_low_conf = classify_bug(code, "SyntaxError", "expected ':'")
    assert isinstance(category, BugCategory)
    assert 0.0 <= confidence <= 1.0


def test_classifier_confidence_threshold_fallback():
    service = MLClassifierService(confidence_threshold=0.9999)
    category, confidence, is_low_conf = service.predict("x = 1", "", "")
    # High threshold triggers low confidence fallback
    assert is_low_conf is True
