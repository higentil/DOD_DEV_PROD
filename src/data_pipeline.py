import numpy as np
from src.config import config

class SignalPipeline:
    def __init__(self):
        #Localize random states to prevent global seed contamination/data leaks
        self.rng = np.random.RandomState(config.random_seed)
        self.t = np.linspace(0, config.signal_duration, int(config.sampling_rate * config.signal_duration))

    def generate_raw_dataset(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        half_size = config.num_samples // 2
        signals = []
        labels = []

        # Radar Chirps (Fixed Math Sweep Equation)
        for _ in range(half_size):
            f0 = self.rng.uniform(120, 140)
            f1 = self.rng.uniform(180, 200)
            phase = self.rng.uniform(0, 2 * np.pi)

            #Instantaneous linear frequency sweep phase accumulation math
            chirp = np.sin(2 * np.pi * (f0 * self.t + (f1 - f0) / (2 * config.signal_duration) * (self.t ** 2)) + phase)
            signals.append(chirp)
            labels.append(0)

        #Communication Signals
        for _ in range(half_size):
            f_carrier = self.rng.uniform(20, 40)

            # Use localized rng state safely
            bits = self.rng.choice([0, np.pi], size=5)
            bit_repeats = len(self.t) // len(bits)
            phase_modulation = np.repeat(bits, bit_repeats)

            if len(phase_modulation) < len(self.t):
                phase_modulation = np.pad(phase_modulation, (0, len(self.t) - len(phase_modulation)), 'edge')

            comms = np.sin(2 * np.pi * f_carrier * self.t + phase_modulation[:len(self.t)])
            signals.append(comms)
            labels.append(1)

        X = np.array(signals)
        y = np.array(labels)

        return self.shuffle_and_split(X, y)

    def shuffle_and_split(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        indices = np.arange(len(y))
        # Use localized state for splitting stability
        self.rng.shuffle(indices)
        X, y = X[indices], y[indices]

        split_idx = int(len(y) * config.train_split)

        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        return X_train, X_test, y_train, y_test
