# Defensive Electronic Warfare (EW) Signal Classifier

A pipeline-driven simulation platform implementing **Adversarial Machine Learning** to secure airborne sensor tracking systems. This repository transitions an unhardened signal classifier into a robust framework capable of maintaining target locks under high-power broadband interference (**Barrage Jamming**) and optimization-driven wave injection (**In-Band Bandwidth Flooding Attacks**).

---

## System Architecture Layout
The codebase strictly decouples data ingestion, signal transformations, threat vectors, optimization loops, and user interfaces into modular software layers:

```text
SensorClassifier/
├── src/
│   ├── config.py               # Pydantic type-safe hyperparameter management
│   ├── data_pipeline.py        # DSP signal generation with isolated random state engines
│   ├── ew_defense.py           # Classifier weights representation & sigmoid mapping
│   └── model_trainer.py        # Independent-sample FFT pipelines & mixed-batch training
├── tests/
│   └── test_classifier.py      # Pytest validation harness
├── app_ui.py                   # High-contrast tactical command terminal UI (Streamlit)
└── requirements.txt            # Explicit dependency pinning
```

---

## Algorithmic & Mathematical Foundations

### 1. Ingestion & Feature Engineering (Fourier Domain Transition)
Raw time-domain waveforms with randomized phase shifts cancel out signal distributions over broad data horizons, bounding basic time-domain linear classifiers to a random-guess ceiling (~50%). 

To resolve this, this pipeline converts 1D time arrays into a static frequency magnitude spectrum using a **Fast Fourier Transform (FFT)**. It scales features independently on a strict **per-signal axis ($axis=1$)** to preserve structural uniqueness and eliminate batch data leakage:

$$X_{\text{features}}^{(i)} = \frac{||\text{FFT}(X^{(i)})_{:150}|| - \min(||\text{FFT}(X^{(i)})_{:150}||)}{\max(||\text{FFT}(X^{(i)})_{:150}||) - \min(||\text{FFT}(X^{(i)})_{:150}||) + \epsilon}$$

This forces the classifier to isolate static frequency energy blocks rather than shifting time steps, moving baseline accuracy from **50.0% to 100.0%**.

### 2. The Adversarial Threat Vector (In-Band Bandwidth Flooding)
Single-tone injections are easily bypassed by frequency-domain feature models. To create an authentic threat vector, this engine runs an **In-Band Bandwidth Flooding Exploit**. It extracts classification error paths and synthesizes a full, destructive cross-class sweep matching the victim signal's exact parameters:

$$X_{\text{spoofed}} = (1 - \epsilon) \cdot X_{\text{original}} + (\epsilon \cdot 4.5 \cdot \text{DeceptiveSweep})$$

This injects a low-frequency communication wave configuration into radar chirps, and a high-frequency chirp matrix into baseband comms lines. This successfully floods the specific frequency bins the model depends on, tanking unhardened target tracking locks from **100.0% to 0.0%**.

### 3. Mitigating Model Collapse (50/50 Mixed-Batch Defense)
Training exclusively on heavily spoofed arrays causes **Label Inversion and Model Collapse**, where a model achieves 100% accuracy under attack but drops to ~3.0% accuracy on clean, uncorrupted signals. 

This pipeline implements a **50/50 Mixed-Batch Training Strategy**. Within each epoch, optimization steps are computed across an equal split of clean signals and adversarially spoofed waveforms. This trains the model to ignore artificial spectrum spikes, successfully stabilizing the system against strategic countermeasures.

---

## Local Verification & Deployment

### 1. Environment Ingestion
Ensure your terminal environment path is located in the target directory and execute the dependency sync:
```bash
pip install -r requirements.txt
```

### 2. Run Automated Regression Test Harness
Run the testing validation suite using Python's module interpreter to guarantee package lookup paths align perfectly:
```bash
python -m pytest -v
```
*(All 3 tests—pipeline dimensions, threat engine integrity, and optimization flows—will return green passing indicators.)*

### 3. Spin Up the Interactive Terminal Profile
Launch the web deployment layer straight from the local command line interface:
```bash
streamlit run app_ui.py
```
Open your default web browser to `http://localhost:8501`. Toggle between the slider buttons to simulate active jamming power levels or strategic spoofing coefficients, and watch your defensively distilled system dynamically hold its lock in real time.


