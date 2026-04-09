import torch
import numpy as np
from typing import Optional, List, Dict
from app.ml.model import load_model
from app.config import settings

_predictor_instance: Optional['Predictor'] = None

class Predictor:
    """Wrapper for model predictions"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = load_model(settings.MODEL_PATH, settings.NUM_CLASSES, self.device)
        self.model.to(self.device)
        
        # Placeholder for character mapping (ETL9G dataset)
        # In production, load the actual character mapping from a file
        self.character_map = self._load_character_map()
    
    def _load_character_map(self) -> Dict[int, str]:
        """Load character mapping (placeholder)"""
        # TODO: Load actual character labels from ETL9G dataset
        # For now, return a dict mapping indices to dummy characters
        return {i: chr(0x3040 + (i % 85)) for i in range(settings.NUM_CLASSES)}
    
    def predict(self, canvas_data: np.ndarray, top_k: int = 15) -> List[Dict[str, float]]:
        """
        Predict character from canvas data.
        
        Args:
            canvas_data: 96x96 grayscale image as numpy array (0-255)
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions with character and confidence
        """
        # Normalize input
        canvas_normalized = canvas_data.astype(np.float32) / 255.0
        
        # Convert to tensor
        input_tensor = torch.from_numpy(canvas_normalized).unsqueeze(0).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            logits = self.model(input_tensor)
            probabilities = torch.softmax(logits, dim=1)[0]
        
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probabilities, min(top_k, settings.MAX_PREDICTIONS))
        
        predictions = []
        for prob, idx in zip(top_probs, top_indices):
            char_idx = idx.item()
            predictions.append({
                "character": self.character_map.get(char_idx, "?"),
                "confidence": float(prob.item())
            })
        
        return predictions

def get_predictor() -> Predictor:
    """Get or create singleton predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = Predictor()
    return _predictor_instance
