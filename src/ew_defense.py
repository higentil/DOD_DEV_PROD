import numpy as np
from src.config import config

class EWSecurityEngine:
    @staticmethod
    def inject_barrage_jamming(signals: np.ndarray) -> np.ndarray:
        # Create an isolated local noise array matching signal layout dimensions
        noise = np.random.normal(0, config.jamming_power, signals.shape)
        return signals + noise

class DefensivelyDistilledWeights:
    def __init__(self, input_dim: int = 150):
        # Localize the seed state calculation to prevent resetting the global environment
        rng = np.random.RandomState(config.random_seed)
        self.weights = rng.normal(0, 0.01, input_dim)
        self.bias = 0.0

    def predict_proba(self, X_features: np.ndarray) -> np.ndarray:
        z = np.dot(X_features, self.weights) + self.bias
        # Expand stability clips to prevent gradient step truncation over normalized feature sets
        return 1 / (1 + np.exp(-np.clip(z, -50.0, 50.0)))

    def predict(self, X_features: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X_features) >= 0.5).astype(int)
