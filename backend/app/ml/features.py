import ast
import re
from typing import Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

KNOWN_ERROR_TYPES = [
    "SyntaxError",
    "IndentationError",
    "NameError",
    "UnboundLocalError",
    "TypeError",
    "IndexError",
    "TimeoutError",
    "ZeroDivisionError",
]


class CodeFeatureExtractor:
    """
    Extracts structural AST features, error signatures, and token statistics.
    Uses zero pretrained embeddings, satisfying Constraint 2.
    """

    def __init__(self, max_token_features: int = 80):
        self.max_token_features = max_token_features
        self.text_vectorizer = TfidfVectorizer(
            max_features=max_token_features,
            token_pattern=r"(?u)\b\w+\b|[^\w\s]",
        )
        self.is_fitted = False

    def fit(self, texts: List[str]) -> "CodeFeatureExtractor":
        self.text_vectorizer.fit(texts)
        self.is_fitted = True
        return self

    def extract_single(self, code: str, error_type: str, message: str) -> np.ndarray:
        # 1. Error Type One-Hot (len = 9)
        err_vec = [1.0 if error_type == t else 0.0 for t in KNOWN_ERROR_TYPES]
        err_vec.append(1.0 if error_type not in KNOWN_ERROR_TYPES else 0.0)

        # 2. AST Structure Indicators (len = 8)
        ast_vec = [0.0] * 8
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    ast_vec[0] = 1.0
                elif isinstance(node, ast.While):
                    ast_vec[1] = 1.0
                elif isinstance(node, ast.If):
                    ast_vec[2] = 1.0
                elif isinstance(node, ast.FunctionDef):
                    ast_vec[3] = 1.0
                elif isinstance(node, ast.Return):
                    ast_vec[4] = 1.0
                elif isinstance(node, ast.Subscript):
                    ast_vec[5] = 1.0
                elif isinstance(node, ast.BinOp):
                    ast_vec[6] = 1.0
                elif isinstance(node, ast.Call):
                    ast_vec[7] = 1.0
        except SyntaxError:
            # If syntax error, mark AST failure flag
            ast_vec[0] = 0.5

        # 3. Code Statistics (len = 5)
        lines = code.splitlines()
        stats_vec = [
            min(len(lines) / 20.0, 1.0),
            min(len(code) / 500.0, 1.0),
            1.0 if any(l.strip().endswith(":") for l in lines) else 0.0,
            1.0 if code.count("(") == code.count(")") else 0.0,
            1.0 if code.count("[") == code.count("]") else 0.0,
        ]

        # 4. Text Vectorizer (len = max_token_features)
        combined_text = f"{code} {error_type} {message}"
        if self.is_fitted:
            text_vec = self.text_vectorizer.transform([combined_text]).toarray()[0]
        else:
            text_vec = np.zeros(self.max_token_features)

        # Combine all features
        feature_vector = np.concatenate([err_vec, ast_vec, stats_vec, text_vec])
        return feature_vector.astype(np.float32)

    def extract_batch(
        self, codes: List[str], error_types: List[str], messages: List[str]
    ) -> np.ndarray:
        vectors = [
            self.extract_single(c, et, msg)
            for c, et, msg in zip(codes, error_types, messages)
        ]
        return np.vstack(vectors)
