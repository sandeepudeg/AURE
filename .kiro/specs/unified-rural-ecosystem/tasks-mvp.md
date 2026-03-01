# MVP Implementation Tasks: Unified Rural Ecosystem (URE)

## Overview

This document outlines the implementation tasks for the URE MVP based on the requirements and design specifications. Tasks are organized by component and include checkpoints for validation.

**MVP Scope**: Single village pilot (Nashik), 3 agents, web interface, PM-Kisan scheme, 9-week timeline.

**Task Naming Convention**:
- `TASK-X.Y`: Component X, Task Y
- `*` suffix: Optional test-related sub-tasks
- `[CHECKPOINT]`: Validation point before proceeding

---

## Phase 1: Infrastructure Setup (Week 1)

### TASK-1.1: AWS Account & IAM Setup
**Objective**: Prepare AWS environment with proper permissions
**Acceptance Criteria**:
- AWS account created with billing enabled
- IAM roles created for Lambda, S3, DynamoDB, Bedrock
- KMS keys created for encryption
- CloudWatch log groups created

**Sub-tasks**:
1. Create AWS account (if not exists)
2. Set up IAM roles:
   - `ure-lambda-role` (Lambda execution)
   - `ure-bedrock-role` (Bedrock access)
   - `ure-s3-role` (S3 read/write)
3. Create KMS key for encryption
4. Create CloudWatch log groups

**[CHECKPOINT-1.1]**: Verify IAM roles and KMS key in AWS console

---

### TASK-1.2: CloudFormation Stack Deployment
**Objective**: Deploy base infrastructure (Lambda, API Gateway, DynamoDB, S3)
**Acceptance Criteria**:
- CloudFormation stack created successfully
- All resources (Lambda, API Gateway, DynamoDB, S3) deployed
- Stack outputs show API Gateway URL and DynamoDB table name
- No errors in CloudWatch logs

**Sub-tasks**:
1. Create CloudFormation template (YAML)
2. Define Lambda function resource
3. Define API Gateway REST API
4. Define DynamoDB table (ure-conversations)
5. Define S3 bucket (knowledge-base-bharat)
6. Deploy stack via AWS CLI

**[CHECKPOINT-1.2]**: Verify all resources in AWS console; test API Gateway endpoint

---

### TASK-1.3: Bedrock Knowledge Base Setup
**Objective**: Create and configure Bedrock Knowledge Base for PM-Kisan scheme
**Acceptance Criteria**:
- Bedrock Knowledge Base created
- PM-Kisan PDF uploaded and indexed
- OpenSearch Serverless collection created
- Knowledge Base can retrieve PM-Kisan information

**Sub-tasks**:
1. Create OpenSearch Serverless collection
2. Create Bedrock Knowledge Base
3. Upload PM-Kisan scheme PDF
4. Configure data source (S3)
5. Index documents
6. Test retrieval with sample queries

**[CHECKPOINT-1.3]**: Query Knowledge Base for "PM-Kisan eligibility" and verify response

---

### TASK-1.4: S3 Bucket Configuration
**Objective**: Set up S3 buckets for PlantVillage images, user uploads, and datasets
**Acceptance Criteria**:
- S3 bucket created with versioning enabled
- Encryption configured (KMS)
- Lifecycle policies set (delete old uploads after 30 days)
- PlantVillage dataset uploaded (50,000+ images)

**Sub-tasks**:
1. Create S3 bucket (knowledge-base-bharat)
2. Enable versioning
3. Configure KMS encryption
4. Set lifecycle policies
5. Upload PlantVillage dataset
6. Upload Agmarknet CSV
7. Create folder structure (plantvillage/, uploads/, datasets/)

**[CHECKPOINT-1.4]**: Verify S3 bucket structure and encryption in AWS console

---

## Phase 2: Backend Development (Weeks 2-3)

### TASK-2.1: MCP Client Implementation
**Objective**: Implement MCP Client for standardized external service access
**Acceptance Criteria**:
- MCP Client class implemented with tool registry management
- Permission verification working correctly
- Retry logic with exponential backoff implemented
- Fallback to cached data working
- All tool calls logged to CloudWatch

**Sub-tasks**:
1. Create mcp_client.py
2. Implement MCPClient class initialization
3. Implement tool registry loading from JSON
4. Implement call_tool method with permission checking
5. Implement retry logic with exponential backoff (3 retries)
6. Implement cache management for fallback
7. Implement tool call logging
8. Create mcp_tool_registry.json with 4 MVP tools
9. Test with mock MCP servers

