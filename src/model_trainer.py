import numpy as np
from src.config import config
from src.ew_defense import EWSecurityEngine, DefensivelyDistilledWeights


class AdversarialTrainer:
    def __init__(self, model: DefensivelyDistilledWeights):
        self.model = model
        self.t = np.linspace(0, config.signal_duration, int(config.sampling_rate * config.signal_duration))

    def _extract_fft_features(self, X: np.ndarray) -> np.ndarray:
        fft_values = np.abs(np.fft.fft(X, axis=1))[:, :150]

        min_vals = np.min(fft_values, axis=1, keepdims=True)
        max_vals = np.max(fft_values, axis=1, keepdims=True)

        return (fft_values - min_vals) / (max_vals - min_vals + 1e-8)

    def _inject_frequency_spoof(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        spoofed = X.copy()
        X_features = self._extract_fft_features(spoofed)
        predictions = self.model.predict_proba(X_features)
        error_directions = predictions - y

        for i in range(len(X)):
            if y[i] == 0:
                # Target is high-frequency Radar Chirp. Flood with a broad low-frequency comms block
                f0, f1 = 20.0, 40.0
            else:
                # Target is low-frequency Comms Wave. Flood with a broad high-frequency radar sweep
                f0, f1 = 120.0, 200.0

            deceptive_sweep = np.sin(
                2 * np.pi * (f0 * self.t + (f1 - f0) / (2 * config.signal_duration) * (self.t ** 2)))
            targeted_attack = deceptive_sweep * np.sign(error_directions[i])

            # Blend the targeted attack wave directly using the config epsilon slider power bounds
            spoofed[i] = (1.0 - config.spoof_epsilon) * X[i] + (config.spoof_epsilon * 4.5 * targeted_attack)

        return np.clip(spoofed, -2.0, 2.0)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, harden: bool = False):
        num_samples = X_train.shape[0]

        rng = np.random.RandomState(config.random_seed)
        self.model.weights = rng.uniform(-0.5, 0.5, 150)
        self.model.bias = 0.0

        lr = config.learning_rate

        for epoch in range(config.epochs):
            X_batch = X_train.copy()

            if harden:
                # Using 50/50 mixed-batch defense
                half_samples = num_samples // 2
                X_batch[:half_samples] = self._inject_frequency_spoof(X_batch[:half_samples], y_train[:half_samples])

            X_features = self._extract_fft_features(X_batch)
            predictions = self.model.predict_proba(X_features)
            errors = predictions - y_train

            dW = np.dot(X_features.T, errors) / num_samples
            db = np.sum(errors) / num_samples

            self.model.weights -= lr * dW
            self.model.bias -= lr * db

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        X_features = self._extract_fft_features(X_test)
        predictions = self.model.predict(X_features)
        return float(np.mean(predictions == y_test))
