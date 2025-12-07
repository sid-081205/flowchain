import sys
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv



# Mock neo3 if not available to allow server startup
try:
    import neo3
except ImportError:
    from unittest.mock import MagicMock
    import sys
    sys.modules["neo3"] = MagicMock()
    sys.modules["neo3.core"] = MagicMock()
    sys.modules["neo3.wallet"] = MagicMock()

from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot
from spoon_ai.schema import Message

# Import experimental tools - handle failures gracefully
try:
    from spoon_ai.tools.neofs_tools import (
        CreateBearerTokenTool,
        CreateContainerTool,
        UploadObjectTool,
        DownloadObjectByIdTool,
        GetObjectHeaderByIdTool,
        DownloadObjectByAttributeTool,
        GetObjectHeaderByAttributeTool,
        DeleteObjectTool,
        SearchObjectsTool,
        SetContainerEaclTool,
        GetContainerEaclTool,
        ListContainersTool,
        GetContainerInfoTool,
        DeleteContainerTool,
        GetNetworkInfoTool
    )
    HAS_NEOFS_TOOLS = True
except ImportError as e:
    print(f"[WARNING] Failed to import NeoFS tools: {e}")
    HAS_NEOFS_TOOLS = False

load_dotenv()

class NeoFSManager:
    """Manager for NeoFS operations using SpoonAI tools."""
    
    def __init__(self, llm_provider="openrouter", model_name="openai/gpt-4o"):
        if HAS_NEOFS_TOOLS:
            self.tools = [
                CreateBearerTokenTool(),
                CreateContainerTool(),
                UploadObjectTool(),
                SetContainerEaclTool(),
                GetContainerEaclTool(),
                ListContainersTool(),
                GetContainerInfoTool(),
                DeleteContainerTool(),
                GetNetworkInfoTool(),
                DownloadObjectByIdTool(),
                DownloadObjectByAttributeTool(),
                DeleteObjectTool(),
                SearchObjectsTool(),
            ]
        else:
            self.tools = []
        
        self.agent = ToolCallAgent(
            llm=ChatBot(
                llm_provider=llm_provider,
                model_name=model_name
            ),
            available_tools=ToolManager(self.tools),
            system_prompt="""
            You are a NeoFS storage specialist.
            
            CRITICAL - Bearer Token Management:
            - Most operations require a specific bearer token.
            - Create the appropriate token before performing the operation.
            - For PUBLIC containers, no token is needed for upload/download.
            - For PRIVATE/eACL containers, you MUST create a token first.
            
            When asked to upload or store files:
            1. Check if a container exists or create one.
            2. Handle token creation if needed.
            3. Upload the file.
            
            Always return the result of your operation concisely.
            """
        )

    async def run(self, query: str) -> str:
        """Run a query against the NeoFS agent."""
        try:
            return await self.agent.run(query)
        except Exception as e:
            return f"NeoFS Operation Failed: {str(e)}"
