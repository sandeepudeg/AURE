# MVP Design Document: Unified Rural Ecosystem (URE)

## Overview

The MVP Design Document outlines the technical architecture and implementation details for the Minimum Viable Product of URE. This design focuses on delivering core multi-agent functionality for a pilot village with 50+ farmers using a simplified tech stack and single-village scope.

**MVP Scope**:
- Single village pilot (Nashik, Maharashtra)
- 3 specialist agents (Agri-Expert, Policy-Navigator, Resource-Optimizer)
- Web interface only (Streamlit)
- Single government scheme (PM-Kisan)
- Basic irrigation recommendations
- 50-100 concurrent users

**Design Principles**:
- **Simplicity**: Minimal components, maximum functionality
- **Cost-Effectiveness**: Serverless architecture, on-demand pricing
- **Reliability**: Bedrock Guardrails for safety, official data grounding
- **Scalability**: Can scale to 1000+ users with minimal changes
- **Maintainability**: Clear separation of concerns, modular agents

---

## MVP Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB APP (MVP)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Input: Text Query or Image Upload                       │  │
│  │  Display: Agent Response + Conversation History          │  │
│  │  Language: Hindi/Marathi Toggle                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Amazon API Gateway
                    (Single POST /query endpoint)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              AWS Lambda (Python 3.9 - MVP)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Parse input (text or image URL)                       │  │
│  │ 2. Retrieve user context from DynamoDB                   │  │
│  │ 3. Initialize MCP Client                                 │  │
│  │ 4. Invoke Strands Supervisor Agent                       │  │
│  │ 5. Store response in DynamoDB                            │  │
│  │ 6. Return response to Streamlit                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MCP CLIENT (MVP)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ TASK: Route tool requests to MCP Servers                 │  │
│  │ COMPONENTS:                                               │  │
│  │  - Tool Registry: Metadata for available MCP tools       │  │
│  │  - Permission Manager: Verify agent tool access          │  │
│  │  - Request Router: Route to appropriate MCP Server       │  │
│  │  - Error Handler: Retry logic and fallback strategies    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ↙                                        ↘
    ┌─────────────────┐                  ┌─────────────────┐
    │ Agmarknet MCP   │                  │ Weather MCP     │
    │    Server       │                  │    Server       │
    │    (MVP)        │                  │    (MVP)        │
    └─────────────────┘                  └─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        Strands Supervisor Agent (Claude 3.5 Sonnet)             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ TASK: Classify query and route to specialist agent       │  │
│  │ INPUT: User query + conversation history                 │  │
│  │ OUTPUT: Routing decision + agent invocation              │  │
│  │ LOGIC:                                                    │  │
│  │  - IF image → route to Agri-Expert                       │  │
│  │  - IF scheme question → route to Policy-Navigator        │  │
│  │  - IF irrigation question → route to Resource-Optimizer  │  │
│  │  - IF complex → invoke multiple agents in parallel       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ↙                    ↓                    ↘
    ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
    │ Agri-Expert │   │Policy-Nav    │   │Resource-Optimizer│
    │   Agent     │   │   Agent      │   │     Agent        │
    │ (MVP)       │   │   (MVP)      │   │     (MVP)        │
    └─────────────┘   └──────────────┘   └──────────────────┘
         ↓                    ↓                    ↓
    ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
    │ Tools:      │   │ Tools:       │   │ Tools:           │
    │ - analyze   │   │ - search_    │   │ - calculate_     │
    │   _image    │   │   schemes    │   │   evapotrans     │
    │ - search_   │   │ - check_     │   │ - analyze_soil   │
    │   plant     │   │   eligibility│   │ - MCP: get_      │
    │   village   │   │ - get_scheme │   │   weather_       │
    │ - MCP: get_ │   │   _details   │   │   forecast       │
    │   mandi_    │   │              │   │ - MCP: get_      │
    │   prices    │   │              │   │   current_       │
    │ - MCP: get_ │   │              │   │   weather        │
    │   nearby_   │   │              │   │ - optimize_pump  │
    │   mandis    │   │              │   │   _schedule      │
    └─────────────┘   └──────────────┘   └──────────────────┘
         ↓                    ↓                    ↓
    ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
    │ Data:       │   │ Data:        │   │ Data:            │
    │ - S3 images │   │ - Bedrock KB │   │ - S3 sensor logs │
    │ - OpenSearch│   │ - DynamoDB   │   │ - MCP Weather    │
    │ - MCP       │   │ - PM-Kisan   │   │   Server         │
    │   Agmarknet │   │ - Eligibility│   │ - Python math    │
    │   Server    │   │              │   │ - Irrigation     │
    └─────────────┘   └──────────────┘   └──────────────────┘
                              ↓
                    Bedrock Guardrails
                    (Safety Validation)
                              ↓
                    Amazon Translate
                    (Hindi/Marathi)
                              ↓
                    Response to Streamlit
                              ↓
                    DynamoDB + CloudWatch
                    (Persistence & Logging)
