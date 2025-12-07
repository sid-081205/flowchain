import sys
import os
from typing import List
from dotenv import load_dotenv

from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot

try:
    from spoon_ai.tools.turnkey_tools import (
        SignEVMTransactionTool,
        SignMessageTool,
        SignTypedDataTool,
        BroadcastTransactionTool,
        BuildUnsignedEIP1559TxTool,
        CompleteTransactionWorkflowTool,
        ListWalletsTool,
        ListWalletAccountsTool,
        ListAllAccountsTool,
        GetWalletTool,
        CreateWalletTool,
        CreateWalletAccountsTool,
        BatchSignTransactionsTool,
        GetActivityTool,
        ListActivitiesTool,
        WhoAmITool,
    )
    HAS_TURNKEY_TOOLS = True
except ImportError as e:
    print(f"[WARNING] Failed to import Turnkey tools: {e}")
    HAS_TURNKEY_TOOLS = False

load_dotenv()

class TurnkeyWalletManager:
    """Manager for Turnkey secure wallet operations."""

    def __init__(self, llm_provider="openrouter", model_name="openai/gpt-4o"):
        if HAS_TURNKEY_TOOLS:
            self.tools = [
                SignEVMTransactionTool(),
                SignMessageTool(),
                SignTypedDataTool(),
                BroadcastTransactionTool(),
                BuildUnsignedEIP1559TxTool(),
                CompleteTransactionWorkflowTool(),
                ListWalletsTool(),
                ListWalletAccountsTool(),
                ListAllAccountsTool(),
                GetWalletTool(),
                CreateWalletTool(),
                CreateWalletAccountsTool(),
                BatchSignTransactionsTool(),
                GetActivityTool(),
                ListActivitiesTool(),
                WhoAmITool(),
            ]
        else:
            self.tools = []
        
        self.network = os.getenv("TURNKEY_NETWORK", "sepolia")
        
        self.agent = ToolCallAgent(
            llm=ChatBot(
                llm_provider=llm_provider,
                model_name=model_name
            ),
            available_tools=ToolManager(self.tools),
            system_prompt=f"""
            You are a Turnkey secure wallet assistant.
            Network: {self.network}
            
            You can help with:
            - Managed Wallets (creation, listing)
            - Signing Transactions (EVM, messages)
            - Activities & Monitoring
            
            Security:
            - Never output private keys (you don't have access to them anyway).
            - Always confirm important details before signing.
            """
        )

    async def run(self, query: str) -> str:
        """Run a query against the Turnkey agent."""
        try:
            return await self.agent.run(query)
        except Exception as e:
            return f"Turnkey Operation Failed: {str(e)}"
