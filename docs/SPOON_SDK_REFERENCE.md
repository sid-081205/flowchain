# SpoonOS SDK Reference (Verified)

**Source**: `spoonos_components/` (Cloned from GitHub)

## 1. Core Agent (`spoon_ai`)

### `ToolCallAgent` (The Agent)
Path: `spoon_ai.agents.toolcall`

```python
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager

# Initialization
agent = ToolCallAgent(
    llm=ChatBot(
        llm_provider="openai",
        model_name="gpt-4o",
        api_key="your-key-here" # OR load via env var OPENAI_API_KEY
    ),
    available_tools=ToolManager([MyTool()]),
    agent_name="Name",
    agent_description="Desc",
    system_prompt="Prompt..."
)

# Execution
await agent.run("User query...")
```

### `BaseTool`
Path: `spoon_ai.tools.base`

**Crucial**: Subclasses must implement `execute`, not `run`.

```python
from spoon_ai.tools.base import BaseTool
from pydantic import Field

class MyTool(BaseTool):
    name = "my_tool"
    description = "does something"
    
    async def execute(self, arg1: str):
        return "result"
```

## 2. Directory Structure
```
/
├── spoonos_components/  # The cloned SDK
├── src/
│   ├── main.py
│   └── tools/
│       └── neo_tool.py  # Custom Neo Tool
```
