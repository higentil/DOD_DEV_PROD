import json
import socket
import sqlite3
import streamlit as st
from config import DB_FILE, LOCAL_HOST, RELAY_LISTEN_PORT
from tactical_crypto import encrypt_packet

st.set_page_config(page_title="TOC Tactical Monitor", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1, h2, h3 { font-family: 'Courier New', monospace; font-weight: bold; }
    .threat-red { border-left: 6px solid #FF3B30; padding-left: 10px; background-color: #2c1a1a; margin-bottom: 10px; border-radius: 4px; }
    .threat-amber { border-left: 6px solid #FFCC00; padding-left: 10px; background-color: #2c251a; margin-bottom: 10px; border-radius: 4px; }
    .threat-green { border-left: 6px solid #34C759; padding-left: 10px; background-color: #1a2c1d; margin-bottom: 10px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

def get_db_entries():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, sender, ai_status, ai_payload, raw_message FROM tactical_logs ORDER BY id DESC")
            return cursor.fetchall()
    except Exception:
        return []

st.title("TOC TACTICAL OPERATIONS MONITOR")
c_net1, c_net2, c_net3, c_btn = st.columns(4)
c_net1.success("📡 MESH LINK: OPERATIONAL")
c_net2.success("🔒 CIPHER: AES-256-GCM")
c_net3.success("🧠 PARSER: SECURE LOCAL")
if c_btn.button("🔄 FORCE REFRESH FEED", use_container_width=True):
    st.rerun()

st.markdown("---")
col_transmit, col_ledger = st.columns(2)

with col_transmit:
    st.subheader("⚡ RAPID SITREP INJECTION")
    sim_sender = st.selectbox("ORIGINATING UNIT:", ["Strike_Team_Delta", "Recon_Squad_Charlie", "Echo_Company_6", "Forward_Base_Alpha"])
    sim_message = st.text_area("RAW AUDIO TRANSCRIPT FEED:", placeholder="Type tactical feed information text here...", height=150)
    
    if st.button("🚀 TRANSMIT PACKET OVER AIR", use_container_width=True):
        if sim_message.strip():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                payload = {"sender": sim_sender, "message": sim_message}
                sock.sendto(encrypt_packet(payload), (LOCAL_HOST, RELAY_LISTEN_PORT))
                st.toast("⚡ Packet broadcasted successfully.", icon="🛰️")
                import time; time.sleep(1.2)
                st.rerun()
            except Exception as e:
                st.error(f"TX FAILURE: {e}")

with col_ledger:
    st.subheader("📋 ACTIVE COMISSION LOG MATRIX")
    entries = get_db_entries()
    
    if not entries:
        st.info("📭 CLEAR LEDGER: No data streams intercepted.")
    else:
        for row in entries:
            record_id, timestamp, sender, status, ai_payload, raw_message = row
            intel = {}
            if status == "PROCESSED_SUCCESS" and ai_payload:
                try: intel = json.loads(ai_payload)
                except Exception: pass
            
            threat = intel.get("threat_level", "GREEN")
            if threat == "RED":
                css_class, header, is_expanded = "threat-red", f"🚨 RED ALERT | MSG #{record_id} | CALLSIGN: {sender}", True
            elif threat == "AMBER":
                css_class, header, is_expanded = "threat-amber", f"⚠️ AMBER ALERT | MSG #{record_id} | CALLSIGN: {sender}", False
            else:
                css_class, header, is_expanded = "threat-green", f"🟢 ROUTINE | MSG #{record_id} | CALLSIGN: {sender}", False

            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            with st.expander(header, expanded=is_expanded):
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"**⏰ TIME:** `{timestamp}`")
                m2.markdown(f"**🩹 MEDEVAC:** {'🚨 REQUIRED' if intel.get('medical_urgency') else '✅ NONE'}")
                m3.markdown("**🔒 CRYPTO:** SECURE")
                st.markdown("**🎯 DIRECTIVE SUMMARY:**")
                st.warning(f"\"{intel.get('summary', 'TRIAGE ERROR')}\"")
                st.markdown("**🎤 INTERCEPTED TRANSCRIPT:**")
                st.caption(f"_{raw_message}_")
            st.markdown('</div>', unsafe_allow_html=True)
