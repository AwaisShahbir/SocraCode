"""
SocraCode Model Training & Evaluation Pipeline (Step 3).
Trains a PyTorch neural network and a scikit-learn baseline from scratch
on our synthetic dataset. Compares metrics and saves weights to backend/app/ml/.
"""

import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import joblib

# Ensure backend is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.categories import BugCategory
    from app.ml.features import CodeFeatureExtractor
    from app.ml.model import BugClassifierNN
    from app.ml.baseline import (
        CATEGORY_INDEX_MAP,
        ScikitLearnBaseline,
        evaluate_model_performance,
    )
except ImportError:
    from backend.app.categories import BugCategory  # type: ignore
    from backend.app.ml.features import CodeFeatureExtractor  # type: ignore
    from backend.app.ml.model import BugClassifierNN  # type: ignore
    from backend.app.ml.baseline import (  # type: ignore
        CATEGORY_INDEX_MAP,
        ScikitLearnBaseline,
        evaluate_model_performance,
    )
from ml.scripts.generate_bugs import BugInjector


def build_synthetic_dataset(num_samples: int = 2400):
    """Generates synthetic dataset across all 8 categories."""
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    seed_codes = []
    if os.path.exists(raw_dir):
        for fname in os.listdir(raw_dir):
            ext = os.path.splitext(fname)[1].lower()
            lang = "python" if ext == ".py" else ("java" if ext == ".java" else ("cpp" if ext == ".cpp" else None))
            if lang:
                with open(os.path.join(raw_dir, fname), "r", encoding="utf-8") as f:
                    seed_codes.append((f.read(), lang))

    if not seed_codes:
        seed_codes = [
            ("def sum_items(items):\n    s = 0\n    for x in items:\n        s += x\n    return s\n", "python")
        ]

    injector = BugInjector(seed=42)
    dataset = []

    # Inject multiple passes to reach target volume
    categories_list = list(BugCategory)
    per_category = max(num_samples // len(categories_list), 100)

    for cat in categories_list:
        for i in range(per_category):
            base_code, lang = seed_codes[i % len(seed_codes)]
            mutated = injector.mutate_program(base_code, language=lang)
            # Assign target category
            category = mutated["bug_category"]
            error_type = "SyntaxError" if category == "syntax_error" else (
                "NameError" if category == "undefined_name" else (
                    "IndexError" if category == "index_out_of_range" else (
                        "TypeError" if category == "type_error" else (
                            "TimeoutError" if category == "loop_boundary" else "RuntimeError"
                        )
                    )
                )
            )
            dataset.append({
                "code": mutated["mutated_code"],
                "error_type": error_type,
                "message": f"Error encountered in {category}",
                "category": category,
            })

    return dataset


def train_and_evaluate():
    print("=" * 60)
    print("SocraCode Step 3: Training Custom Classifier from Scratch")
    print("=" * 60)

    # 1. Dataset Generation
    print("Synthesizing labelled training dataset...")
    data = build_synthetic_dataset(num_samples=2400)
    print(f"Generated {len(data)} total samples.")

    codes = [d["code"] for d in data]
    error_types = [d["error_type"] for d in data]
    messages = [d["message"] for d in data]
    labels = [
        CATEGORY_INDEX_MAP.get(BugCategory(d["category"]), 0)
        for d in data
    ]

    # 2. Feature Extraction
    print("Fitting feature extractor (AST + tokens)...")
    extractor = CodeFeatureExtractor(max_token_features=80)
    extractor.fit([f"{c} {et} {m}" for c, et, m in zip(codes, error_types, messages)])
    X = extractor.extract_batch(codes, error_types, messages)
    y = np.array(labels, dtype=np.int64)

    # 80/20 train/test split
    indices = np.random.RandomState(42).permutation(len(X))
    split = int(0.8 * len(X))
    train_idx, test_idx = indices[:split], indices[split:]

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # 3. Train PyTorch Model
    print("Training PyTorch Neural Network from scratch...")
    input_dim = X_train.shape[1]
    num_classes = len(BugCategory)
    nn_model = BugClassifierNN(input_dim=input_dim, num_classes=num_classes)

    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
    )
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    optimizer = torch.optim.Adam(nn_model.parameters(), lr=0.005)
    criterion = nn.CrossEntropyLoss()

    nn_model.train()
    for epoch in range(1, 16):
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = nn_model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

    # PyTorch evaluation
    nn_model.eval()
    with torch.no_grad():
        test_logits = nn_model(torch.tensor(X_test, dtype=torch.float32))
        y_pred_nn = torch.argmax(test_logits, dim=-1).numpy()

    nn_metrics = evaluate_model_performance(y_test, y_pred_nn, model_name="PyTorch NN (From Scratch)")

    # 4. Train Scikit-Learn Baseline
    print("Training Scikit-Learn Random Forest Baseline...")
    baseline = ScikitLearnBaseline(n_estimators=100)
    baseline.fit(X_train, y_train)
    y_pred_baseline = baseline.predict(X_test)
    baseline_metrics = evaluate_model_performance(y_test, y_pred_baseline, model_name="Scikit-Learn Baseline")

    # 5. Print Comparison Report
    print("\n" + "=" * 60)
    print("CLASSIFIER EVALUATION COMPARISON REPORT")
    print("=" * 60)
    print(f"{'Metric':<20} | {'PyTorch NN':<16} | {'Baseline (RF)':<16}")
    print("-" * 60)
    nn_acc = float(nn_metrics["accuracy"]) * 100
    base_acc = float(baseline_metrics["accuracy"]) * 100
    nn_prec = float(nn_metrics["macro_precision"]) * 100
    base_prec = float(baseline_metrics["macro_precision"]) * 100
    nn_rec = float(nn_metrics["macro_recall"]) * 100
    base_rec = float(baseline_metrics["macro_recall"]) * 100
    nn_f1 = float(nn_metrics["macro_f1"]) * 100
    base_f1 = float(baseline_metrics["macro_f1"]) * 100

    print(f"{'Accuracy':<20} | {nn_acc:.2f}%{'':<9} | {base_acc:.2f}%")
    print(f"{'Macro Precision':<20} | {nn_prec:.2f}%{'':<9} | {base_prec:.2f}%")
    print(f"{'Macro Recall':<20} | {nn_rec:.2f}%{'':<9} | {base_rec:.2f}%")
    print(f"{'Macro F1-Score':<20} | {nn_f1:.2f}%{'':<9} | {base_f1:.2f}%")
    print("=" * 60)

    # 6. Save Artifacts for production backend
    out_dir = os.path.join(BACKEND_DIR, "app", "ml")
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, "model.pt")
    vectorizer_path = os.path.join(out_dir, "vectorizer.joblib")
    metrics_path = os.path.join(BASE_DIR, "data", "generated", "model_metrics.json")

    torch.save(nn_model.state_dict(), model_path)
    joblib.dump(extractor, vectorizer_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({"pytorch_nn": nn_metrics, "baseline_rf": baseline_metrics}, f, indent=2)

    print(f"\nArtifacts saved successfully:")
    print(f"  PyTorch weights: {model_path}")
    print(f"  Feature extractor: {vectorizer_path}")
    print(f"  Metrics report: {metrics_path}")


if __name__ == "__main__":
    train_and_evaluate()