```

### MVP Data Flow

```
1. USER INPUT
   ├─ Text query: "My wheat has yellow spots"
   ├─ Image upload: Leaf photo (JPG/PNG)
   └─ User ID: farmer_12345

2. STREAMLIT APP
   ├─ Validate input
   ├─ Upload image to S3 (if present)
   └─ Call API Gateway /query endpoint

3. API GATEWAY
   ├─ Route to Lambda
   └─ Pass input + user_id

4. LAMBDA FUNCTION
   ├─ Retrieve user context from DynamoDB
   │  └─ farm_size, crop_type, location, language
   ├─ Initialize MCP Client
   │  └─ Load Tool Registry and configure MCP Servers
   ├─ Prepare Supervisor Agent input
   └─ Invoke Strands Supervisor

5. SUPERVISOR AGENT
   ├─ Classify query type
   ├─ Route to specialist agent(s)
   └─ Wait for agent response(s)

6. SPECIALIST AGENT EXECUTION
   ├─ Agri-Expert (if image/disease query)
   │  ├─ Retrieve image from S3
   │  ├─ Search PlantVillage embeddings in OpenSearch
   │  ├─ Invoke Claude 3.5 Sonnet for analysis
   │  ├─ MCP Client → Agmarknet MCP Server (get_mandi_prices)
   │  └─ Return disease + treatment + price
   │
   ├─ Policy-Navigator (if scheme query)
   │  ├─ Search Bedrock Knowledge Base for PM-Kisan
   │  ├─ Check village eligibility in DynamoDB
   │  ├─ Assess farmer eligibility
   │  └─ Return scheme details + eligibility
   │
   └─ Resource-Optimizer (if irrigation query)
      ├─ Retrieve sensor data from S3
      ├─ MCP Client → Weather MCP Server (get_weather_forecast)
      ├─ Calculate Evapotranspiration (Python)
      ├─ Optimize pump schedule
      └─ Return irrigation recommendation

7. RESPONSE SYNTHESIS
   ├─ Supervisor combines agent outputs
   ├─ Apply Bedrock Guardrails (safety check)
   └─ Return synthesized response

8. LANGUAGE TRANSLATION
   ├─ Detect user language preference
   ├─ Translate response via Amazon Translate
   └─ Return in Hindi/Marathi

9. RESPONSE DELIVERY
   ├─ Lambda returns response to API Gateway
   ├─ Streamlit displays response
   └─ Show conversation history

10. PERSISTENCE
    ├─ Store conversation in DynamoDB
    ├─ Log to CloudWatch
    └─ Update user context
```

---

## MVP Components and Interfaces

### 1. Streamlit Web App (Frontend)

**Purpose**: Simple, user-friendly interface for farmers

**Features**:
- Text input box for queries
- Image upload button (JPG/PNG)
- Response display area
- Conversation history sidebar
- Language toggle (English/Hindi/Marathi)
- User profile section (farm size, crop type, location)

**Code Structure**:
```python
# streamlit_app.py
import streamlit as st
import requests
import json

st.set_page_config(page_title="Gram-Setu", layout="wide")

# Sidebar: User Profile
with st.sidebar:
    st.title("👨‍🌾 Your Profile")
    user_id = st.text_input("User ID", "farmer_12345")
    farm_size = st.number_input("Farm Size (acres)", 1, 100, 5)
    crop_type = st.selectbox("Crop Type", ["Wheat", "Cotton", "Rice", "Corn"])
    location = st.text_input("Village", "Nashik")
    language = st.selectbox("Language", ["English", "Hindi", "Marathi"])

# Main: Query Interface
st.title("🌾 Gram-Setu: Village Bridge AI")

# Text Query
query = st.text_area("Ask your question:", placeholder="e.g., My wheat has yellow spots")

# Image Upload
uploaded_image = st.file_uploader("Or upload a crop image:", type=["jpg", "png"])

# Submit Button
if st.button("Get Advice"):
    # Call Lambda via API Gateway
    response = requests.post(
        "https://api-gateway-url/query",
        json={
            "user_id": user_id,
            "query": query,
            "image_url": upload_to_s3(uploaded_image) if uploaded_image else None,
            "context": {
                "farm_size": farm_size,
                "crop_type": crop_type,
                "location": location,
                "language": language
            }
        }
    )
    
    # Display Response
    result = response.json()
    st.success(result["response"])
    
    # Show Conversation History
    st.subheader("Conversation History")
    for msg in result["history"]:
        st.write(f"**{msg['role']}**: {msg['content']}")
```

### 2. Lambda Function (Request Handler)

**Purpose**: Orchestrate request flow and manage state

**Responsibilities**:
- Parse incoming requests
- Retrieve user context from DynamoDB
- Invoke Strands Supervisor Agent
- Store responses in DynamoDB
- Handle errors and timeouts

**Code Structure**:
```python
# lambda_handler.py
import json
import boto3
from strands import Agent
from mcp_client import MCPClient
import logging

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')

