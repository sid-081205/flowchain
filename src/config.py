import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Identity & Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEO_WIF = os.getenv("NEO_WIF")
TURNKEY_SIGN_WITH = os.getenv("TURNKEY_SIGN_WITH")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Critical Infrastructure
COLD_STORAGE_ADDRESS = os.getenv("COLD_STORAGE_ADDRESS")
NEO_RPC_URL = os.getenv("NEO_RPC_URL", "https://testnet1.neo.coz.io:443")
USE_MOCK_WALLET = os.getenv("USE_MOCK_WALLET", "false").lower() == "true"

# Validation
if not COLD_STORAGE_ADDRESS:
    print("WARNING: COLD_STORAGE_ADDRESS is not set. Killswitch will not function.")

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "false").lower() == "true"
