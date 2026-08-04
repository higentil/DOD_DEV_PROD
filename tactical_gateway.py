import socket
import sqlite3
import sys
from config import LOCAL_HOST, GATEWAY_LISTEN_PORT, DB_FILE
from local_triage import analyze_battlefield_report 
from tactical_crypto import decrypt_packet

def init_local_database():
    """Initializes local storage schema configurations safely using secure context scopes."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tactical_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sender TEXT,
                raw_message TEXT,
                ai_status TEXT,
                ai_payload TEXT
            )
        ''')
        conn.commit()

def log_to_local_cache(sender: str, message: str, status: str, ai_json: str = None):
    """Guarantees handle release on every atomic ledger transaction."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tactical_logs (sender, raw_message, ai_status, ai_payload) VALUES (?, ?, ?, ?)",
            (sender, message, status, ai_json)
        )
        conn.commit()
    print(f"💾 [LEDGER] Entry synchronized locally. Status: {status}")

def start_gateway():
    init_local_database()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_HOST, GATEWAY_LISTEN_PORT))
    
    if sys.platform == "win32":
        try:
            sock.ioctl(socket.SIO_UDP_CONNRESET, False)
        except AttributeError:
            pass

    print(f"🛡️ [GATEWAY] Command Center Processing Node Active on Port {GATEWAY_LISTEN_PORT}...\n")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            payload = decrypt_packet(data)
            sender = payload.get('sender', 'UNKNOWN')
            raw_text = payload.get('message', '')
            
            triage_result = analyze_battlefield_report(raw_text)
            log_to_local_cache(sender, raw_text, "PROCESSED_SUCCESS", triage_result)
            print("-" * 60)
            
        except ConnectionResetError:
            print("⚠️ [WIRE] Trapped transient connection dropout.")
        except (ValueError, PermissionError) as crypto_err:
            print(f"❌ [SECURITY INFRACTION BLOCK] Cypher threat or invalid tag signature: {crypto_err}")
        except Exception as e:
            print(f"❌ [UNHANDLED ANOMALY] Gateway runtime error: {e}")

if __name__ == "__main__":
    start_gateway()