logger = logging.getLogger()

def lambda_handler(event, context):
    """
    Main Lambda handler for URE MVP with MCP integration
    """
    try:
        # 1. Parse input
        body = json.loads(event['body'])
        user_id = body['user_id']
        query = body['query']
        image_url = body.get('image_url')
        user_context = body.get('context', {})
        
        # 2. Retrieve conversation history
        table = dynamodb.Table('ure-conversations')
        response = table.get_item(Key={'user_id': user_id})
        conversation_history = response.get('Item', {}).get('messages', [])
        
        # 3. Initialize MCP Client
        mcp_client = MCPClient(
            tool_registry_path='mcp_tool_registry.json',
            servers={
                'agmarknet': {'url': 'https://agmarknet-mcp-server.com'},
                'weather': {'url': 'https://weather-mcp-server.com'}
            }
        )
        
        # 4. Prepare Supervisor Agent input
        supervisor_input = {
            'query': query,
            'image_url': image_url,
            'conversation_history': conversation_history,
            'user_context': user_context,
            'mcp_client': mcp_client
        }
        
        # 5. Invoke Supervisor Agent
        supervisor = Agent(
            model='claude-3-5-sonnet',
            tools=[agri_expert_tool, policy_nav_tool, resource_opt_tool],
            mcp_client=mcp_client
        )
        
        agent_response = supervisor.run(supervisor_input)
        
        # 6. Apply Guardrails
        guardrails_response = apply_bedrock_guardrails(agent_response)
        
        # 7. Translate response
        translated_response = translate_response(
            guardrails_response,
            user_context.get('language', 'English')
        )
        
        # 8. Store in DynamoDB
        conversation_history.append({
            'role': 'user',
            'content': query,
            'timestamp': int(time.time())
        })
        conversation_history.append({
            'role': 'assistant',
            'content': translated_response,
            'timestamp': int(time.time())
        })
        
        table.put_item(Item={
            'user_id': user_id,
            'messages': conversation_history,
            'last_updated': int(time.time())
        })
        
        # 9. Return response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': translated_response,
                'history': conversation_history[-10:]  # Last 10 messages
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### 3. MCP Client (MVP)

**Purpose**: Standardize external service access through Model Context Protocol

**Responsibilities**:
- Manage MCP Tool Registry with metadata
- Route tool requests to appropriate MCP Servers
- Verify agent permissions before tool execution
- Handle errors with retry logic and fallback strategies
- Log all tool calls for audit and debugging

**Code Structure**:
```python
# mcp_client.py
import json
import requests
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger()

class MCPClient:
    """
    MCP Client for standardized external service access
    """
    
    def __init__(self, tool_registry_path: str, servers: Dict[str, Dict]):
        """
        Initialize MCP Client with tool registry and server configurations
        
        Args:
            tool_registry_path: Path to JSON file containing tool metadata
            servers: Dictionary of MCP server configurations
        """
        self.tool_registry = self._load_tool_registry(tool_registry_path)
        self.servers = servers
        self.cache = {}  # Simple in-memory cache for fallback
        
    def _load_tool_registry(self, path: str) -> Dict:
        """Load tool registry from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)
    
    def call_tool(self, tool_id: str, agent_role: str, params: Dict) -> Dict[str, Any]:
        """
        Call an MCP tool with permission checking and error handling
        
        Args:
            tool_id: Unique identifier for the tool
            agent_role: Role of the requesting agent (e.g., 'Agri-Expert')
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # 1. Validate tool exists in registry
            if tool_id not in self.tool_registry:
                logger.error(f"Tool {tool_id} not found in registry")
                return {
                    'success': False,
                    'error': f"Tool {tool_id} not found. Available tools: {list(self.tool_registry.keys())}"
                }
            
            tool_metadata = self.tool_registry[tool_id]
            
            # 2. Check agent permissions
            if agent_role not in tool_metadata['permissions']:
                logger.warning(f"Agent {agent_role} lacks permission for tool {tool_id}")
                return {
                    'success': False,
                    'error': f"Permission denied for tool {tool_id}"
                }
            
            # 3. Get MCP server configuration
            server_name = tool_metadata['server_name']
            if server_name not in self.servers:
                logger.error(f"MCP Server {server_name} not configured")
                return self._fallback_to_cache(tool_id, params)
            
            # 4. Call MCP server with retry logic
            result = self._call_with_retry(
                server_name=server_name,
                tool_id=tool_id,
                params=params,
                max_retries=3
            )
            
            # 5. Cache successful result
            if result['success']:
                self._cache_result(tool_id, params, result)
            
            # 6. Log tool call
            self._log_tool_call(tool_id, agent_role, params, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_id}: {str(e)}")
            return self._fallback_to_cache(tool_id, params)
    
    def _call_with_retry(self, server_name: str, tool_id: str, params: Dict, max_retries: int) -> Dict:
        """
        Call MCP server with exponential backoff retry logic
        """
        server_url = self.servers[server_name]['url']
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{server_url}/tools/{tool_id}",
                    json=params,
                    timeout=5
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'data': response.json(),
                        'source': 'mcp_server'
                    }
                else:
                    logger.warning(f"MCP Server returned {response.status_code}, attempt {attempt + 1}/{max_retries}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"MCP Server timeout, attempt {attempt + 1}/{max_retries}")
            except Exception as e:
                logger.error(f"MCP Server error: {str(e)}, attempt {attempt + 1}/{max_retries}")
            
            # Exponential backoff
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        # All retries failed
        return self._fallback_to_cache(tool_id, params)
    
    def _fallback_to_cache(self, tool_id: str, params: Dict) -> Dict:
        """
        Fallback to cached data when MCP server is unavailable
        """
        cache_key = f"{tool_id}:{json.dumps(params, sort_keys=True)}"
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            logger.info(f"Using cached data for {tool_id} (age: {time.time() - cached_data['timestamp']}s)")
            return {
                'success': True,
                'data': cached_data['result'],
                'source': 'cache',
                'warning': f"Data from cache (last updated: {cached_data['timestamp']})"
            }
        else:
            return {
                'success': False,
                'error': f"MCP Server unavailable and no cached data for {tool_id}"
            }
    
    def _cache_result(self, tool_id: str, params: Dict, result: Dict):
        """Cache successful tool call result"""
        cache_key = f"{tool_id}:{json.dumps(params, sort_keys=True)}"
        self.cache[cache_key] = {
            'result': result['data'],
            'timestamp': time.time()
        }
    
    def _log_tool_call(self, tool_id: str, agent_role: str, params: Dict, result: Dict):
        """Log tool call for audit and debugging"""
        logger.info(json.dumps({
            'event': 'mcp_tool_call',
            'tool_id': tool_id,
            'agent_role': agent_role,
            'params': params,
            'success': result['success'],
            'source': result.get('source', 'unknown'),
            'timestamp': time.time()
        }))
```