**Code Structure**:
```python
# mcp_client.py
import json
import requests
import time
import logging

class MCPClient:
    def __init__(self, tool_registry_path, servers):
        # Load tool registry
        # Configure MCP servers
        pass
    
    def call_tool(self, tool_id, agent_role, params):
        # Validate tool exists
        # Check permissions
        # Call MCP server with retry
        # Cache result
        # Log call
        pass
```

**MCP Tool Registry** (mcp_tool_registry.json):
```json
{
  "get_mandi_prices": {
    "tool_id": "get_mandi_prices",
    "server_name": "agmarknet",
    "permissions": ["Agri-Expert", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3
  },
  "get_nearby_mandis": {...},
  "get_current_weather": {...},
  "get_weather_forecast": {...}
}
```

**[CHECKPOINT-2.1]**: Test MCP Client with mock servers; verify permission checks and retry logic

---

### TASK-2.2: Lambda Function - Request Handler
**Objective**: Implement Lambda function to orchestrate request flow with MCP Client
**Acceptance Criteria**:
- Lambda function accepts POST requests with user_id, query, image_url, context
- Initializes MCP Client with tool registry and server configurations
- Retrieves user context from DynamoDB
- Invokes Supervisor Agent with MCP Client
- Stores responses in DynamoDB
- Returns JSON response with status code 200

**Sub-tasks**:
1. Create lambda_handler.py
2. Implement request parsing (JSON validation)
3. Implement MCP Client initialization
4. Implement DynamoDB retrieval (get_item)
5. Implement Supervisor Agent invocation with MCP Client
6. Implement response storage (put_item)
7. Implement error handling (try-catch, logging)
8. Deploy to AWS Lambda with MCP Client dependencies

**Code Structure**:
```python
# lambda_handler.py
import json
import boto3
import logging
from strands import Agent
from mcp_client import MCPClient

dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()

def lambda_handler(event, context):
    # Parse input
    # Initialize MCP Client
    # Retrieve user context
    # Invoke Supervisor with MCP Client
    # Store response
    # Return response
    pass
```

**[CHECKPOINT-2.2]**: Test Lambda with sample payload; verify MCP Client initialization and DynamoDB storage

---

### TASK-2.3: Supervisor Agent Implementation
**Objective**: Implement Supervisor Agent for query routing
**Acceptance Criteria**:
- Supervisor Agent classifies query type (image/disease/scheme/irrigation)
- Routes to correct specialist agent(s)
- Handles multi-agent invocation for complex queries
- Returns structured response with agent name and confidence

**Sub-tasks**:
1. Define Supervisor system prompt
2. Implement query classification logic
3. Implement routing logic (if-else rules)
4. Implement multi-agent invocation
5. Implement response synthesis
6. Test with 20+ sample queries

**System Prompt**:
```
You are Gram-Setu (Village Bridge) AI Orchestrator.

TASK: Analyze farmer query and route to specialist agent.

AGENTS:
1. Agri-Expert: Crop diseases, pests, market prices
2. Policy-Navigator: PM-Kisan scheme eligibility
3. Resource-Optimizer: Irrigation, water management

ROUTING:
- Image OR disease/pest mention → Agri-Expert
- PM-Kisan/subsidy/scheme mention → Policy-Navigator
- Irrigation/water/weather mention → Resource-Optimizer
- Complex (multiple domains) → Multiple agents
```

**[CHECKPOINT-2.3]**: Test Supervisor with 20 sample queries; verify routing accuracy ≥ 90%

---

### TASK-2.4: Agri-Expert Agent Implementation
**Objective**: Implement Agri-Expert Agent for disease identification and market prices via MCP
**Acceptance Criteria**:
- Agent analyzes crop images using Claude 3.5 Sonnet
- Identifies disease with confidence ≥ 80%
- Retrieves treatment recommendations from Bedrock KB
- Fetches market prices via MCP Client (get_mandi_prices tool)
- Returns structured response with disease, treatment, price

**Sub-tasks**:
1. Define Agri-Expert system prompt
2. Implement analyze_image tool (Claude multimodal)
3. Implement search_plantvillage tool (OpenSearch)
4. Implement get_treatment_metadata tool (Bedrock KB)
5. Integrate MCP Client for get_mandi_prices tool
6. Integrate MCP Client for get_nearby_mandis tool
7. Test with 50 PlantVillage images
8. Validate accuracy ≥ 80%
9. Test MCP tool calls with Agmarknet MCP Server

