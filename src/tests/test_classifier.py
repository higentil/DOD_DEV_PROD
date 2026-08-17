import pytest
import numpy as np
from src.config import config
from src.data_pipeline import SignalPipeline
from src.ew_defense import EWSecurityEngine, DefensivelyDistilledWeights
from src.model_trainer import AdversarialTrainer


def test_pipeline_dimensions():
    pipeline = SignalPipeline()
    X_train, X_test, y_train, y_test = pipeline.generate_raw_dataset()

    # Verify rows match train split percentage bounds
    assert len(X_train) == int(config.num_samples * config.train_split)
    # FIX: Correct matrix shape comparison check for 2D signal arrays
    assert X_train.shape[1] == int(config.sampling_rate * config.signal_duration)


def test_threat_engine_integrity():
    # FIX: Provide a valid non-empty array with matching row dimensions
    mock_signals = np.zeros((10, 1000))
    mock_labels = np.zeros(10, dtype=int)

    model = DefensivelyDistilledWeights()
    trainer = AdversarialTrainer(model)

    # Validate Barrage Jamming
    jammed = EWSecurityEngine.inject_barrage_jamming(mock_signals)
    assert jammed.shape == mock_signals.shape
    assert not np.array_equal(jammed, mock_signals)

    # Validate Adversarial Spoofing
    spoofed = trainer._inject_frequency_spoof(mock_signals, mock_labels)
    assert spoofed.shape == mock_signals.shape
    assert not np.array_equal(spoofed, mock_signals)
    assert np.max(np.abs(spoofed)) <= 2.0


def test_model_training_and_evaluation_flow():
    pipeline = SignalPipeline()
    X_train, X_test, y_train, y_test = pipeline.generate_raw_dataset()

    model = DefensivelyDistilledWeights()
    trainer = AdversarialTrainer(model)

    trainer.fit(X_train, y_train, harden=False)
    acc_standard = trainer.evaluate(X_test, y_test)
    assert 0.0 <= acc_standard <= 1.0

    trainer.fit(X_train, y_train, harden=True)
    acc_hardened = trainer.evaluate(X_test, y_test)
    assert 0.0 <= acc_hardened <= 1.0