**MCP Tool Registry Structure** (`mcp_tool_registry.json`):
```json
{
  "get_mandi_prices": {
    "tool_id": "get_mandi_prices",
    "server_name": "agmarknet",
    "description": "Fetch current market prices for crops by location",
    "parameters_schema": {
      "type": "object",
      "properties": {
        "crop": {"type": "string", "description": "Crop name (e.g., wheat, cotton)"},
        "district": {"type": "string", "description": "District name"},
        "state": {"type": "string", "description": "State name"}
      },
      "required": ["crop", "district"]
    },
    "permissions": ["Agri-Expert", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3
  },
  "get_nearby_mandis": {
    "tool_id": "get_nearby_mandis",
    "server_name": "agmarknet",
    "description": "Discover nearby market locations",
    "parameters_schema": {
      "type": "object",
      "properties": {
        "district": {"type": "string", "description": "District name"},
        "radius_km": {"type": "number", "description": "Search radius in kilometers"}
      },
      "required": ["district"]
    },
    "permissions": ["Agri-Expert", "Supervisor"],
    "timeout_ms": 3000,
    "retry_count": 3
  },
  "get_current_weather": {
    "tool_id": "get_current_weather",
    "server_name": "weather",
    "description": "Retrieve real-time weather conditions",
    "parameters_schema": {
      "type": "object",
      "properties": {
        "location": {"type": "string", "description": "Location name"},
        "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
      },
      "required": ["location"]
    },
    "permissions": ["Resource-Optimizer", "Supervisor"],
    "timeout_ms": 3000,
    "retry_count": 3
  },
  "get_weather_forecast": {
    "tool_id": "get_weather_forecast",
    "server_name": "weather",
    "description": "Get weather forecasts for planning",
    "parameters_schema": {
      "type": "object",
      "properties": {
        "location": {"type": "string", "description": "Location name"},
        "days": {"type": "number", "description": "Number of forecast days", "default": 3}
      },
      "required": ["location"]
    },
    "permissions": ["Resource-Optimizer", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3
  }
}
```

### 4. Strands Supervisor Agent

**Purpose**: Orchestrate specialist agents

**System Prompt**:
```
You are the "Gram-Setu" (Village Bridge) AI Orchestrator for the MVP.

TASK: Analyze the farmer's query and route to the appropriate specialist agent.

AVAILABLE AGENTS:
1. Agri-Expert: For crop diseases, pests, market prices
2. Policy-Navigator: For PM-Kisan scheme eligibility
3. Resource-Optimizer: For irrigation and water management

ROUTING LOGIC:
- IF query contains image OR mentions disease/pest → Agri-Expert
- IF query mentions PM-Kisan, subsidy, scheme → Policy-Navigator
- IF query mentions irrigation, water, weather → Resource-Optimizer
- IF query is complex (multiple domains) → Invoke multiple agents

CONSTRAINTS:
- Use simple, non-technical language
- Always suggest lowest-cost option first
- If ambiguous, ask clarifying question
- Apply safety checks before responding
```

