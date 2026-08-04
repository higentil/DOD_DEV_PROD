import collections
import socket
import sys
import time
from config import LOCAL_HOST, RELAY_LISTEN_PORT, GATEWAY_LISTEN_PORT

BACKUP_QUEUE = collections.deque(maxlen=50)

def start_relay():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_HOST, RELAY_LISTEN_PORT))
    
    if sys.platform == "win32":
        try:
            sock.ioctl(socket.SIO_UDP_CONNRESET, False)
        except AttributeError:
            pass

    print(f"📡 [NODE-B] Tactical Relay Armed on Port {RELAY_LISTEN_PORT}...")

    while True:
        try:
            if BACKUP_QUEUE:
                cached_data = BACKUP_QUEUE.popleft()
                sock.sendto(cached_data, (LOCAL_HOST, GATEWAY_LISTEN_PORT))
                time.sleep(0.1)

            data, addr = sock.recvfrom(4096)
            sock.sendto(data, (LOCAL_HOST, GATEWAY_LISTEN_PORT))
            
        except ConnectionResetError:
            if 'data' in locals() and data:
                BACKUP_QUEUE.append(data)
                print(f"⚠️ [LINK LOSS] Gateway offline. Payload cached locally ({len(BACKUP_QUEUE)}/50).")
        except Exception as e:
            print(f"❌ [SYSTEM ERROR] Network anomaly trapped: {e}")

if __name__ == "__main__":
    start_relay()
