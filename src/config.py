import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Identity & Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO_WIF = os.getenv("NEO_WIF")
NEO_RPC_URL = os.getenv("NEO_RPC_URL", "https://testnet1.neo.coz.io:443")

# Turnkey (Agent Wallet)
TURNKEY_API_KEY = os.getenv("TURNKEY_API_KEY") # Not fully used yet, but good to have

# Voice (Future)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Validation
if not NEO_WIF:
    print("WARNING: NEO_WIF is not set. Wallet operations will fail.")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. LLM operations will fail.")
