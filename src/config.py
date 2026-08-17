from pydantic import BaseModel, Field

class EWSensorConfig(BaseModel):
    # Signal Parameters
    sampling_rate: int = Field(default=1000, description="Hz")
    signal_duration: float = Field(default=1.0, description="Seconds")
    num_samples: int = Field(default=500, description="Dataset size")
    random_seed: int = Field(default=42, description="Reproducibility anchor")

    # EW Attack Parameters
    jamming_power: float = Field(default=1.5, description="Variance of noise")
    spoof_epsilon: float = Field(default=0.3, description="Adversarial perturbation limit")

    # Model Training Parameters
    # FIX: Scaled to 0.2 to perfectly match our standardized FFT gradient space
    learning_rate: float = Field(default=0.2, description="Gradient step size")
    epochs: int = Field(default=15, description="Optimization rounds")
    train_split: float = Field(default=0.8, description="Train/Test ratio")

# Global singleton configuration object
config = EWSensorConfig()
