"""
Turnkey Agent Demo - AI-powered secure blockchain operations

This demo shows how to use an AI agent to perform Turnkey operations:
- Sign transactions (single and batch)
- Message and EIP-712 signing
- Wallet and account management
- Activity monitoring and audit
- Complete transaction workflows

The agent automatically handles:
- Multi-account discovery
- Batch operations
- Gas optimization
- Error handling and troubleshooting

All test data is embedded for easy demonstration.

Usage:
    python examples/turnkey-agent-demo.py
"""

import asyncio
import os
import time
from typing import List
from dotenv import load_dotenv

from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot
from pydantic import Field

load_dotenv()

# Import Turnkey tools
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
except ImportError:
    # Fallback/Mock for analysis if package missing
    print("Warning: spoon_ai.tools.turnkey_tools not found. Using mocks.")
    class BaseMockTool:
        def __init__(self, *args, **kwargs): pass
    SignEVMTransactionTool = BaseMockTool
    SignMessageTool = BaseMockTool
    SignTypedDataTool = BaseMockTool
    BroadcastTransactionTool = BaseMockTool
    BuildUnsignedEIP1559TxTool = BaseMockTool
    CompleteTransactionWorkflowTool = BaseMockTool
    ListWalletsTool = BaseMockTool
    ListWalletAccountsTool = BaseMockTool
    ListAllAccountsTool = BaseMockTool
    GetWalletTool = BaseMockTool
    CreateWalletTool = BaseMockTool
    CreateWalletAccountsTool = BaseMockTool
    BatchSignTransactionsTool = BaseMockTool
    GetActivityTool = BaseMockTool
    ListActivitiesTool = BaseMockTool
    WhoAmITool = BaseMockTool


