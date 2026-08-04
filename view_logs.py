import json
import sqlite3
from config import DB_FILE

R, A, G, W = "\033[91m", "\033[93m", "\033[92m", "\033[0m"

def display_tactical_dashboard():
    """Outputs a highly condensed, single-line tabular view of tactical intel records."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, sender, ai_payload, raw_message FROM tactical_logs ORDER BY id DESC LIMIT 30")
            rows = cursor.fetchall()
            
        if not rows:
            print("\n[!] OPERATIONAL LEDGER EMPTY: NO PACKETS CAPTURED.")
            return

        print(f"\n{'ID':<4} | {'TIMESTAMP':<19} | {'CALLSIGN':<20} | {'TRT':<5} | {'MED':<5} | {'TACTICAL DIRECTIVE / INTEL SUMMARY'}")
        print("-" * 110)

        for row in rows:
            record_id, timestamp, sender, ai_payload, raw_message = row
            threat, med_urgency, summary, color = "GREEN", "NONE", "UNPARSED DATA FEED", G
            
            if ai_payload:
                try:
                    intel = json.loads(ai_payload)
                    threat = intel.get("threat_level", "GREEN")
                    med_urgency = "REQ" if intel.get("medical_urgency") else "NONE"
                    summary = intel.get("summary", "N/A")
                except json.JSONDecodeError:
                    summary = f"CORRUPT PAYLOAD: {raw_message[:40]}..."

            if threat == "RED" or med_urgency == "REQ":
                color, threat_tag, med_tag = R, "RED", "🚨"
            elif threat == "AMBER":
                color, threat_tag, med_tag = A, "AMB", "⚠️"
            else:
                color, threat_tag, med_tag = G, "GRN", "  "

            print(f"{color}{record_id:<4}{W} | {timestamp:<19} | {sender:<20} | {color}{threat_tag:<5}{W} | {med_tag:<5} | {color}{summary}{W}")
            
    except sqlite3.OperationalError:
        print("\n[❌] ERROR: Ledger database offline or file not initialized.")
    except Exception as e:
        print(f"\n[❌] SYSTEM ANOMALY: {e}")

if __name__ == "__main__":
    display_tactical_dashboard()