### 5. Agri-Expert Agent (MVP)

**Purpose**: Provide agricultural expertise

**Tools**:
- `analyze_image`: Claude 3.5 Sonnet multimodal analysis
- `search_plantvillage`: Vector similarity search in OpenSearch
- `get_treatment_metadata`: Retrieve treatment info from Bedrock KB
- **MCP Tools**:
  - `get_mandi_prices`: Fetch market prices via MCP Client
  - `get_nearby_mandis`: Discover nearby markets via MCP Client

**Data Sources**:
- S3: PlantVillage images (50,000+)
- OpenSearch: Image embeddings + disease metadata
- Bedrock KB: Treatment recommendations
- MCP Agmarknet Server: Real-time prices via MCP Client

**Example Flow**:
```
Input: Farmer uploads wheat leaf image
  ↓
1. Store image in S3
2. Generate embedding using Titan Multimodal
3. Search OpenSearch for similar PlantVillage images
4. Retrieve top 3 matches (e.g., Yellow Rust, Leaf Spot, Healthy)
5. Invoke Claude 3.5 Sonnet with image + matches
6. Claude identifies: "Yellow Rust (85% confidence)"
7. Fetch treatment from Bedrock KB
8. MCP Client → Agmarknet MCP Server (get_mandi_prices)
   - Request: {"crop": "wheat", "district": "Nashik", "state": "Maharashtra"}
   - Response: {"price": 2500, "market": "Nashik APMC", "date": "2026-01-13"}
9. Return: Disease + Treatment + Market Price
```

### 6. Policy-Navigator Agent (MVP)

**Purpose**: Help farmers find PM-Kisan eligibility

**Tools**:
- `search_schemes`: RAG query on Bedrock Knowledge Base
- `check_eligibility`: Query DynamoDB for village amenities
- `get_scheme_details`: Retrieve PM-Kisan information

**Data Sources**:
- Bedrock KB: PM-Kisan scheme PDF
- DynamoDB: Village amenities (irrigation type, distance to town)
- data.gov.in: Scheme eligibility criteria

**Example Flow**:
```
Input: "Am I eligible for PM-Kisan?"
  ↓
1. Search Bedrock KB for PM-Kisan details
2. Retrieve eligibility criteria:
   - Must be farmer
   - Must own land
   - Income < ₹2 lakh/year
3. Query DynamoDB for village (Nashik) amenities
4. Check farmer context (farm size, income)
5. Assess eligibility: "Yes, eligible for ₹6000/year"
6. Return: Eligibility + Subsidy Amount + Application Process
```

### 7. Resource-Optimizer Agent (MVP)

**Purpose**: Provide irrigation recommendations

**Tools**:
- `calculate_evapotranspiration`: Python math model
- `analyze_soil_moisture`: Interpret sensor data
- `optimize_pump_schedule`: Suggest irrigation times
- **MCP Tools**:
  - `get_weather_forecast`: Fetch forecasts via MCP Client
  - `get_current_weather`: Get real-time weather via MCP Client

**Data Sources**:
- S3: Sensor JSON logs
- MCP Weather Server: Weather forecasts via MCP Client
- Python: Evapotranspiration calculations

**Example Flow**:
```
Input: Soil moisture 0.4, rain forecast 60% in 12 hours
  ↓
1. Retrieve sensor data from S3
2. MCP Client → Weather MCP Server (get_weather_forecast)
   - Request: {"location": "Nashik", "days": 3}
   - Response: {
       "forecast": [
         {"date": "2026-01-13", "rain_probability": 60, "temp": 35},
         {"date": "2026-01-14", "rain_probability": 20, "temp": 33}
       ]
     }
3. Calculate Evapotranspiration (ET):
   - Temperature: 35°C
   - Humidity: 40%
   - ET = 5mm/day
4. Analyze soil moisture:
   - Current: 0.4 (low)
   - Threshold: 0.3 (critical)
   - Rain expected: 60% probability
5. Decision logic:
   - IF moisture < 0.3 AND rain predicted → Wait for rain
   - IF moisture < 0.3 AND no rain → Irrigate now
   - IF moisture > 0.7 → Don't irrigate
6. Return: "Wait for rain (60% probability in 12 hours)"
```

---

## MVP Data Models

### User Context Model

```python
{
    "user_id": "farmer_12345",
    "name": "Rajesh Kumar",
    "location": {
        "village": "Nashik",
        "district": "Nashik",
        "state": "Maharashtra"
    },
    "farm_details": {
        "total_acres": 5,
        "crops": ["wheat", "cotton"],
        "soil_type": "black_soil",
        "irrigation_type": "canal"
    },
    "language_preference": "marathi",
    "created_at": "2026-01-13T10:30:00Z"
}
```