class TurnkeyAgentDemo:
    """Turnkey Agent-based comprehensive demonstration"""

    # Embedded test data with all configurations
    TEST_DATA = {
        "network": "sepolia",
        "chain_id": 11155111,
        "rpc_url": "https://1rpc.io/sepolia",
        "explorer": "https://sepolia.etherscan.io",
        
        # Transaction templates
        "transaction_templates": {
            "simple_transfer": {
                "description": "Simple ETH transfer",
                "value_wei": "10000000000000000",  # 0.01 ETH
                "data_hex": "0x",
                "gas_limit": "21000"
            }
        },
        
        # EIP-712 templates
        "eip712_templates": {
            "simple_mail": {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                    ],
                    "Mail": [
                        {"name": "contents", "type": "string"}
                    ],
                },
                "primaryType": "Mail",
                "domain": {"name": "Turnkey", "version": "1", "chainId": 11155111},
                "message": {"contents": "Hello from Turnkey Agent Demo"},
            },
            "permit": {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                        {"name": "verifyingContract", "type": "address"}
                    ],
                    "Permit": [
                        {"name": "owner", "type": "address"},
                        {"name": "spender", "type": "address"},
                        {"name": "value", "type": "uint256"},
                        {"name": "nonce", "type": "uint256"},
                        {"name": "deadline", "type": "uint256"}
                    ]
                },
                "primaryType": "Permit",
                "domain": {
                    "name": "Test Token",
                    "version": "1",
                    "chainId": 11155111,
                    "verifyingContract": "0x1234567890123456789012345678901234567890"
                },
                "message": {
                    "owner": "0x6B02D710B27bEB57156898d778079016404BEDC3",
                    "spender": "0x1234567890123456789012345678901234567890",
                    "value": "1000000000000000000",
                    "nonce": 0,
                    "deadline": 1735689600
                }
            }
        },
        
        # Message signing templates
        "message_templates": {
            "authentication": "Sign in to DApp at 2025-10-22",
            "order": "Sell 1.5 ETH at 2500 USDC - Order #12345",
            "simple": "Hello Turnkey Trading Agent"
        },
        
        # Batch operation settings
        "batch_settings": {
            "max_accounts": 3,
            "default_value_wei": "1000000000000000",  # 0.001 ETH
            "enable_broadcast": False
        },
        
        # Wallet configuration templates
        "wallet_templates": {
            "ethereum_wallet": {
                "accounts": [{
                    "curve": "CURVE_SECP256K1",
                    "pathFormat": "PATH_FORMAT_BIP32",
                    "path": "m/44'/60'/0'/0/0",
                    "addressFormat": "ADDRESS_FORMAT_ETHEREUM"
                }],
                "mnemonic_length": 24
            },
            "multi_account_wallet": {
                "accounts": [
                    {
                        "curve": "CURVE_SECP256K1",
                        "pathFormat": "PATH_FORMAT_BIP32",
                        "path": f"m/44'/60'/0'/0/{i}",
                        "addressFormat": "ADDRESS_FORMAT_ETHEREUM"
                    } for i in range(3)
                ],
                "mnemonic_length": 24
            }
        }
    }

    def __init__(self):
        """Initialize the demo with embedded test data"""
        self.load_test_data()
        self.agents = {}

    def load_test_data(self):
        """Load test data from embedded TEST_DATA configuration"""
        try:
            data = self.TEST_DATA
            
            # Load basic configuration
            self.network = data.get("network", "sepolia")
            self.chain_id = data.get("chain_id", 11155111)
            self.rpc_url = data.get("rpc_url", "")
            self.explorer = data.get("explorer", "")
            
            # Load transaction templates
            self.transaction_templates = data.get("transaction_templates", {})
            
            # Load EIP-712 templates
            self.eip712_templates = data.get("eip712_templates", {})
            
            # Load message templates
            self.message_templates = data.get("message_templates", {})
            
            # Load batch settings
            self.batch_settings = data.get("batch_settings", {})
            
            # Load wallet templates
            self.wallet_templates = data.get("wallet_templates", {})
            
            print(f"✅ Loaded test data from embedded configuration")
            print(f"   Network: {self.network} (Chain ID: {self.chain_id})")
            print(f"   RPC URL: {self.rpc_url}")
            print(f"   Explorer: {self.explorer}")
            print(f"   Transaction Templates: {len(self.transaction_templates)}")
            print(f"   EIP-712 Templates: {len(self.eip712_templates)}")
            print(f"   Message Templates: {len(self.message_templates)}")
            
        except Exception as e:
            print(f"❌ Failed to load test data: {e}")
            # Set minimal defaults
            self.network = "sepolia"
            self.chain_id = 11155111
            self.rpc_url = "https://1rpc.io/sepolia"
            self.explorer = "https://sepolia.etherscan.io"
            self.transaction_templates = {}
            self.eip712_templates = {}
            self.message_templates = {}
            self.batch_settings = {}
            self.wallet_templates = {}

    def create_agent(self, name: str, tools: List, description: str) -> ToolCallAgent:
        """Create a specialized agent with specific tools"""
        
        network = self.network
        chain_id = self.chain_id
        rpc_url = self.rpc_url
        
        class TurnkeySpecializedAgent(ToolCallAgent):
            agent_name: str = name
            agent_description: str = description
            system_prompt: str = f"""
        You are a Turnkey secure blockchain specialist focused on {description}.

        **Environment Configuration:**
        - Network: {network} (Chain ID: {chain_id})
        - RPC URL: {rpc_url}

        **Key Operations and Best Practices:**

        1. **Transaction Workflow**:
        - Build unsigned tx → Sign with Turnkey → Optionally broadcast
        - Use complete_transaction_workflow for end-to-end operations
        - Always check account balance before broadcasting

        2. **Batch Operations**:
        - Use batch_sign_transactions for multi-account operations
        - Automatically discovers all organization accounts
        - Control with max_accounts and enable_broadcast parameters

        3. **Account Management**:
        - list_all_accounts: Discover all accounts across wallets
        - list_wallets: Get all wallets
        - create_wallet: Create new wallets dynamically

        4. **Signing Operations**:
        - sign_evm_transaction: Sign prepared transactions
        - sign_message: Sign arbitrary messages (authentication, orders)
        - sign_typed_data: Sign EIP-712 structured data (permits, approvals)

        5. **Security Best Practices**:
        - Never expose private keys
        - Verify transaction details before signing
        - Monitor activity logs for security
        - Test on testnet before mainnet

        **Tool Usage Examples:**

        - Complete workflow: complete_transaction_workflow(sign_with="0x...", to_address="0x...", value_wei="1000000", enable_broadcast=false)
        - Batch operations: batch_sign_transactions(to_address="0x...", value_wei="1000000", max_accounts="3", enable_broadcast=false)
        - Account discovery: list_all_accounts()

        Provide clear, informative responses based on the tool results.
        Always explain security implications and best practices.
        """
            max_steps: int = 20
            available_tools: ToolManager = Field(default_factory=lambda: ToolManager(tools))
        
        # NOTE: Refactored needed here: ChatBot setup is dependent on user's env
        llm_instance = ChatBot(llm_provider="openai", model_name="gpt-4o") # Using gpt-4o as prompt suggests, or env default

        agent = TurnkeySpecializedAgent(llm=llm_instance)
        return agent

    def setup_agents(self):
        """Setup specialized agents for different Turnkey operations"""
        
        # Secure Signing Agent (4 tools)
        signing_tools = [
            ListAllAccountsTool(),  # Add this tool to get account addresses
            SignEVMTransactionTool(),
            SignMessageTool(),
            SignTypedDataTool(),
        ]
        self.agents['signing'] = self.create_agent(
            "Secure Signing Specialist",
            signing_tools,
            "Expert in secure transaction and message signing using Turnkey"
        )
        
        # Transaction Manager Agent (4 tools)
        transaction_tools = [
            BuildUnsignedEIP1559TxTool(),
            SignEVMTransactionTool(),
            BroadcastTransactionTool(),
            CompleteTransactionWorkflowTool(),
        ]
        self.agents['transaction'] = self.create_agent(
            "Transaction Manager",
            transaction_tools,
            "Specialist in building, signing, and broadcasting blockchain transactions"
        )
        
        # Account Manager Agent (6 tools)
        account_tools = [
            ListWalletsTool(),
            ListWalletAccountsTool(),
            ListAllAccountsTool(),
            GetWalletTool(),
            CreateWalletTool(),
            CreateWalletAccountsTool(),
        ]
        self.agents['account'] = self.create_agent(
            "Account Manager",
            account_tools,
            "Expert in managing Turnkey wallets and accounts"
        )
        
        # Batch Operations Agent (4 tools)
        batch_tools = [
            ListAllAccountsTool(),
            BatchSignTransactionsTool(),
            SignMessageTool(),
            SignTypedDataTool(),
        ]
        self.agents['batch'] = self.create_agent(
            "Batch Operations Manager",
            batch_tools,
            "Specialist in multi-account batch operations and parallel signing"
        )
        
        # Activity Monitor Agent (3 tools: GetActivityTool, ListActivitiesTool, WhoAmITool)
        monitor_tools = [
            GetActivityTool(),      # Get specific activity details by ID
            ListActivitiesTool(),   # List recent activities with pagination
            WhoAmITool(),           # Get organization information
        ]
        self.agents['monitor'] = self.create_agent(
            "Activity Monitor",
            monitor_tools,
            "Expert in monitoring Turnkey activities and organization status"
        )

    # ... [Rest of method implementations would be here, but for brevity in saving, we will rely on the Refactor step to implement the reusable logic] ...

# ... [The rest of the file is the "demo" driver code which we will likely replace with a cleaner interface] ...