**Tools**:
```python
def analyze_image(image_url):
    # Use Claude 3.5 Sonnet to analyze image
    pass

def search_plantvillage(disease_name):
    # Search OpenSearch for similar images
    pass

def get_treatment_metadata(disease_name):
    # Query Bedrock KB
    pass

# MCP Tools (via MCP Client)
def get_mandi_prices(crop_name, district, state):
    # Call MCP Client
    return mcp_client.call_tool(
        tool_id='get_mandi_prices',
        agent_role='Agri-Expert',
        params={'crop': crop_name, 'district': district, 'state': state}
    )

def get_nearby_mandis(district, radius_km):
    # Call MCP Client
    return mcp_client.call_tool(
        tool_id='get_nearby_mandis',
        agent_role='Agri-Expert',
        params={'district': district, 'radius_km': radius_km}
    )
```

**[CHECKPOINT-2.4]**: Test with 50 PlantVillage images; verify accuracy ≥ 80% and MCP tool calls work

---

### TASK-2.5: Policy-Navigator Agent Implementation
**Objective**: Implement Policy-Navigator Agent for PM-Kisan eligibility
**Acceptance Criteria**:
- Agent searches Bedrock Knowledge Base for PM-Kisan details
- Checks farmer eligibility based on criteria
- Returns eligibility status, subsidy amount, application process
- Handles edge cases (missing data, ambiguous eligibility)

**Sub-tasks**:
1. Define Policy-Navigator system prompt
2. Implement search_schemes tool (Bedrock KB RAG)
3. Implement check_eligibility tool (DynamoDB + logic)
4. Implement get_scheme_details tool (Bedrock KB)
5. Test with 30 farmer profiles
6. Validate eligibility assessment accuracy

**Tools**:
```python
def search_schemes(query):
    # RAG query on Bedrock KB
    pass

def check_eligibility(farmer_profile):
    # Check PM-Kisan eligibility criteria
    pass

def get_scheme_details(scheme_name):
    # Retrieve scheme details from Bedrock KB
    pass
```

**[CHECKPOINT-2.5]**: Test with 30 farmer profiles; verify eligibility assessment accuracy

---

### TASK-2.6: Resource-Optimizer Agent Implementation
**Objective**: Implement Resource-Optimizer Agent for irrigation recommendations via MCP
**Acceptance Criteria**:
- Agent calculates evapotranspiration (ET) based on weather
- Analyzes soil moisture from sensor data
- Fetches weather data via MCP Client (get_weather_forecast, get_current_weather)
- Generates irrigation recommendations
- Returns recommendation with confidence and reasoning

**Sub-tasks**:
1. Define Resource-Optimizer system prompt
2. Implement calculate_evapotranspiration tool (Python math)
3. Implement analyze_soil_moisture tool (sensor data)
4. Integrate MCP Client for get_weather_forecast tool
5. Integrate MCP Client for get_current_weather tool
6. Implement optimize_pump_schedule tool (logic)
7. Test with 20 weather/soil scenarios
8. Validate recommendation validity
9. Test MCP tool calls with Weather MCP Server

**Tools**:
```python
def calculate_evapotranspiration(temp, humidity, wind_speed):
    # Hargreaves-Samani equation
    pass

def analyze_soil_moisture(sensor_data):
    # Interpret moisture levels
    pass

def optimize_pump_schedule(et, moisture, forecast):
    # Generate irrigation recommendation
    pass

# MCP Tools (via MCP Client)
def get_weather_forecast(location, days=3):
    # Call MCP Client
    return mcp_client.call_tool(
        tool_id='get_weather_forecast',
        agent_role='Resource-Optimizer',
        params={'location': location, 'days': days}
    )

def get_current_weather(location, units='metric'):
    # Call MCP Client
    return mcp_client.call_tool(
        tool_id='get_current_weather',
        agent_role='Resource-Optimizer',
        params={'location': location, 'units': units}
    )
```

**[CHECKPOINT-2.6]**: Test with 20 weather/soil scenarios; verify recommendation validity and MCP tool calls work

---

### TASK-2.7: Bedrock Guardrails Integration
**Objective**: Implement safety guardrails to filter harmful content
**Acceptance Criteria**:
- Guardrails block harmful pesticide advice
- Guardrails block off-topic content
- Guardrails allow legitimate agricultural advice
- False positive rate < 5%

**Sub-tasks**:
1. Create Bedrock Guardrail configuration
2. Define harmful content patterns (pesticides, dangerous practices)
3. Define off-topic patterns (politics, religion, non-agricultural)
4. Implement guardrail invocation in Lambda
5. Test with 100 sample responses
6. Validate false positive rate < 5%

**[CHECKPOINT-2.7]**: Test with 100 sample responses; verify false positive rate < 5%

---

### TASK-2.8: Amazon Translate Integration
**Objective**: Implement response translation to Hindi/Marathi
**Acceptance Criteria**:
- Responses translated to user's language preference
- Translation quality acceptable (no major meaning loss)
- Latency < 500ms per translation
- Supports English, Hindi, Marathi

