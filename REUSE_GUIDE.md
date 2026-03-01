# Code Reuse Guide from AIForall Project

## Overview
This guide helps you identify and reuse relevant code from your AIForall project for the URE MVP.

## What to Look For in AIForall Folder

### 1. Agent Implementation Files
Look for Python files that contain agent logic:

**Files to find:**
- `agent.py` or `*_agent.py` - Main agent class implementations
- `tools.py` or `*_tools.py` - Tool/function definitions for agents
- `prompts.py` or `*_prompts.py` - System prompts and instructions
- `config.py` or `settings.py` - Configuration management

**What to copy:**
```
AIForall/
├── agents/
│   ├── base_agent.py          → Copy to: src/agents/base_agent.py
│   ├── agent_tools.py          → Copy to: src/agents/tools.py
│   └── agent_config.py         → Copy to: src/config/agent_config.py
```

### 2. Strands Agents SDK Usage Patterns
Look for how agents are created using strands-agents:

**Key patterns to identify:**
```python
# Pattern 1: Agent initialization
from strands import Agent

agent = Agent(
    name="AgentName",
    model="anthropic.claude-3-sonnet",
    instructions="System prompt...",
    tools=[tool1, tool2]
)

# Pattern 2: Tool definitions
def my_tool(param1: str, param2: int) -> dict:
    """Tool description"""
    # Implementation
    return result

# Pattern 3: Agent execution
response = agent.run("User query")
```

### 3. MCP Client Integration
Look for MCP (Model Context Protocol) client usage:

**Files to find:**
- `mcp_client.py` - MCP client wrapper
- `mcp_tools.py` - MCP tool registry
- `mcp_config.json` - MCP server configurations

**What to adapt:**
- MCP client initialization code
- Tool registration patterns
- Error handling for MCP calls

### 4. AWS Integration Code
Look for boto3 usage patterns:

**Files to find:**
- `aws_utils.py` - AWS helper functions
- `s3_handler.py` - S3 operations
- `dynamodb_handler.py` - DynamoDB operations
- `bedrock_client.py` - Bedrock API calls

### 5. Streamlit UI Components
Look for Streamlit app structure:

**Files to find:**
- `app.py` or `main.py` - Main Streamlit app
- `components/*.py` - Reusable UI components
- `pages/*.py` - Multi-page app structure

**What to reuse:**
- Chat interface patterns
- File upload handlers
- Session state management
- UI layout components

### 6. Utility Functions
Look for helper functions:

**Files to find:**
- `utils.py` - General utilities
- `data_processing.py` - Data manipulation
- `validators.py` - Input validation
- `formatters.py` - Output formatting

## Step-by-Step Reuse Process

### Step 1: Create Target Directory Structure
```bash
# In your current workspace
mkdir -p src/agents
mkdir -p src/tools
mkdir -p src/config
mkdir -p src/utils
mkdir -p src/ui
mkdir -p src/aws
```

### Step 2: Identify Key Files
In the AIForall folder, look for:
1. Main agent implementation (highest priority)
2. Tool definitions used by agents
3. Configuration files
4. Utility functions

### Step 3: Copy Specific Files
Instead of copying everything, copy only these file types:
- `*.py` files related to agents
- `config.yaml` or `config.json`
- `.env.example` (if exists)
- `requirements.txt` (to compare dependencies)

### Step 4: Adaptation Checklist

For each copied file, update:
- [ ] Import statements (adjust paths)
- [ ] Configuration values (AWS regions, model names)
- [ ] Environment variable names
- [ ] Function/class names to match URE naming
- [ ] Remove unused dependencies

## URE MVP Agent Mapping

Map AIForall agents to URE agents:

| AIForall Agent | URE MVP Agent | Purpose |
|----------------|---------------|---------|
| Your existing agent | Agri-Expert | Crop disease diagnosis, recommendations |
| Your existing agent | Resource-Optimizer | Irrigation, fertilizer optimization |

## Key Code Patterns to Reuse

### Pattern 1: Agent Base Class
```python
# From AIForall - adapt this pattern
class BaseAgent:
    def __init__(self, name, model, instructions):
        self.agent = Agent(
            name=name,
            model=model,
            instructions=instructions
        )
    
    def run(self, query):
        return self.agent.run(query)
```

### Pattern 2: Tool Registration
```python
# From AIForall - adapt this pattern
def register_tools(agent):
    tools = [
        tool1,
        tool2,
        tool3
    ]
    agent.tools = tools
```

### Pattern 3: MCP Integration
```python
# From AIForall - adapt this pattern
from mcp import Client

mcp_client = Client(server_url="...")
result = mcp_client.call_tool("tool_name", params)
```

## What NOT to Copy

❌ Don't copy:
- Large data files
- Model weights or embeddings
- API keys or credentials
- Virtual environment folders
- `__pycache__` directories
- `.git` folders
- Log files

## Quick Start: Minimal Files to Copy

If you want to start quickly, copy only these 3-5 files:
1. **Main agent file** - Shows agent initialization
2. **Tools file** - Shows tool definitions
3. **Config file** - Shows configuration structure
4. **Utils file** - Shows helper functions
5. **App file** (if Streamlit) - Shows UI structure

## Next Steps After Copying

1. **Review the code** - Understand the patterns used
2. **Update imports** - Fix any broken import paths
3. **Test individually** - Test each component separately
4. **Integrate gradually** - Add one component at a time
5. **Document changes** - Note what you adapted and why

## Need Help?

After you've copied specific files, I can help you:
- Adapt the code for URE MVP
- Fix import issues
- Integrate with existing code
- Optimize for your use case

---

**Remember**: Copy only what you need, not everything. Start with agent implementation patterns and build from there.