### Conversation Message Model

```python
{
    "user_id": "farmer_12345",
    "messages": [
        {
            "timestamp": "2026-01-13T10:35:00Z",
            "role": "user",
            "content": "My wheat leaves have yellow spots",
            "type": "text"
        },
        {
            "timestamp": "2026-01-13T10:35:30Z",
            "role": "assistant",
            "content": "You have Yellow Rust. Use Neem Oil...",
            "agent": "Agri-Expert",
            "confidence": 0.85
        }
    ]
}
```

### Agent Response Model

```python
{
    "agent_name": "Agri-Expert",
    "query_type": "disease_identification",
    "response": {
        "disease": "Yellow Rust",
        "confidence": 0.85,
        "treatment": {
            "immediate": "Remove infected leaves",
            "organic": "Mix neem oil with soap water",
            "chemical": "Apply fungicide (last resort)"
        },
        "cost_estimate": "₹500-1000",
        "subsidy_available": True,
        "subsidy_info": "20% subsidy under PM-Kisan"
    },
    "sources": ["PlantVillage", "Bedrock KB", "Agmarknet"]
}
```

---

## MVP Correctness Properties

### Property 1: Query Routing Accuracy
**For any** user query, the Supervisor Agent SHALL route to the correct specialist agent(s) based on query domain (Agricultural/Policy/Resource).
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 2: Disease Identification Accuracy
**For any** crop leaf image from PlantVillage, the Agri-Expert Agent SHALL identify the disease with accuracy ≥ 80%.
**Validates: Requirements 4.2, 4.3**

### Property 3: PM-Kisan Eligibility Matching
**For any** farmer profile, the Policy-Navigator Agent SHALL correctly assess PM-Kisan eligibility based on official criteria.
**Validates: Requirements 6.1, 6.3**

### Property 4: Irrigation Recommendation Validity
**For any** weather and soil data, the Resource-Optimizer Agent SHALL generate valid irrigation recommendations.
**Validates: Requirements 7.1, 7.2**

### Property 5: Conversation History Persistence
**For any** user message, the system SHALL store it in DynamoDB and retrieve it in subsequent sessions.
**Validates: Requirements 3.1, 3.2, 3.4**

### Property 6: Safety Guardrail Filtering
**For any** agent response, Bedrock Guardrails SHALL block harmful advice and off-topic content.
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 7: Response Time SLA
**For any** query, the system SHALL respond within 5 seconds for 95% of requests.
**Validates: Requirements 10.2, 10.5**

### Property 8: Data Encryption
**For any** user data in DynamoDB or S3, it SHALL be encrypted using AWS KMS.
**Validates: Requirements 12.1, 12.2**

### Property 9: MCP Tool Permission Enforcement
**For any** MCP tool request from an agent, the MCP Client SHALL verify the agent has permission before executing the request.
**Validates: Requirements 13.3, 14.6**

### Property 10: MCP Tool Retry Logic
**For any** MCP tool call that fails, the system SHALL retry up to 3 times with exponential backoff before returning an error.
**Validates: Requirements 13.4, 15.1**

### Property 11: MCP Tool Logging
**For any** MCP tool invocation, the system SHALL log the tool call, parameters, response, and execution time.
**Validates: Requirements 13.5**

### Property 12: MCP Fallback Handling
**For any** MCP server that becomes unavailable, the system SHALL gracefully handle the failure and provide cached data when available.
**Validates: Requirements 13.6, 15.1, 15.4**

---

## MVP Error Handling

### Input Validation

**Invalid Image Format**:
- User uploads non-image file
- Response: "Please upload a valid image (JPG, PNG)"

**Empty Query**:
- User submits empty text
- Response: "Please enter a question or upload an image"

**Missing User Context**:
- User hasn't filled profile
- Response: "Please complete your profile (farm size, crop type, location)"

### Processing Errors

**Image Analysis Timeout**:
- Claude 3.5 Sonnet takes > 10 seconds
- Fallback: "Unable to analyze image. Please describe the symptoms."

**Bedrock KB Query Failure**:
- Knowledge Base search fails
- Fallback: Return cached PM-Kisan info or generic response

**MCP Server Unavailable**:
- Agmarknet or Weather MCP Server fails
- Fallback: Use cached data with timestamp disclaimer
- Example: "Market prices from cache (last updated: 2 hours ago)"

**MCP Tool Permission Denied**:
- Agent attempts to use unauthorized tool
- Response: Block request and log security incident
- Example: "Permission denied for tool get_mandi_prices"

**MCP Tool Not Found**:
- Agent requests non-existent tool
- Response: Return error with available tool suggestions
- Example: "Tool 'get_crop_yield' not found. Available tools: get_mandi_prices, get_nearby_mandis"

### Safety Errors

