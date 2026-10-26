import torch
import torch.nn as nn
from typing import Tuple


class BugClassifierNN(nn.Module):
    """
    Compact PyTorch neural network trained from scratch.
    Classifies code snippets into one of the 8 canonical bug categories.
    """

    def __init__(self, input_dim: int, num_classes: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def predict_with_confidence(self, x: torch.Tensor) -> Tuple[int, float]:
        """Runs inference and returns (predicted_class_index, confidence_score)."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=-1)
            confidence, class_idx = torch.max(probabilities, dim=-1)
            return int(class_idx.item()), float(round(float(confidence.item()), 4))