**Sub-tasks**:
1. Implement translate_response function
2. Integrate Amazon Translate API
3. Support language detection
4. Test with 50 sample responses
5. Validate translation quality

**[CHECKPOINT-2.8]**: Test translation with 50 responses; verify quality acceptable

---

### TASK-2.9: MCP Server Configuration
**Objective**: Configure Agmarknet and Weather MCP Servers
**Acceptance Criteria**:
- Agmarknet MCP Server configured and accessible
- Weather MCP Server configured and accessible
- MCP Tool Registry uploaded to S3
- Environment variables set in Lambda
- All 4 MCP tools working correctly

**Sub-tasks**:
1. Set up Agmarknet MCP Server (or mock for testing)
2. Set up Weather MCP Server (or mock for testing)
3. Upload mcp_tool_registry.json to S3
4. Configure Lambda environment variables:
   - MCP_TOOL_REGISTRY_PATH
   - MCP_AGMARKNET_SERVER_URL
   - MCP_WEATHER_SERVER_URL
5. Test all 4 MCP tools:
   - get_mandi_prices
   - get_nearby_mandis
   - get_current_weather
   - get_weather_forecast
6. Verify permission checks work
7. Verify retry logic works
8. Verify fallback to cache works

**[CHECKPOINT-2.9]**: Test all 4 MCP tools; verify server connectivity and tool functionality

---

## Phase 3: Frontend Development (Week 3)

### TASK-3.1: Streamlit App - Basic Structure
**Objective**: Create Streamlit web app with basic UI
**Acceptance Criteria**:
- Streamlit app runs without errors
- User profile section (sidebar) with inputs
- Query input area (text + image upload)
- Response display area
- Conversation history sidebar

**Sub-tasks**:
1. Create streamlit_app.py
2. Implement page configuration
3. Implement sidebar (user profile)
4. Implement main area (query interface)
5. Implement response display
6. Implement conversation history
7. Test locally with `streamlit run streamlit_app.py`

**[CHECKPOINT-3.1]**: Run Streamlit app locally; verify UI renders correctly

---

### TASK-3.2: Streamlit App - API Integration
**Objective**: Connect Streamlit app to Lambda via API Gateway
**Acceptance Criteria**:
- Streamlit app sends requests to API Gateway
- Receives responses from Lambda
- Displays responses in UI
- Handles errors gracefully
- Latency < 5 seconds for 95% of requests

**Sub-tasks**:
1. Implement API Gateway URL configuration
2. Implement request sending (requests library)
3. Implement response parsing
4. Implement error handling
5. Implement loading indicators
6. Test end-to-end with Lambda

**[CHECKPOINT-3.2]**: Test end-to-end flow; verify response display and error handling

---

### TASK-3.3: Streamlit App - Image Upload
**Objective**: Implement image upload and S3 storage
**Acceptance Criteria**:
- Users can upload JPG/PNG images
- Images stored in S3 with unique names
- Image URL passed to Lambda
- File size validation (max 5MB)
- Supported formats: JPG, PNG

**Sub-tasks**:
1. Implement file uploader widget
2. Implement file validation (format, size)
3. Implement S3 upload function
4. Implement URL generation
5. Test with sample images

**[CHECKPOINT-3.3]**: Upload test image; verify S3 storage and URL generation

---

### TASK-3.4: Streamlit App - Language Support
**Objective**: Implement language toggle (English/Hindi/Marathi)
**Acceptance Criteria**:
- Language selector in sidebar
- UI labels translated to selected language
- Responses displayed in selected language
- Language preference persisted in session

**Sub-tasks**:
1. Create language translation dictionary
2. Implement language selector widget
3. Implement UI translation logic
4. Implement language preference storage
5. Test with all 3 languages

**[CHECKPOINT-3.4]**: Test language toggle; verify UI and responses in all languages

---

### TASK-3.5: Streamlit App - Conversation History
**Objective**: Display and manage conversation history
**Acceptance Criteria**:
- Conversation history displayed in sidebar
- Users can view past conversations
- Users can clear history
- History persists across sessions
- Shows last 10 messages

**Sub-tasks**:
1. Implement history display widget
2. Implement history retrieval from DynamoDB
3. Implement clear history function
4. Implement session persistence
5. Test with multiple conversations

**[CHECKPOINT-3.5]**: Test conversation history; verify persistence and display

---

## Phase 4: Integration & Testing (Week 4)

