import os

# Network Topography Parameters
LOCAL_HOST = "127.0.0.1"
RELAY_LISTEN_PORT = 5002
GATEWAY_LISTEN_PORT = 5003

# Storage Assets
DB_FILE = "tactical_intel_cache.db"

# Clock drift limits for replay verification
MAX_CLOCK_SKEW_SECONDS = 60

def get_secure_crypto_key() -> bytes:
    """Fetches the 32-byte master cryptosystem secret from the local scope environment."""
    key_str = os.environ.get("TACTICAL_SHARED_KEY", "FallbackDefaultKey32BytesLong!!!")
    return key_str.encode('utf-8')[:32].ljust(32, b'\x00')
