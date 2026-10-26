import numpy as np
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from app.categories import BugCategory

CATEGORY_INDEX_MAP = {cat: idx for idx, cat in enumerate(BugCategory)}
INDEX_CATEGORY_MAP = {idx: cat for idx, cat in enumerate(BugCategory)}


class ScikitLearnBaseline:
    """Scikit-learn baseline classifier on the exact same dataset for evaluation comparison."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ScikitLearnBaseline":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


def evaluate_model_performance(
    y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "Model"
) -> Dict[str, object]:
    """Generates evaluation metrics: accuracy, precision, recall, and confusion matrix."""
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(BugCategory))))

    categories = [cat.value for cat in BugCategory]

    return {
        "model_name": model_name,
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(prec), 4),
        "macro_recall": round(float(rec), 4),
        "macro_f1": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "categories": categories,
    }