### TASK-4.1: End-to-End Integration Testing
**Objective**: Test complete flow from Streamlit to Lambda to Agents
**Acceptance Criteria**:
- Complete flow works without errors
- Response time < 5 seconds
- All components communicate correctly
- Error handling works as expected

**Sub-tasks**:
1. Test text query flow
2. Test image upload flow
3. Test multi-agent routing
4. Test error scenarios
5. Test with 50 concurrent users (load test)

**[CHECKPOINT-4.1]**: Complete end-to-end test; verify all flows work

---

### TASK-4.2: Unit Tests - Lambda Handler*
**Objective**: Write unit tests for Lambda function with MCP Client
**Acceptance Criteria**:
- Tests cover request parsing, MCP Client initialization, DynamoDB operations, error handling
- Test coverage ≥ 80%
- All tests pass

**Sub-tasks**:
1. Test request parsing (valid/invalid JSON)
2. Test MCP Client initialization
3. Test DynamoDB retrieval (existing/missing user)
4. Test error handling (timeout, API failure, MCP server failure)
5. Test response formatting

**[CHECKPOINT-4.2]**: Run unit tests; verify coverage ≥ 80%

---

### TASK-4.3: Unit Tests - MCP Client*
**Objective**: Write unit tests for MCP Client
**Acceptance Criteria**:
- Tests cover tool registry loading, permission checks, retry logic, caching
- Test coverage ≥ 90%
- All tests pass

**Sub-tasks**:
1. Test tool registry loading (valid/invalid JSON)
2. Test permission verification (allowed/denied)
3. Test retry logic with exponential backoff
4. Test fallback to cache
5. Test tool call logging
6. Test MCP server unavailability handling

**[CHECKPOINT-4.3]**: Run MCP Client tests; verify coverage ≥ 90%

---

### TASK-4.4: Unit Tests - Agent Routing*
**Objective**: Write unit tests for Supervisor Agent routing
**Acceptance Criteria**:
- Tests cover all routing paths
- Routing accuracy ≥ 95%
- All tests pass

**Sub-tasks**:
1. Test image routing (→ Agri-Expert)
2. Test scheme routing (→ Policy-Navigator)
3. Test irrigation routing (→ Resource-Optimizer)
4. Test multi-agent routing

**[CHECKPOINT-4.4]**: Run routing tests; verify accuracy ≥ 95%

---

### TASK-4.5: Unit Tests - Disease Identification*
**Objective**: Write unit tests for Agri-Expert disease identification with MCP tools
**Acceptance Criteria**:
- Tests cover 50 PlantVillage images
- Tests cover MCP tool calls (get_mandi_prices, get_nearby_mandis)
- Accuracy ≥ 80%
- All tests pass

**Sub-tasks**:
1. Test with 50 PlantVillage images
2. Verify disease identification accuracy
3. Verify treatment retrieval
4. Test MCP tool: get_mandi_prices
5. Test MCP tool: get_nearby_mandis
6. Test MCP fallback when server unavailable

**[CHECKPOINT-4.5]**: Run disease tests; verify accuracy ≥ 80% and MCP tools work

---

### TASK-4.6: Unit Tests - PM-Kisan Eligibility*
**Objective**: Write unit tests for Policy-Navigator eligibility assessment
**Acceptance Criteria**:
- Tests cover 30 farmer profiles
- Eligibility assessment accuracy ≥ 95%
- All tests pass

**Sub-tasks**:
1. Test with 30 farmer profiles
2. Verify eligibility assessment
3. Verify subsidy calculation
4. Verify edge cases (missing data, ambiguous)

**[CHECKPOINT-4.6]**: Run eligibility tests; verify accuracy ≥ 95%

---

### TASK-4.7: Unit Tests - Irrigation Recommendations*
**Objective**: Write unit tests for Resource-Optimizer recommendations with MCP tools
**Acceptance Criteria**:
- Tests cover 20 weather/soil scenarios
- Tests cover MCP tool calls (get_weather_forecast, get_current_weather)
- Recommendation validity ≥ 90%
- All tests pass

**Sub-tasks**:
1. Test with 20 weather/soil scenarios
2. Verify ET calculation
3. Verify soil moisture analysis
4. Test MCP tool: get_weather_forecast
5. Test MCP tool: get_current_weather
6. Test MCP fallback when server unavailable
7. Verify recommendation validity

**[CHECKPOINT-4.7]**: Run irrigation tests; verify validity ≥ 90% and MCP tools work

---

### TASK-4.8: Property-Based Tests*
**Objective**: Write property-based tests for correctness properties including MCP
**Acceptance Criteria**:
- Tests cover all 12 MVP correctness properties (8 original + 4 MCP)
- Minimum 100 iterations per property
- All tests pass