**Harmful Content Detected**:
- Agent generates dangerous pesticide advice
- Response: "I cannot provide that advice. Please consult a certified agronomist."

**Off-Topic Query**:
- User asks about politics
- Response: "I'm here to help with agricultural questions. How can I assist with your farming?"

---

## MVP Testing Strategy

### Unit Tests

**Agent Routing Tests**:
```python
def test_supervisor_routes_image_to_agri_expert():
    query = {"type": "image", "content": "leaf_image.jpg"}
    result = supervisor.route(query)
    assert result["agent"] == "Agri-Expert"

def test_supervisor_routes_scheme_to_policy_nav():
    query = {"type": "text", "content": "Am I eligible for PM-Kisan?"}
    result = supervisor.route(query)
    assert result["agent"] == "Policy-Navigator"
```

**Disease Identification Tests**:
```python
def test_agri_expert_identifies_yellow_rust():
    image_path = "plantvillage/yellow_rust_001.jpg"
    result = agri_expert.analyze_image(image_path)
    assert result["disease"] == "Yellow Rust"
    assert result["confidence"] >= 0.80
```

**PM-Kisan Eligibility Tests**:
```python
def test_policy_nav_assesses_eligibility():
    farmer = {
        "land_owner": True,
        "income": 150000,
        "village": "Nashik"
    }
    result = policy_nav.check_eligibility(farmer)
    assert result["eligible"] == True
    assert result["subsidy"] == 6000
```

### Property-Based Tests

**Property 1: Query Routing**
- Generate 100 random queries
- Verify correct agent routing for each
- Minimum 100 iterations

**Property 2: Disease Identification**
- Generate 100 random PlantVillage images
- Verify accuracy ≥ 80%
- Minimum 100 iterations

**Property 5: Conversation Persistence**
- Store 100 random conversations
- Retrieve and verify completeness
- Minimum 100 iterations

**Property 9: MCP Tool Permission Enforcement**
- Generate 100 random tool requests with various agent roles
- Verify permission checks work correctly
- Minimum 100 iterations

**Property 10: MCP Tool Retry Logic**
- Simulate 100 MCP server failures
- Verify retry logic with exponential backoff
- Minimum 100 iterations

**Property 12: MCP Fallback Handling**
- Simulate 100 MCP server unavailability scenarios
- Verify fallback to cached data
- Minimum 100 iterations

### Integration Tests

**End-to-End Flow**:
```python
def test_end_to_end_disease_identification():
    # 1. Upload image
    image_url = upload_image("wheat_leaf.jpg")
    
    # 2. Submit query
    response = lambda_handler({
        "body": json.dumps({
            "user_id": "test_farmer",
            "query": "What's wrong with my wheat?",
            "image_url": image_url
        })
    })
    
    # 3. Verify response
    result = json.loads(response["body"])
    assert "disease" in result["response"]
    assert "treatment" in result["response"]
    assert result["statusCode"] == 200

def test_mcp_tool_integration():
    # 1. Initialize MCP Client
    mcp_client = MCPClient(
        tool_registry_path='mcp_tool_registry.json',
        servers={
            'agmarknet': {'url': 'https://test-agmarknet-server.com'},
            'weather': {'url': 'https://test-weather-server.com'}
        }
    )
    
    # 2. Call MCP tool
    result = mcp_client.call_tool(
        tool_id='get_mandi_prices',
        agent_role='Agri-Expert',
        params={'crop': 'wheat', 'district': 'Nashik'}
    )
    
    # 3. Verify result
    assert result['success'] == True
    assert 'price' in result['data']
    assert result['source'] in ['mcp_server', 'cache']

def test_mcp_fallback_to_cache():
    # 1. Initialize MCP Client with unavailable server
    mcp_client = MCPClient(
        tool_registry_path='mcp_tool_registry.json',
        servers={
            'agmarknet': {'url': 'https://unavailable-server.com'}
        }
    )
    
    # 2. Pre-populate cache
    mcp_client.cache['get_mandi_prices:{"crop":"wheat","district":"Nashik"}'] = {
        'result': {'price': 2500, 'market': 'Nashik APMC'},
        'timestamp': time.time()
    }
    
    # 3. Call MCP tool (should fallback to cache)
    result = mcp_client.call_tool(
        tool_id='get_mandi_prices',
        agent_role='Agri-Expert',
        params={'crop': 'wheat', 'district': 'Nashik'}
    )
    
    # 4. Verify fallback
    assert result['success'] == True
    assert result['source'] == 'cache'
    assert 'warning' in result
```

---

## MVP Performance Targets

### Latency

- API Gateway → Lambda: < 100ms
- Lambda → Supervisor: < 500ms
- Supervisor → Agent: < 1000ms
- Agent → External API: < 1000ms
- **Total End-to-End: < 5 seconds (95th percentile)**

### Throughput

- Support 50-100 concurrent users
- Process 10-20 requests per second
- Handle 500+ daily active users

### Storage

