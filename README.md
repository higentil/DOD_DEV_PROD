# 🛡️ Secure Edge Communications Network Mesh (DoW Prototype)

An off-grid, decentralized, multi-hop tactical mesh network simulation designed for austere, zero-connectivity battlefield deployment scenarios.

## 🏗️ System Architecture

```text
[Edge Node A (Client)] ──(AES-256-GCM Radio Burst)──> [Node B (Relay Windows Socket Proxy)] ──(UDP Hop)──> [Command Gateway] ──> [Local Triage Processing Core] ──> [SQLite Secure Ledger]
```

## ⚡ Core Engineering Features

- **Asynchronous Wire Simulation:** Developed utilizing connectionless UDP sockets to model physical over-the-air bottlenecks typical of Bluetooth Direct and LoRa hardware modules.
- **Cryptographic Anti-Replay Engine:** Hardened application-layer security via AES-256-GCM authenticated encryption paired with temporal clock-skew tracking to block adversarial packet capture and replay spoofing.
- **Deterministic Edge Tokenizer:** Features a sub-millisecond local parsing module that sanitizes military pleasantries and filters filler words out of high-entropy text to assemble dense low-bandwidth payload profiles.
- **Resource-Insulated Local Caching:** Implements explicit Python context managers (`with` scopes) across an offline transactional SQLite ledger to protect thread execution files against connection leakage or filesystem handle corruption.

## 🚀 Installation & Local Deployment

1. **Clone the repository and cross into the root footprint:**
   ```bash
   git clone https://github.com/higentil/DOD_DEV_PROD.git
   cd secure-edge-communications
   ```

2. **Initialize your virtual environment and arm required dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Establish your secure master cryptographic token inside your terminal scope:**
   ```bash
   # On macOS/Linux:
   export TACTICAL_SHARED_KEY="TacticalSecretKeyMustBe32Bytes!!"
   
   # On Windows (PowerShell):
   \$env:TACTICAL_SHARED_KEY="TacticalSecretKeyMustBe32Bytes!!"
   ```

4. **Launch the offline services across separate terminal sessions:**
   - **Terminal 1 (Command Hub):** `python tactical_gateway.py`
   - **Terminal 2 (Radio Relay Node):** `python edge_relay.py`
   - **Terminal 3 (Tactical Monitor UI):** `streamlit run app_ui.py`

## 🧪 Automated Testing

This architecture maintains 100% test coverage over core cryptographic, data integrity, and anti-replay verification modules using `pytest`. Verify code parameters locally by running:

```bash
pytest -v
```