**Sub-tasks**:
1. Property 1: Query Routing Accuracy (100 random queries)
2. Property 2: Disease Identification Accuracy (100 random images)
3. Property 3: PM-Kisan Eligibility Matching (100 random profiles)
4. Property 4: Irrigation Recommendation Validity (100 random scenarios)
5. Property 5: Conversation History Persistence (100 random conversations)
6. Property 6: Safety Guardrail Filtering (100 random responses)
7. Property 7: Response Time SLA (100 random requests)
8. Property 8: Data Encryption (100 random data items)
9. Property 9: MCP Tool Permission Enforcement (100 random tool requests)
10. Property 10: MCP Tool Retry Logic (100 simulated failures)
11. Property 11: MCP Tool Logging (100 random tool calls)
12. Property 12: MCP Fallback Handling (100 server unavailability scenarios)

**[CHECKPOINT-4.8]**: Run property tests; verify all pass with 100+ iterations

---

### TASK-4.9: Security Testing*
**Objective**: Test security controls including MCP permissions
**Acceptance Criteria**:
- All data encrypted in transit and at rest
- No PII exposed in logs
- API Gateway authentication working
- KMS encryption verified
- MCP tool permissions enforced

**Sub-tasks**:
1. Verify S3 encryption (KMS)
2. Verify DynamoDB encryption (KMS)
3. Verify API Gateway authentication
4. Verify no PII in CloudWatch logs
5. Test data deletion (TTL)
6. Verify MCP tool permission enforcement
7. Test unauthorized MCP tool access attempts

**[CHECKPOINT-4.9]**: Verify all security controls in place including MCP permissions

---

## Phase 5: Pilot Deployment (Weeks 5-6)

### TASK-5.1: AWS Deployment
**Objective**: Deploy MVP to AWS production environment with MCP infrastructure
**Acceptance Criteria**:
- All resources deployed to AWS
- MCP Client and Tool Registry configured
- Agmarknet and Weather MCP Servers accessible
- API Gateway endpoint accessible
- Lambda function invocable
- DynamoDB table accessible
- S3 bucket accessible
- Bedrock Knowledge Base accessible

**Sub-tasks**:
1. Deploy Lambda function with MCP Client
2. Upload MCP Tool Registry to S3
3. Configure MCP Server URLs in Lambda environment
4. Deploy API Gateway
5. Deploy DynamoDB table
6. Deploy S3 bucket
7. Deploy Bedrock Knowledge Base
8. Configure environment variables
9. Test all endpoints
10. Test MCP tool connectivity

**[CHECKPOINT-5.1]**: Verify all AWS resources deployed and MCP infrastructure working

---

### TASK-5.2: Streamlit App Deployment
**Objective**: Deploy Streamlit app to production
**Acceptance Criteria**:
- Streamlit app accessible via public URL
- App connects to AWS Lambda
- All features working in production
- Performance acceptable (< 5s response time)

**Sub-tasks**:
1. Deploy Streamlit app (Streamlit Cloud or EC2)
2. Configure API Gateway URL
3. Configure environment variables
4. Test all features
5. Monitor performance

**[CHECKPOINT-5.2]**: Verify Streamlit app accessible and working

---

### TASK-5.3: Farmer Onboarding
**Objective**: Onboard 50+ farmers to MVP pilot
**Acceptance Criteria**:
- 50+ farmers registered
- User profiles created
- Farmers can submit queries
- Farmers receive responses

**Sub-tasks**:
1. Create farmer registration process
2. Create user profile templates
3. Onboard farmers (50+)
4. Verify farmer access
5. Collect initial feedback

**[CHECKPOINT-5.3]**: Verify 50+ farmers registered and active

---

### TASK-5.4: Pilot Monitoring & Logging
**Objective**: Set up monitoring and logging for pilot
**Acceptance Criteria**:
- CloudWatch logs configured
- Metrics tracked (latency, throughput, errors)
- Alerts configured for errors
- Dashboard created for monitoring

**Sub-tasks**:
1. Configure CloudWatch logs
2. Create custom metrics
3. Set up alarms (error rate, latency)
4. Create CloudWatch dashboard
5. Monitor pilot for 2 weeks

**[CHECKPOINT-5.4]**: Verify monitoring and logging working

---

### TASK-5.5: Pilot Feedback Collection
**Objective**: Collect feedback from farmers during pilot
**Acceptance Criteria**:
- Feedback survey created
- 50+ responses collected
- Feedback analyzed
- Issues identified and prioritized

**Sub-tasks**:
1. Create feedback survey
2. Distribute to farmers
3. Collect responses
4. Analyze feedback
5. Identify issues and improvements

