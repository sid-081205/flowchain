import sys
import os
import asyncio
from unittest.mock import MagicMock

# Mock neo3 before ANY imports occur
sys.modules["neo3"] = MagicMock()
sys.modules["neo3.core"] = MagicMock()
sys.modules["neo3.wallet"] = MagicMock()

# Determine project root
project_root = os.path.abspath(os.path.join(os.getcwd()))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import project modules
from src import config
# Mock API key if missing to allow initialization to proceed
if not config.GEMINI_API_KEY:
    config.GEMINI_API_KEY = "mock_key_for_testing"

# Import main and server
try:
    from src.main import main as app_main, FlowChainAgent
    from src.server import initialize_agent as server_init_agent
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

async def test_startup():
    print("Testing src/main.py startup...")
    # initializing agent wrapper
    try:
        from src.tools.market import MarketAnalyst
        market = MarketAnalyst(llm_provider="gemini", model_name="gemini-flash")
        print("✅ MarketAnalyst initialized")
    except Exception as e:
         print(f"❌ MarketAnalyst init failed: {e}")

    try:
        from src.tools.neofs import NeoFSManager
        neofs = NeoFSManager(llm_provider="gemini", model_name="gemini-flash")
        print(f"✅ NeoFSManager initialized (Tools: {len(neofs.tools)})")
    except Exception as e:
        print(f"❌ NeoFSManager init failed: {e}")

    print("Testing src/server.py agent initialization...")
    try:
        agent = await server_init_agent()
        print(f"✅ Server Agent initialized: {agent.name}")
    except Exception as e:
        print(f"❌ Server Agent init failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_startup())
