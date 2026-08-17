import streamlit as st
import numpy as np
import pandas as pd
from src.config import config
from src.data_pipeline import SignalPipeline
from src.ew_defense import EWSecurityEngine, DefensivelyDistilledWeights
from src.model_trainer import AdversarialTrainer

st.set_page_config(page_title="EW Sensor Defense Terminal", layout="wide")

# Custom injection CSS for tactical Dark-Mode styling
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #00ff66; font-family: 'Courier New', monospace; }
    h1, h2, h3 { color: #00ff66 !important; text-shadow: 0 0 10px #00ff66; }
    .stButton>button { background-color: #1f242c; color: #00ff66; border: 1px solid #00ff66; }
    .css-1offfwp p { color: #00ff66 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("EW ADVERSARIAL SENSOR CLASSIFIER")
st.subheader("Tactical Command Terminal Profile")

# Sidebar Control Console Parameters Setup
st.sidebar.header("Electronic Attack Vectors")
config.jamming_power = st.sidebar.slider("Barrage Jamming Power (Noise Variance)", 0.0, 5.0, 1.5)
config.spoof_epsilon = st.sidebar.slider("Adversarial Spoofing Limit (FGSM Epsilon)", 0.0, 1.0, 0.3)

st.sidebar.header("Model Distillation Controls")
config.learning_rate = st.sidebar.slider("Model Learning Rate (Step Size)", 0.01, 0.5, 0.2)
config.epochs = st.sidebar.slider("Training Epochs", 5, 50, 15)
harden_checkbox = st.sidebar.checkbox("Deploy Adversarial Training (Hardened System)")

# Cache data generation states natively
if 'data' not in st.session_state:
    pipeline = SignalPipeline()
    st.session_state.data = pipeline.generate_raw_dataset()

X_train, X_test, y_train, y_test = st.session_state.data

# Initialize & Train Target Models
standard_model = DefensivelyDistilledWeights()
trainer = AdversarialTrainer(standard_model)

with st.spinner("Optimizing defense matrix parameters..."):
    trainer.fit(X_train, y_train, harden=harden_checkbox)

# Run Live Simulations Across Three Environments
# First Environment: Clean Signal State
acc_clean = trainer.evaluate(X_test, y_test)

# Second Environment: Barrage Jamming Environment (Brute-Force White Noise)
X_test_jammed = EWSecurityEngine.inject_barrage_jamming(X_test)
acc_jammed = trainer.evaluate(X_test_jammed, y_test)

# Third Environment:Adversarial Spoofing Environment (Targeted Electronic Deception)
X_test_spoofed = trainer._inject_frequency_spoof(X_test, y_test)
acc_spoofed = trainer.evaluate(X_test_spoofed, y_test)

# Render Real-Time Technical Dashboard Gauges
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Clean Tracking Lock", value=f"{acc_clean * 100:.1f}%")
    st.caption("Baseline uncorrupted target signature accuracy.")

with col2:
    st.metric(label="Under Barrage Jamming", value=f"{acc_jammed * 100:.1f}%",
              delta=f"{(acc_jammed - acc_clean)*100:.1f}% Status")
    st.caption("Brute-force noise interference signature degradation.")

with col3:
    st.metric(label="Under Adversarial Spoofing", value=f"{acc_spoofed * 100:.1f}%",
              delta=f"{(acc_spoofed - acc_clean)*100:.1f}% Status")
    st.caption("Coordinated optimization-driven target manipulation.")

# Visual Status Callouts
if harden_checkbox:
    st.success("DEFENSIVE ENGINE STATUS: HARDENED AGAINST COUNTERMEASURES")
else:
    st.warning("DEFENSIVE ENGINE STATUS: VULNERABLE TO STRATEGIC ADVERSARIAL ATTACKS")

st.markdown("---")
st.subheader("Live Raw Signal Footprint Visualizer")
selected_idx = st.selectbox("Select Signal Waveform Instance ID to Inspect", range(len(X_test)))

signal_type = "Communication Transmission (PSK-5)" if y_test[selected_idx] == 1 else "Radar Spatial Chirp"
st.text(f"Ground Truth Target Vector Class Profile: {signal_type}")

# FIX: Map dictionary vectors safely into a structured Pandas DataFrame for clean Streamlit line rendering
chart_df = pd.DataFrame({
    "Original Signal Sample": X_test[selected_idx],
    "Jammed Interference Array": X_test_jammed[selected_idx],
    "Spoofed Adversarial Array": X_test_spoofed[selected_idx]
})

st.line_chart(chart_df)
