# URE Agents

Multi-agent system for the Unified Rural Ecosystem (URE) MVP.

## Architecture

```
Supervisor Agent (Orchestrator)
    ├── Agri-Expert Agent (Disease diagnosis, market prices)
    ├── Policy-Navigator Agent (PM-Kisan eligibility)
    └── Resource-Optimizer Agent (Irrigation recommendations)
```

## Agents

### 1. Supervisor Agent
- **File**: `supervisor.py`
- **Role**: Main orchestrator that routes queries to specialist agents
- **Model**: Amazon Nova Pro (us.amazon.nova-pro-v1:0)
- **Temperature**: 0.3
- **Tools**: All 3 specialist agents

### 2. Agri-Expert Agent
- **File**: `agri_expert.py`
- **Role**: Crop disease diagnosis and market price information
- **Model**: Amazon Nova Pro
- **Temperature**: 0.3
- **Tools**: http_request (for API calls)
- **Capabilities**:
  - Disease identification from symptoms
  - Treatment recommendations (organic & chemical)
  - Market price information
  - Pest management advice

### 3. Policy-Navigator Agent
- **File**: `policy_navigator.py`
- **Role**: Government scheme eligibility and guidance
- **Model**: Amazon Nova Pro
- **Temperature**: 0.2 (more precise for rules)
- **Tools**: None (uses Bedrock KB via Lambda)
- **Capabilities**:
  - PM-Kisan eligibility checking
  - Subsidy information
  - Application guidance
  - Documentation requirements

### 4. Resource-Optimizer Agent
- **File**: `resource_optimizer.py`
- **Role**: Irrigation and water management recommendations
- **Model**: Amazon Nova Pro
- **Temperature**: 0.3
- **Tools**: http_request (for weather APIs)
- **Capabilities**:
  - Evapotranspiration calculations
  - Soil moisture analysis
  - Irrigation scheduling
  - Pump optimization
  - Weather-based recommendations

## Usage

### Individual Agent Testing

```python
from agents import agri_expert_agent, policy_navigator_agent, resource_optimizer_agent

# Test Agri-Expert
response = agri_expert_agent("What are the symptoms of tomato blight?")
print(response)

# Test Policy-Navigator
response = policy_navigator_agent("Am I eligible for PM-Kisan?")
print(response)

# Test Resource-Optimizer
response = resource_optimizer_agent("When should I irrigate my wheat?")
print(response)
```

### Supervisor Agent (Recommended)

```python
from agents import supervisor_agent

# Supervisor automatically routes to the right specialist
response = supervisor_agent("My wheat has yellow spots")
print(response)
```

### Interactive Mode

```bash
# Activate virtual environment
source rural/bin/activate  # Linux/Mac
rural\Scripts\activate     # Windows

# Run supervisor in interactive mode
python src/agents/supervisor.py
```

## Configuration

Agent configuration is centralized in `src/config/agent_config.py`:

- Model IDs
- Temperature settings
- MCP server URLs
- AWS resource names
- Timeout values

## Environment Variables

Required environment variables (see `.env.example`):

```bash
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
AWS_REGION=ap-south-1
MCP_AGMARKNET_SERVER_URL=http://localhost:8001
MCP_WEATHER_SERVER_URL=http://localhost:8002
```

## Testing

Run the test script:

```bash
python test_agents.py
```

## Next Steps

1. Integrate MCP Client with agents for external API calls
2. Add Bedrock Knowledge Base integration for Policy-Navigator
3. Implement image analysis for Agri-Expert
4. Create Lambda handler to orchestrate agents
5. Build Streamlit UI for user interaction