**[CHECKPOINT-5.5]**: Collect and analyze feedback from 50+ farmers

---

## Phase 6: Testing & Validation (Weeks 5-6)

### TASK-6.1: Functional Testing
**Objective**: Verify all MVP features work as specified including MCP integration
**Acceptance Criteria**:
- All 15 MVP requirements verified (12 original + 3 MCP)
- All features working correctly
- No critical bugs

**Sub-tasks**:
1. Test Requirement 1: Web Interface
2. Test Requirement 2: Supervisor Routing
3. Test Requirement 3: Conversation History
4. Test Requirement 4: Agricultural Image Analysis
5. Test Requirement 5: Market Prices
6. Test Requirement 6: PM-Kisan Scheme
7. Test Requirement 7: Irrigation Recommendations
8. Test Requirement 8: Knowledge Base
9. Test Requirement 9: Safety & Guardrails
10. Test Requirement 10: Scalability (50 concurrent users)
11. Test Requirement 11: Multi-Agent Coordination
12. Test Requirement 12: Data Privacy
13. Test Requirement 13: MCP Integration (tool calls, permissions, retry)
14. Test Requirement 14: MCP Tool Registry (discovery, metadata)
15. Test Requirement 15: MCP Error Handling (fallback, caching)

**[CHECKPOINT-6.1]**: Verify all 15 requirements met

---

### TASK-6.2: Performance Testing
**Objective**: Verify performance meets targets
**Acceptance Criteria**:
- Response time < 5 seconds (95th percentile)
- Throughput ≥ 10 requests/second
- Support 50-100 concurrent users
- No memory leaks

**Sub-tasks**:
1. Load test with 50 concurrent users
2. Load test with 100 concurrent users
3. Measure response time distribution
4. Measure throughput
5. Monitor memory usage
6. Identify bottlenecks

**[CHECKPOINT-6.2]**: Verify performance meets targets

---

### TASK-6.3: Scalability Testing
**Objective**: Verify system can scale to 1000+ users
**Acceptance Criteria**:
- System handles 1000+ concurrent users
- No degradation in response time
- Auto-scaling works correctly
- Cost remains acceptable

**Sub-tasks**:
1. Load test with 500 concurrent users
2. Load test with 1000 concurrent users
3. Verify auto-scaling triggers
4. Measure cost impact
5. Identify scaling limits

**[CHECKPOINT-6.3]**: Verify system scales to 1000+ users

---

### TASK-6.4: Correctness Property Validation*
**Objective**: Validate all 12 MVP correctness properties (8 original + 4 MCP)
**Acceptance Criteria**:
- All 12 properties verified
- Minimum 100 iterations per property
- All properties pass

**Sub-tasks**:
1. Validate Property 1: Query Routing Accuracy
2. Validate Property 2: Disease Identification Accuracy
3. Validate Property 3: PM-Kisan Eligibility Matching
4. Validate Property 4: Irrigation Recommendation Validity
5. Validate Property 5: Conversation History Persistence
6. Validate Property 6: Safety Guardrail Filtering
7. Validate Property 7: Response Time SLA
8. Validate Property 8: Data Encryption
9. Validate Property 9: MCP Tool Permission Enforcement
10. Validate Property 10: MCP Tool Retry Logic
11. Validate Property 11: MCP Tool Logging
12. Validate Property 12: MCP Fallback Handling

**[CHECKPOINT-6.4]**: Verify all 12 properties pass

---

## Phase 7: Finalization (Weeks 7-9)

### TASK-7.1: Bug Fixes & Optimization
**Objective**: Fix identified bugs and optimize performance
**Acceptance Criteria**:
- All critical bugs fixed
- Performance optimized
- Response time < 5 seconds
- No known issues

**Sub-tasks**:
1. Prioritize bugs by severity
2. Fix critical bugs
3. Optimize slow queries
4. Optimize Lambda memory usage
5. Optimize DynamoDB queries
6. Re-test after fixes

**[CHECKPOINT-7.1]**: Verify all critical bugs fixed

---

### TASK-7.2: Documentation
**Objective**: Create comprehensive documentation
**Acceptance Criteria**:
- Architecture documentation complete
- API documentation complete
- Deployment guide complete
- User guide complete
- Developer guide complete

**Sub-tasks**:
1. Create architecture documentation
2. Create API documentation (OpenAPI spec)
3. Create deployment guide
4. Create user guide (for farmers)
5. Create developer guide (for team)
6. Create troubleshooting guide

**[CHECKPOINT-7.2]**: Verify all documentation complete

---

### TASK-7.3: Demo Preparation
**Objective**: Prepare demo for hackathon submission
**Acceptance Criteria**:
- Demo script prepared
- Demo environment ready
- Demo runs smoothly
- All features showcased

