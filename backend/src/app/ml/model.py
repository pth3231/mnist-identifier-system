import torch
import torch.nn as nn
import numpy as np
from typing import Optional
from ..config import settings

class JapaneseCharacterClassifier(nn.Module):
    """Deep learning model for Japanese character classification"""
    
    def __init__(self, input_size: int = 9216, num_classes: int = 3036):
        super().__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(input_size, 512)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(256, 128)
        self.dropout3 = nn.Dropout(0.3)
        self.fc4 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.dropout1(x)
        x = self.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.relu(self.fc3(x))
        x = self.dropout3(x)
        x = self.fc4(x)
        return x

def load_model(model_path: str, num_classes: int = 3036, device: str = "cpu") -> JapaneseCharacterClassifier:
    """Load a trained model"""
    model = JapaneseCharacterClassifier(input_size=9216, num_classes=num_classes)
    try:
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
        model.eval()
    except FileNotFoundError:
        print(f"Warning: Model file not found at {model_path}. Using untrained model.")
    return model
