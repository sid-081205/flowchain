import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Identity & Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO_WIF = os.getenv("NEO_WIF")
TURNKEY_API_KEY = os.getenv("TURNKEY_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Critical Infrastructure
COLD_STORAGE_ADDRESS = os.getenv("COLD_STORAGE_ADDRESS")
NEO_RPC_URL = os.getenv("NEO_RPC_URL", "https://testnet1.neo.coz.io:443")

# Voice IDs
VOICE_ID_RACHEL_CALM = "21m00Tcm4TlvDq8ikWAM"
VOICE_ID_CLYDE_URGENT = "2EiwWnXFnvU5JabPnv8n"

# Validation
if not COLD_STORAGE_ADDRESS:
    print("WARNING: COLD_STORAGE_ADDRESS is not set. Killswitch will not function.")

if not NEO_WIF:
    print("WARNING: NEO_WIF is not set. Wallet operations may fail.")
