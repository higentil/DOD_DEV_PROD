import time
import pytest
from Crypto.Cipher import AES
from tactical_crypto import encrypt_packet, decrypt_packet

def test_successful_encryption_decryption_loop():
    """Verifies that a valid data packet is encrypted and decrypted with 100% fidelity."""
    mock_payload = {
        "sender": "Strike_Team_Alpha",
        "message": "Enroute to objective checkpoint green. Status routine."
    }
    
    # 1. Scramble message array
    encrypted_bytes = encrypt_packet(mock_payload)
    assert isinstance(encrypted_bytes, bytes)
    
    # 2. Descramble message array
    decrypted_dict = decrypt_packet(encrypted_bytes)
    
    # 3. Assert deep parity match
    assert decrypted_dict["sender"] == "Strike_Team_Alpha"
    assert decrypted_dict["message"] == "Enroute to objective checkpoint green. Status routine."

def test_tampered_ciphertext_fails_integrity_check():
    """Verifies that if an attacker alters even 1 bit of data, AES-GCM tags catch it and drop it."""
    mock_payload = {"sender": "Recon_1", "message": "All quiet."}
    encrypted_bytes = encrypt_packet(mock_payload)
    
    # Simulating data corruption by flipping bits or changing characters in transit
    corrupted_bytes = encrypted_bytes.replace(b"a", b"z")
    
    # GCM auth tag check must raise a ValueError during verification
    with pytest.raises(ValueError):
        decrypt_packet(corrupted_bytes)

def test_anti_replay_attack_temporal_window_validation():
    """Verifies that old packets recorded and re-sent by an adversary are dropped instantly."""
    mock_payload = {"sender": "Command_Post", "message": "Execute retreat order."}
    encrypted_bytes = encrypt_packet(mock_payload)
    
    # Simulate an adversary waiting out the clock skew window (61 seconds) before replaying the packet
    print("\n⏳ Simulating an adversarial time delay... (Mocking clock drift block)")
    
    # To avoid stalling a live unit test execution run for 61 real seconds, 
    # we can intercept the encrypted packet and manually alter its inner encrypted timestamp 
    # using structural injection, or we can use pytest monkeypatch to warp time.
    # Here, we test the code's time exception directly:
    import json
    from base64 import b64decode, b64encode
    
    packet_dict = json.loads(encrypted_bytes.decode('utf-8'))
    nonce = b64decode(packet_dict["nonce"])
    ciphertext = b64decode(packet_dict["ciphertext"])
    tag = b64decode(packet_dict["tag"])
    
    # Force initialize the decrypt module inside a modified custom test container 
    # to confirm that an old tx timestamp triggers PermissionError.
    from config import get_secure_crypto_key
    cipher = AES.new(get_secure_crypto_key(), AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
    payload = json.loads(decrypted_data.decode('utf-8'))
    
    # Force warp the transmission packet timestamp back by 5 minutes to simulate a classic replay
    payload["_tx_timestamp"] = time.time() - 300
    
    # Re-encrypt it with the old backdated time to trick the gateway
    cipher_new = AES.new(get_secure_crypto_key(), AES.MODE_GCM)
    c_text, t_tag = cipher_new.encrypt_and_digest(json.dumps(payload).encode('utf-8'))
    backdated_packet = json.dumps({
        "nonce": b64encode(cipher_new.nonce).decode('utf-8'),
        "ciphertext": b64encode(c_text).decode('utf-8'),
        "tag": b64encode(t_tag).decode('utf-8')
    }).encode('utf-8')
    
    # The gateway processing pipe must catch the backdate and throw a PermissionError
    with pytest.raises(PermissionError, match="Security alert: Packet rejected due to temporal skew"):
        decrypt_packet(backdated_packet)
