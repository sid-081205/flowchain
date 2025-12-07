import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Identity & Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEO_WIF = os.getenv("NEO_WIF")
TURNKEY_SIGN_WITH = os.getenv("TURNKEY_SIGN_WITH")
TURNKEY_API_KEY = os.getenv("TURNKEY_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Neo Blockchain Configuration
NEO_RPC_URL = os.getenv("NEO_RPC_URL", "https://testnet1.neo.coz.io:443")
NEO_NETWORK = os.getenv("NEO_NETWORK", "testnet")  # mainnet or testnet
USE_MOCK_WALLET = os.getenv("USE_MOCK_WALLET", "false").lower() == "true"

# Critical Infrastructure
COLD_STORAGE_ADDRESS = os.getenv("COLD_STORAGE_ADDRESS")

# Application Settings
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "false").lower() == "true"
USE_TURNKEY_SIGNING = os.getenv("USE_TURNKEY_SIGNING", "true").lower() == "true"