**Sub-tasks**:
1. Create demo script
2. Prepare demo data (sample queries, images)
3. Set up demo environment
4. Test demo flow
5. Prepare presentation slides

**[CHECKPOINT-7.3]**: Demo runs smoothly without errors

---

### TASK-7.4: Hackathon Submission
**Objective**: Submit MVP to AWS AI for Bharat Hackathon
**Acceptance Criteria**:
- All submission requirements met
- Code uploaded to repository
- Documentation complete
- Demo video recorded (if required)
- Submission deadline met

**Sub-tasks**:
1. Prepare submission package
2. Create README with project overview
3. Upload code to GitHub/repository
4. Record demo video (if required)
5. Submit to hackathon platform
6. Verify submission received

**[CHECKPOINT-7.4]**: Submission confirmed by hackathon platform

---

## Task Dependencies & Timeline

```
Week 1: Infrastructure Setup
├─ TASK-1.1: AWS Account & IAM Setup
├─ TASK-1.2: CloudFormation Stack Deployment
├─ TASK-1.3: Bedrock Knowledge Base Setup
└─ TASK-1.4: S3 Bucket Configuration

Week 2-3: Backend Development
├─ TASK-2.1: MCP Client Implementation
├─ TASK-2.2: Lambda Function - Request Handler
├─ TASK-2.3: Supervisor Agent Implementation
├─ TASK-2.4: Agri-Expert Agent Implementation
├─ TASK-2.5: Policy-Navigator Agent Implementation
├─ TASK-2.6: Resource-Optimizer Agent Implementation
├─ TASK-2.7: Bedrock Guardrails Integration
├─ TASK-2.8: Amazon Translate Integration
└─ TASK-2.9: MCP Server Configuration

Week 3: Frontend Development
├─ TASK-3.1: Streamlit App - Basic Structure
├─ TASK-3.2: Streamlit App - API Integration
├─ TASK-3.3: Streamlit App - Image Upload
├─ TASK-3.4: Streamlit App - Language Support
└─ TASK-3.5: Streamlit App - Conversation History

Week 4: Integration & Testing
├─ TASK-4.1: End-to-End Integration Testing
├─ TASK-4.2: Unit Tests - Lambda Handler*
├─ TASK-4.3: Unit Tests - MCP Client*
├─ TASK-4.4: Unit Tests - Agent Routing*
├─ TASK-4.5: Unit Tests - Disease Identification*
├─ TASK-4.6: Unit Tests - PM-Kisan Eligibility*
├─ TASK-4.7: Unit Tests - Irrigation Recommendations*
├─ TASK-4.8: Property-Based Tests*
└─ TASK-4.9: Security Testing*

Weeks 5-6: Pilot Deployment & Testing
├─ TASK-5.1: AWS Deployment
├─ TASK-5.2: Streamlit App Deployment
├─ TASK-5.3: Farmer Onboarding
├─ TASK-5.4: Pilot Monitoring & Logging
├─ TASK-5.5: Pilot Feedback Collection
├─ TASK-6.1: Functional Testing
├─ TASK-6.2: Performance Testing
├─ TASK-6.3: Scalability Testing
└─ TASK-6.4: Correctness Property Validation*

Weeks 7-9: Finalization
├─ TASK-7.1: Bug Fixes & Optimization
├─ TASK-7.2: Documentation
├─ TASK-7.3: Demo Preparation
└─ TASK-7.4: Hackathon Submission
```

---

## Success Criteria

### Functional Success
- All 15 MVP requirements implemented and verified (12 original + 3 MCP)
- All 12 correctness properties validated (8 original + 4 MCP)
- Zero critical bugs
- All features working as specified
- MCP integration working correctly (tool calls, permissions, retry, fallback)

### Performance Success
- Response time < 5 seconds (95th percentile)
- Throughput ≥ 10 requests/second
- Support 50-100 concurrent users
- Cost ≤ $73/month (includes MCP infrastructure)

### User Success
- 50+ farmers onboarded
- Positive feedback from farmers
- High engagement (daily active users)
- Successful disease identification (≥ 80% accuracy)

### Safety Success
- Zero harmful advice delivered
- All guardrails working correctly
- Data privacy maintained
- No security incidents

---

## Notes

- Tasks marked with `*` are optional test-related sub-tasks. Include them for comprehensive testing but can be deferred if time is limited.
- Each checkpoint should be validated before proceeding to the next phase.
- Parallel execution is possible for independent tasks (e.g., agent implementations can run in parallel).
- Timeline assumes 1-2 developers working full-time on the project.