- S3: 60GB (PlantVillage + user uploads)
- DynamoDB: 1GB (conversation history)
- Bedrock KB: 100MB (PM-Kisan docs)

---

## MVP Deployment

### Infrastructure as Code (CloudFormation)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'URE MVP Infrastructure'

Resources:
  # MCP Tool Registry
  MCPToolRegistry:
    Type: AWS::S3::Object
    Properties:
      Bucket: !Ref KnowledgeBaseBucket
      Key: mcp_tool_registry.json
      Body: |
        {
          "get_mandi_prices": {
            "tool_id": "get_mandi_prices",
            "server_name": "agmarknet",
            "description": "Fetch current market prices for crops by location",
            "parameters_schema": {...},
            "permissions": ["Agri-Expert", "Supervisor"],
            "timeout_ms": 5000,
            "retry_count": 3
          },
          "get_weather_forecast": {
            "tool_id": "get_weather_forecast",
            "server_name": "weather",
            "description": "Get weather forecasts for planning",
            "parameters_schema": {...},
            "permissions": ["Resource-Optimizer", "Supervisor"],
            "timeout_ms": 5000,
            "retry_count": 3
          }
        }

  # Lambda Function
  URELambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: ure-mvp-handler
      Runtime: python3.9
      Handler: lambda_handler.handler
      Memory: 512
      Timeout: 30
      Role: !GetAtt LambdaRole.Arn
      Environment:
        Variables:
          DYNAMODB_TABLE: ure-conversations
          S3_BUCKET: knowledge-base-bharat
          MCP_TOOL_REGISTRY_PATH: s3://knowledge-base-bharat/mcp_tool_registry.json
          MCP_AGMARKNET_SERVER_URL: https://agmarknet-mcp-server.com
          MCP_WEATHER_SERVER_URL: https://weather-mcp-server.com

  # API Gateway
  URE API:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: ure-mvp-api
      Description: URE MVP API

  # DynamoDB Table
  ConversationsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: ure-conversations
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: user_id
          AttributeType: S
        - AttributeName: timestamp
          AttributeType: N
      KeySchema:
        - AttributeName: user_id
          KeyType: HASH
        - AttributeName: timestamp
          KeyType: RANGE
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # S3 Bucket
  KnowledgeBaseBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: knowledge-base-bharat
      VersioningConfiguration:
        Status: Enabled
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: aws:kms
```

### Deployment Steps

1. **Create AWS Resources**:
   ```bash
   aws cloudformation create-stack \
     --stack-name ure-mvp \
     --template-body file://cloudformation.yaml
   ```

2. **Upload Datasets**:
   ```bash
   aws s3 sync plantvillage/ s3://knowledge-base-bharat/plantvillage/
   aws s3 cp agmarknet.csv s3://knowledge-base-bharat/agmarknet.csv
   aws s3 cp pm-kisan.pdf s3://knowledge-base-bharat/pm-kisan.pdf
   aws s3 cp mcp_tool_registry.json s3://knowledge-base-bharat/mcp_tool_registry.json
   ```

3. **Configure MCP Servers**:
   ```bash
   # Set up Agmarknet MCP Server
   export MCP_AGMARKNET_SERVER_URL=https://agmarknet-mcp-server.com
   
   # Set up Weather MCP Server
   export MCP_WEATHER_SERVER_URL=https://weather-mcp-server.com
   ```

4. **Create Bedrock Knowledge Base**:
   ```bash
   aws bedrock create-knowledge-base \
     --name ure-mvp-kb \
     --storage-configuration type=OPENSEARCH_SERVERLESS
   ```

5. **Deploy Streamlit App**:
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

---

## MVP Cost Breakdown

| Service | Usage | Cost/Month |
| --- | --- | --- |
| Lambda | 100K invocations, 512MB, 5s avg | $2 |
| API Gateway | 100K requests | $3.50 |
| DynamoDB | On-demand, 50GB | $15 |
| S3 | 60GB storage | $2 |
| Bedrock | 100K tokens (Claude 3.5) | $5 |
| OpenSearch Serverless | 4 OCUs | $20 |
| MCP Infrastructure | Tool registry, 2 MCP servers | $5 |
| CloudWatch | Logs + metrics | $5 |
| KMS | 1000 requests | $1 |
| Translate | 1M characters | $15 |
| **Total** | | **~$73/month** |

---

## MVP Timeline

| Week | Phase | Tasks |
| --- | --- | --- |
| 1 | Setup | AWS account, CloudFormation, Streamlit scaffold |
| 2-3 | Development | Implement agents, integrate Bedrock, S3, DynamoDB, MCP Client |
| 4 | Integration | Connect all components, test end-to-end |
| 5-6 | Testing | Unit tests, property tests, security tests |
| 7-8 | Pilot | Deploy to AWS, onboard 50 farmers, collect feedback |
| 9 | Submission | Final demo, documentation, hackathon submission |

