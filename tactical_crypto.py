import json
import time
from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from config import get_secure_crypto_key, MAX_CLOCK_SKEW_SECONDS

def encrypt_packet(payload_dict: dict) -> bytes:
    """Injects anti-replay timestamps and encrypts payload arrays securely using AES-256-GCM."""
    payload_dict["_tx_timestamp"] = time.time()
    serialized_data = json.dumps(payload_dict).encode('utf-8')
    
    cipher = AES.new(get_secure_crypto_key(), AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(serialized_data)
    
    encrypted_packet = {
        "nonce": b64encode(cipher.nonce).decode('utf-8'),
        "ciphertext": b64encode(ciphertext).decode('utf-8'),
        "tag": b64encode(tag).decode('utf-8')
    }
    return json.dumps(encrypted_packet).encode('utf-8')

def decrypt_packet(raw_bytes: bytes) -> dict:
    """Verifies GCM authenticity signatures and explicitly validates time windows to block replays."""
    try:
        packet = json.loads(raw_bytes.decode('utf-8'))
        nonce = b64decode(packet["nonce"])
        ciphertext = b64decode(packet["ciphertext"])
        tag = b64decode(packet["tag"])
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Wire protocol unpacking failure: {e}")
        
    cipher = AES.new(get_secure_crypto_key(), AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
    payload = json.loads(decrypted_data.decode('utf-8'))
    
    tx_time = payload.get("_tx_timestamp", 0)
    if abs(time.time() - tx_time) > MAX_CLOCK_SKEW_SECONDS:
        raise PermissionError("Security alert: Packet rejected due to temporal skew/replay validation failure.")
        
    payload.pop("_tx_timestamp", None)
    return payload
