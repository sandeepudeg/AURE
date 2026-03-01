# MVP Requirements Document: Unified Rural Ecosystem (URE)

## Introduction

The MVP (Minimum Viable Product) for URE focuses on delivering core functionality for the AI for Bharat hackathon. This document outlines the essential requirements needed to demonstrate the multi-agent architecture and deliver immediate value to farmers in a pilot village.

**MVP Scope**: Single village pilot with 3 specialist agents, basic web interface, and integration with one government scheme dataset.

**Timeline**: Q1 2026 (3 months)

**Success Metrics**:
- 50+ farmers onboarded in pilot village
- 80%+ disease identification accuracy on PlantVillage images
- 90%+ scheme eligibility matching accuracy
- < 5 second response time for 95% of queries
- Zero critical safety violations

---

## Glossary

- **Strands Supervisor Agent**: Orchestration agent using Claude 3.5 Sonnet on Bedrock
- **Agri-Expert Agent**: Agricultural image analysis and market price lookup
- **Policy-Navigator Agent**: Government scheme eligibility matching
- **Resource-Optimizer Agent**: Irrigation timing recommendations
- **Amazon Bedrock**: AWS service providing Claude 3.5 Sonnet model
- **Claude 3.5 Sonnet**: Foundation model for all LLM-based agents
- **Bedrock Knowledge Base**: Vector database for RAG on schemes
- **Amazon S3**: Cloud storage for images and datasets
- **Amazon DynamoDB**: NoSQL database for conversation history
- **Amazon Lambda**: Serverless compute for request handling
- **Amazon API Gateway**: REST API endpoint
- **PlantVillage Dataset**: 50,000+ crop disease images
- **Agmarknet**: Government of India market price data
- **PM-Kisan**: Primary government scheme for MVP
- **Bedrock Guardrails**: Safety mechanisms for content filtering

---

## MVP Requirements

### Requirement 1: Web Interface and Entry Point (MVP Scope)

**User Story:** As a farmer in the pilot village, I want to access the system through a simple web interface, so that I can get agricultural advice without technical barriers.

#### Acceptance Criteria

1. WHEN a farmer visits the web app, THE System SHALL display a simple interface with text input and image upload
2. WHEN a farmer types a question, THE System SHALL send it to Lambda and display the response within 5 seconds
3. WHEN a farmer uploads a crop image, THE System SHALL store it in S3 and analyze it within 10 seconds
4. WHEN a farmer submits a query, THE System SHALL retrieve their conversation history and provide context-aware responses
5. THE System SHALL display responses in simple Hindi/Marathi language (translated from English)

_Requirements: 1.1, 1.2, 1.4, 3.2, 3.4_

---

### Requirement 2: Supervisor Agent Routing (MVP Scope)

**User Story:** As a system, I want the Supervisor Agent to intelligently route requests to the correct specialist, so that each query is handled by the appropriate expert.

#### Acceptance Criteria

1. WHEN a farmer sends a query, THE Strands Supervisor Agent SHALL classify it as Agricultural, Policy, or Resource-based
2. WHEN a farmer sends a crop image, THE Supervisor Agent SHALL route it to the Agri-Expert Agent
3. WHEN a farmer asks about PM-Kisan scheme, THE Supervisor Agent SHALL route it to the Policy-Navigator Agent
4. WHEN a farmer asks about irrigation, THE Supervisor Agent SHALL route it to the Resource-Optimizer Agent
5. WHEN the Supervisor Agent generates a response, THE System SHALL apply Bedrock Guardrails to block harmful advice

_Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_

---

### Requirement 3: Conversation History (MVP Scope)

**User Story:** As a farmer, I want the system to remember my previous conversations, so that I don't have to repeat information.

#### Acceptance Criteria

1. WHEN a farmer sends a message, THE System SHALL store it in DynamoDB with user ID, timestamp, and content
2. WHEN a farmer starts a new session, THE System SHALL load their previous conversation history
3. WHEN retrieving history, THE System SHALL include user context (farm size, crop type, location)
4. WHEN a farmer references earlier information, THE System SHALL use that context in responses

_Requirements: 3.1, 3.2, 3.4, 3.5_

---

### Requirement 4: Agricultural Image Analysis (MVP Scope)

**User Story:** As a farmer, I want to upload photos of my crops and receive disease identification, so that I can address problems quickly.

#### Acceptance Criteria

1. WHEN a farmer uploads a leaf image, THE System SHALL store it in S3 and pass the URL to the Agri-Expert Agent
2. WHEN the Agri-Expert Agent receives an image, THE System SHALL invoke Claude 3.5 Sonnet to analyze it
3. WHEN an image is analyzed, THE Agri-Expert Agent SHALL identify diseases using PlantVillage Dataset as reference
4. WHEN a disease is identified, THE Agri-Expert Agent SHALL provide treatment recommendations (organic first, then chemical)
5. WHEN a disease is identified, THE Supervisor Agent SHALL simultaneously check for PM-Kisan subsidies

_Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

---

### Requirement 5: Market Price Information (MVP Scope - Limited)

**User Story:** As a farmer, I want to know current market prices for my crops, so that I can decide when to sell.

#### Acceptance Criteria

1. WHEN a farmer asks about crop prices, THE Agri-Expert Agent SHALL query the Bedrock Knowledge Base for Agmarknet prices
2. WHEN price data is retrieved, THE System SHALL provide prices for the farmer's district and crop type
3. WHEN multiple markets are available, THE System SHALL recommend the market with the highest price
4. WHEN price data is queried, THE System SHALL use the latest Agmarknet dataset (updated daily)

_Requirements: 5.1, 5.2, 5.3, 5.5_

---

### Requirement 6: Government Scheme Navigation (MVP Scope - PM-Kisan Only)

**User Story:** As a farmer, I want to find out if I'm eligible for PM-Kisan scheme, so that I can access government support.

#### Acceptance Criteria

1. WHEN a farmer asks about PM-Kisan, THE Policy-Navigator Agent SHALL query the Bedrock Knowledge Base
2. WHEN PM-Kisan is identified, THE Policy-Navigator Agent SHALL provide eligibility criteria and subsidy amount (₹6000/year)
3. WHEN a farmer describes their situation, THE Policy-Navigator Agent SHALL assess PM-Kisan eligibility
4. WHEN scheme information is retrieved, THE System SHALL include eligibility criteria, subsidy amount, and application process

_Requirements: 6.1, 6.2, 6.3, 6.6_

---

### Requirement 7: Resource Optimization (MVP Scope - Basic)

**User Story:** As a farmer, I want irrigation recommendations based on weather and soil conditions, so that I can save water.

#### Acceptance Criteria

1. WHEN a farmer provides soil moisture and weather data (JSON), THE Resource-Optimizer Agent SHALL analyze it
2. WHEN irrigation timing is calculated, THE System SHALL provide specific recommendations based on rainfall forecast
3. WHEN soil moisture is high (>0.7), THE System SHALL advise AGAINST irrigation
4. WHEN soil moisture is low (<0.3) and rain is predicted, THE System SHALL advise "Wait for rain"

_Requirements: 7.1, 7.2, 7.3, 7.4_

---

### Requirement 8: Knowledge Base Setup (MVP Scope)

**User Story:** As a system administrator, I want to set up the Knowledge Base with essential datasets, so that agents can provide accurate information.

#### Acceptance Criteria

1. WHEN the system is initialized, THE Knowledge Base SHALL be populated with PM-Kisan scheme details
2. WHEN the Knowledge Base is created, THE System SHALL index Agmarknet prices and PlantVillage disease metadata
3. WHEN RAG queries are performed, THE System SHALL retrieve information from the indexed knowledge base
4. WHEN datasets are indexed, THE System SHALL store PlantVillage images and Agmarknet CSVs in S3

_Requirements: 8.1, 8.2, 8.4, 8.6_

---

### Requirement 9: Safety and Guardrails (MVP Scope)

**User Story:** As a system administrator, I want to ensure the AI provides safe advice, so that farmers don't receive harmful guidance.

#### Acceptance Criteria

1. WHEN an agent generates a response, THE System SHALL apply Bedrock Guardrails to validate content safety
2. WHEN a response contains potentially harmful advice, THE System SHALL reject it and provide a safe alternative
3. WHEN a user asks off-topic questions, THE System SHALL redirect them to agricultural topics
4. WHEN guardrail violations occur, THE System SHALL log the incident for review

_Requirements: 9.1, 9.2, 9.3, 9.5_

---

### Requirement 10: Scalability (MVP Scope - Pilot Scale)

**User Story:** As a system architect, I want the system to handle 50+ concurrent farmers in the pilot village, so that the MVP can scale if successful.

#### Acceptance Criteria

1. WHEN user load increases to 50 concurrent users, THE System SHALL process requests without degradation
2. WHEN multiple farmers submit requests simultaneously, THE System SHALL process them within 5 seconds
3. WHEN S3 storage grows with images, THE System SHALL maintain fast retrieval
4. WHEN DynamoDB usage increases, THE System SHALL maintain consistent query performance

_Requirements: 10.1, 10.2, 10.3, 10.4_

---

### Requirement 11: Multi-Agent Coordination (MVP Scope)

**User Story:** As a system designer, I want multiple agents to work together, so that farmers receive holistic recommendations.

#### Acceptance Criteria

1. WHEN a query requires multiple agents, THE Supervisor Agent SHALL coordinate their execution
2. WHEN the Agri-Expert identifies a disease, THE Policy-Navigator Agent SHALL simultaneously search for PM-Kisan subsidies
3. WHEN responses from multiple agents are received, THE Supervisor Agent SHALL synthesize them into one answer
4. WHEN agents communicate, THE System SHALL use Strands Agents SDK tool calling for reliable coordination

_Requirements: 11.1, 11.2, 11.3, 11.6_

---

### Requirement 12: Data Privacy (MVP Scope)

**User Story:** As a farmer, I want my personal information to be protected, so that my data remains private.

#### Acceptance Criteria

1. WHEN user data is stored in DynamoDB, THE System SHALL encrypt it using AWS KMS
2. WHEN data is transmitted between components, THE System SHALL use HTTPS/TLS encryption
3. WHEN a user requests data deletion, THE System SHALL remove their conversation history from DynamoDB
4. WHEN sensitive information is detected, THE System SHALL mask it in logs

_Requirements: 12.1, 12.2, 12.3, 12.5_

---

---

### Requirement 13: Model Context Protocol (MCP) Integration (MVP Scope - Basic)

**User Story:** As a system architect, I want to standardize external service access through MCP, so that agents can reliably access market prices and weather data without tight coupling.

#### Acceptance Criteria

1. WHEN the system initializes, THE MCP Client SHALL be configured with access to two MCP Servers: Agmarknet and Weather
2. WHEN an agent requests market price data, THE MCP Client SHALL route the request to the Agmarknet MCP Server using standardized tool calling
3. WHEN an MCP tool is invoked, THE System SHALL verify the requesting agent has permission to use that tool before execution
4. WHEN an MCP tool call fails, THE System SHALL retry up to 3 times with exponential backoff before returning an error
5. WHEN an MCP tool is invoked, THE System SHALL log the tool call, parameters, response, and execution time to CloudWatch

**Available MCP Tools (MVP)**:
- `get_mandi_prices`: Fetch current market prices for crops by location
- `get_nearby_mandis`: Discover nearby market locations
- `get_current_weather`: Retrieve real-time weather conditions
- `get_weather_forecast`: Get weather forecasts for planning

_Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

---

### Requirement 14: MCP Tool Registry (MVP Scope - Basic)

**User Story:** As a system administrator, I want a centralized registry of MCP tools, so that agents can discover available tools and understand their parameters.

#### Acceptance Criteria

1. WHEN the system initializes, THE MCP Tool Registry SHALL be populated with metadata for all available MCP tools
2. WHEN an agent queries for available tools, THE System SHALL return tool metadata including parameters and permissions
3. WHEN an agent attempts to use a tool, THE System SHALL validate the tool exists in the registry before execution

**Tool Registry Metadata Structure (MVP)**:
- tool_id: Unique identifier for the tool
- server_name: Name of the MCP server providing the tool
- description: Human-readable description of tool functionality
- parameters_schema: JSON schema defining required and optional parameters
- permissions: List of agent roles authorized to use the tool

_Requirements: 14.1, 14.2, 14.5_

---

### Requirement 15: MCP Error Handling (MVP Scope - Basic)

**User Story:** As a system architect, I want basic error handling for MCP tool failures, so that the system gracefully handles when external services are unavailable.

#### Acceptance Criteria

1. WHEN an MCP server fails to respond within timeout, THE System SHALL return a user-friendly error message
2. WHEN an MCP tool is not found, THE System SHALL return an error message and suggest alternative data sources
3. WHEN an agent lacks permission for an MCP tool, THE System SHALL block the request and log a security incident
4. WHEN MCP fallback is triggered, THE System SHALL provide cached data with timestamp disclaimer to the user

**Error Handling Strategies (MVP)**:
- MCP Server Unavailable: Fall back to cached data from last 24 hours
- Tool Not Found: Suggest alternative tools or manual data entry
- Permission Denied: Block request and log security incident

_Requirements: 15.1, 15.2, 15.4, 15.7_

---

## MVP Exclusions (Phase 2+)

The following features are **NOT** included in MVP but planned for Phase 2:

- WhatsApp/Telegram integration (Phase 2)
- Voice interface (Phase 2)
- Multi-language support beyond Hindi/Marathi (Phase 2)
- Historical price trends (Phase 2)
- Multiple government schemes (Phase 2 - currently only PM-Kisan)
- Advanced irrigation calculations (Phase 2)
- IoT sensor integration (Phase 2)
- Government API MCP Server (Phase 2)
- Advanced MCP circuit breaker pattern (Phase 2)
- MCP tool metadata updates without restart (Phase 2)
- Federated learning (Phase 3)
- Sovereign LLM migration (Phase 3)

---

## MVP Architecture

### High-Level MVP Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (MVP)                         │
│              Streamlit Web App (Single Page)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Text Input Box | Image Upload | Response Display       │  │
│  │  Conversation History | Language Toggle (Hindi/Marathi) │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Amazon API Gateway
                    (REST Endpoint)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              AWS Lambda (Request Handler - MVP)                 │
│  - Parse user input (text/image)                                │
│  - Retrieve conversation history from DynamoDB                  │
│  - Invoke Supervisor Agent                                      │
│  - Store response in DynamoDB                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        Strands Supervisor Agent (Claude 3.5 Sonnet)             │
│  - Classify query: Agricultural/Policy/Resource                 │
│  - Route to appropriate specialist agent                        │
│  - Synthesize multi-agent responses                             │
│  - Apply Bedrock Guardrails                                     │
└─────────────────────────────────────────────────────────────────┘
         ↙                    ↓                    ↘
    ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
    │ Agri-Expert │   │Policy-Nav    │   │Resource-Optimizer│
    │   Agent     │   │   Agent      │   │     Agent        │
    │ (MVP)       │   │   (MVP)      │   │     (MVP)        │
    └─────────────┘   └──────────────┘   └──────────────────┘
         ↓                    ↓                    ↓
    ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
    │ S3 Images   │   │Bedrock KB    │   │Python Logic      │
    │ OpenSearch  │   │(PM-Kisan)    │   │(Irrigation Calc) │
    │ Agmarknet   │   │DynamoDB      │   │S3 Sensor Logs    │
    │ (Prices)    │   │(Village Data)│   │Weather APIs      │
    └─────────────┘   └──────────────┘   └──────────────────┘
                              ↓
                    Bedrock Guardrails
                    (Safety Validation)
                              ↓
                    Amazon Translate
                    (Hindi/Marathi)
                              ↓
                    Response to User
                    (via Streamlit)
                              ↓
                    DynamoDB + CloudWatch
                    (Logging & Audit)
```

### MVP Component Interaction Flow

1. **User Input**: Farmer enters text or uploads image via Streamlit
2. **API Gateway**: Routes request to Lambda function
3. **Context Retrieval**: Lambda fetches conversation history from DynamoDB
4. **Supervisor Analysis**: Strands Supervisor classifies query and routes to agent(s)
5. **Agent Execution**: Specialist agent(s) execute with appropriate tools
6. **Response Synthesis**: Supervisor combines outputs into single response
7. **Safety Validation**: Bedrock Guardrails filter response
8. **Language Translation**: Amazon Translate converts to Hindi/Marathi
9. **Response Delivery**: Answer displayed in Streamlit UI
10. **Persistence**: Conversation stored in DynamoDB, audit logged to CloudWatch

---

## MVP Technology Stack

### Core AI/ML Services (MVP)

| Component | Technology | Purpose | MVP Details |
| --- | --- | --- | --- |
| **Foundation Model** | Claude 3.5 Sonnet (Bedrock) | LLM backbone for all agents | Multimodal (text, images), tool calling |
| **Agent Orchestration** | Strands Agents SDK | Multi-agent coordination | 3 agents: Agri-Expert, Policy-Nav, Resource-Opt |
| **Knowledge Retrieval** | Bedrock Knowledge Base | RAG for PM-Kisan scheme | Single scheme indexed for MVP |
| **Vector Database** | Amazon OpenSearch Serverless | Image/document embeddings | PlantVillage images + PM-Kisan docs |
| **Embeddings** | Amazon Titan Multimodal | Image-to-vector conversion | For PlantVillage similarity search |
| **Safety & Guardrails** | Bedrock Guardrails | Content filtering | Blocks harmful advice, off-topic queries |

### AWS Infrastructure Services (MVP)

| Component | Technology | Purpose | MVP Details |
| --- | --- | --- | --- |
| **Compute** | AWS Lambda | Serverless request handling | Single function for MVP |
| **API Management** | Amazon API Gateway | REST endpoint | Single endpoint for Streamlit |
| **Storage** | Amazon S3 | Image and dataset storage | knowledge-base-bharat bucket |
| **Database** | Amazon DynamoDB | Conversation history | On-demand pricing for MVP |
| **Encryption** | AWS KMS | Data encryption at rest | Encrypts DynamoDB and S3 |
| **Networking** | HTTPS/TLS | Secure communication | All API calls encrypted |
| **Monitoring** | CloudWatch | Logging and metrics | Basic dashboards for MVP |
| **IAM** | AWS Identity & Access Management | Access control | Least-privilege Lambda role |

### Frontend and Integration (MVP)

| Component | Technology | Purpose | MVP Details |
| --- | --- | --- | --- |
| **Web Interface** | Streamlit (Python) | User-facing application | Single-page app, no authentication |
| **Language Support** | Amazon Translate | Multi-language responses | Hindi and Marathi only for MVP |
| **Text-to-Speech** | Amazon Polly (Optional) | Voice output | Not included in MVP |

### Data Sources (MVP)

| Dataset | Source | Format | Use Case | MVP Status |
| --- | --- | --- | --- | --- |
| **PlantVillage** | Kaggle/GitHub | Images (JPG) | Disease identification | Included (50,000 images) |
| **Agmarknet Prices** | agmarknet.gov.in | CSV | Market prices | Included (daily update) |
| **PM-Kisan Scheme** | data.gov.in | PDF/CSV | Scheme eligibility | Included (single scheme) |
| **Village Amenities** | Census 2011 | CSV | Eligibility checks | Included (pilot village only) |
| **Weather Data** | OpenWeather API | JSON | Irrigation recommendations | Included (free tier) |

### Development and Deployment Tools (MVP)

| Tool | Purpose | MVP Details |
| --- | --- | --- |
| **Python 3.9+** | Development language | Lambda functions, Streamlit app |
| **Boto3** | AWS SDK | Interact with Lambda, S3, DynamoDB, Bedrock |
| **Strands SDK** | Agent framework | @tool decorator, Agent class |
| **Streamlit** | Web framework | Simple UI without backend complexity |
| **Pandas** | Data processing | CSV handling for Agmarknet, Census data |
| **NumPy** | Numerical computing | Irrigation calculations |
| **Pillow (PIL)** | Image processing | Image upload and preprocessing |
| **JSON** | Data format | API requests/responses, sensor logs |
| **Git/GitHub** | Version control | Code repository |
| **AWS CloudFormation** | Infrastructure as Code | Deploy Lambda, API Gateway, DynamoDB |
| **Docker** | Containerization | Package Lambda function |
| **pytest** | Testing | Unit tests for agent logic |

### External APIs and Services (MVP)

| Service | Purpose | MVP Integration |
| --- | --- | --- |
| **Agmarknet API** | Real-time crop prices | MCP Server integration via MCP Client |
| **OpenWeather API** | Weather forecasts | MCP Server integration via MCP Client |
| **Amazon Translate** | Language translation | Convert responses to Hindi/Marathi |
| **Amazon Polly** | Text-to-speech | Optional for future phases |

### MCP Integration (MVP)

| Component | Technology | Purpose | MVP Details |
| --- | --- | --- | --- |
| **MCP Client** | Model Context Protocol Client | Central hub for tool requests | Manages requests from agents to MCP servers |
| **MCP Tool Registry** | JSON-based registry | Tool metadata storage | Stores tool definitions, parameters, permissions |
| **Agmarknet MCP Server** | MCP Server | Market price data access | Provides get_mandi_prices, get_nearby_mandis tools |
| **Weather MCP Server** | MCP Server | Weather data access | Provides get_current_weather, get_weather_forecast tools |

---

## MVP Toolchain Integration Flow

```
User Input (Streamlit Web App)
    ↓
Streamlit → API Gateway
    ↓
Lambda Function (Python)
    ├─→ Retrieve DynamoDB conversation history
    ├─→ Invoke Strands Supervisor Agent
    │
    └─→ Strands Supervisor (Claude 3.5 Sonnet on Bedrock)
        ├─→ Agri-Expert Agent
        │   ├─→ Amazon S3 (Image retrieval)
        │   ├─→ Amazon OpenSearch (PlantVillage embeddings)
        │   ├─→ Bedrock Knowledge Base (Disease metadata)
        │   └─→ MCP Client → Agmarknet MCP Server (Market prices)
        │
        ├─→ Policy-Navigator Agent
        │   ├─→ Bedrock Knowledge Base (PM-Kisan scheme)
        │   ├─→ Amazon DynamoDB (Village eligibility data)
        │   └─→ data.gov.in (Scheme information)
        │
        └─→ Resource-Optimizer Agent
            ├─→ Amazon S3 (Sensor JSON logs)
            ├─→ Python Code Interpreter (Evapotranspiration)
            └─→ MCP Client → Weather MCP Server (Weather forecasts)

    ↓
Bedrock Guardrails (Safety validation)
    ↓
Amazon Translate (Hindi/Marathi conversion)
    ↓
Response to Streamlit UI
    ↓
Store in DynamoDB (Conversation history)
    ↓
Log to CloudWatch (Audit trail)
```

---

## MVP Deployment Architecture

### Infrastructure Components

```
AWS Account (Single Region: us-east-1)
│
├─ Lambda Function
│  ├─ Runtime: Python 3.9
│  ├─ Memory: 512 MB
│  ├─ Timeout: 30 seconds
│  ├─ Concurrency: 100 (reserved)
│  └─ MCP Client integration
│
├─ MCP Infrastructure
│  ├─ MCP Tool Registry (JSON)
│  ├─ Agmarknet MCP Server
│  ├─ Weather MCP Server
│  └─ Tool permission management
│
├─ API Gateway
│  ├─ REST API
│  ├─ Single POST endpoint: /query
│  └─ Rate limiting: 1000 req/min
│
├─ DynamoDB Table
│  ├─ Partition Key: user_id
│  ├─ Sort Key: timestamp
│  ├─ On-demand billing
│  └─ TTL: 90 days
│
├─ S3 Bucket (knowledge-base-bharat)
│  ├─ PlantVillage images (50GB)
│  ├─ Agmarknet CSVs (100MB)
│  ├─ PM-Kisan PDFs (50MB)
│  ├─ User uploads (10GB)
│  └─ Versioning enabled
│
├─ Bedrock Knowledge Base
│  ├─ Vector DB: OpenSearch Serverless
│  ├─ Indexed documents: PM-Kisan scheme
│  └─ Embedding model: Titan Multimodal
│
├─ CloudWatch
│  ├─ Logs: Lambda execution logs
│  ├─ Metrics: Response time, error rate
│  └─ Alarms: High error rate, throttling
│
└─ IAM Role (Lambda Execution)
   ├─ bedrock:InvokeModel
   ├─ s3:GetObject, s3:PutObject
   ├─ dynamodb:GetItem, dynamodb:PutItem
   ├─ kms:Decrypt, kms:GenerateDataKey
   └─ logs:CreateLogGroup, logs:PutLogEvents
```

### Deployment Steps

1. **Create AWS Resources** (CloudFormation):
   - Lambda function with Strands SDK
   - API Gateway endpoint
   - DynamoDB table
   - S3 bucket with versioning
   - Bedrock Knowledge Base

2. **Upload Datasets**:
   - PlantVillage images to S3
   - Agmarknet CSV to S3
   - PM-Kisan PDF to S3
   - Index documents in Bedrock KB
   - Configure MCP Tool Registry
   - Set up Agmarknet and Weather MCP Servers

3. **Deploy Streamlit App**:
   - Deploy to Streamlit Cloud or EC2
   - Configure API Gateway endpoint
   - Set environment variables (AWS credentials)

4. **Configure Monitoring**:
   - CloudWatch dashboards
   - Alarms for errors and latency
   - Log retention: 7 days

---

## MVP Cost Estimation (Monthly)

| Service | Usage | Cost |
| --- | --- | --- |
| **Lambda** | 100K invocations, 512MB, 5s avg | $2 |
| **API Gateway** | 100K requests | $3.50 |
| **DynamoDB** | On-demand, 50GB storage | $15 |
| **S3** | 60GB storage, 10K requests | $2 |
| **Bedrock** | 100K tokens (Claude 3.5) | $5 |
| **OpenSearch Serverless** | 4 OCUs | $20 |
| **MCP Infrastructure** | Tool registry, 2 MCP servers | $5 |
| **CloudWatch** | Logs and metrics | $5 |
| **KMS** | 1000 requests | $1 |
| **Translate** | 1M characters | $15 |
| **Total** | | **~$73/month** |

---

## MVP Deployment Timeline

| Phase | Duration | Tasks |
| --- | --- | --- |
| **Setup** | Week 1 | AWS account setup, CloudFormation templates, Streamlit scaffolding |
| **Agent Development** | Weeks 2-3 | Implement Supervisor, Agri-Expert, Policy-Nav, Resource-Opt agents |
| **Integration** | Week 4 | Connect agents to Bedrock, S3, DynamoDB, APIs |
| **Testing** | Weeks 5-6 | Unit tests, integration tests, property-based tests, security testing |
| **Pilot Deployment** | Weeks 7-8 | Deploy to AWS, onboard 50 farmers, collect feedback |
| **Hackathon Submission** | Week 9 | Final demo, documentation, submission |

---

## MVP Success Criteria

### Functional Success

- [ ] Supervisor Agent correctly routes 95%+ of queries to appropriate specialist
- [ ] Agri-Expert identifies diseases with 80%+ accuracy on PlantVillage images
- [ ] Policy-Navigator correctly assesses PM-Kisan eligibility for 90%+ of test cases
- [ ] Resource-Optimizer provides valid irrigation recommendations for 90%+ of queries
- [ ] Multi-agent coordination works seamlessly for complex queries

### Performance Success

- [ ] 95% of queries respond within 5 seconds
- [ ] System handles 50 concurrent users without errors
- [ ] Image upload and analysis completes within 10 seconds
- [ ] Conversation history retrieval < 500ms

### Safety Success

- [ ] Zero critical safety violations (harmful advice delivered)
- [ ] 100% of guardrail violations logged and reviewed
- [ ] All user data encrypted at rest and in transit
- [ ] PII masking working for all sensitive fields

### User Success

- [ ] 50+ farmers onboarded in pilot village
- [ ] 70%+ of farmers find recommendations helpful (survey)
- [ ] 60%+ of farmers use system at least 2x per week
- [ ] Net Promoter Score (NPS) ≥ 40

---

## MVP Deployment Plan

### Phase 1: Development (Weeks 1-4)
- Set up AWS infrastructure (Lambda, DynamoDB, S3, Bedrock)
- Configure MCP Client and Tool Registry
- Set up Agmarknet and Weather MCP Servers
- Implement Supervisor Agent with routing logic
- Implement Agri-Expert Agent with PlantVillage integration and MCP tool access
- Implement Policy-Navigator Agent with PM-Kisan data
- Implement Resource-Optimizer Agent with MCP weather tool access
- Build Streamlit web interface

### Phase 2: Testing (Weeks 5-6)
- Unit tests for all agent logic
- MCP integration tests (tool calling, error handling, permissions)
- Property-based tests for core properties
- Integration tests for end-to-end flows
- Security testing (encryption, PII masking, MCP permissions)
- Performance testing (load, latency)

### Phase 3: Pilot Deployment (Weeks 7-8)
- Deploy to AWS production environment
- Onboard 50 farmers in pilot village
- Monitor system performance and errors
- Collect user feedback
- Iterate based on feedback

### Phase 4: Hackathon Submission (Week 9)
- Prepare demo and presentation
- Document architecture and design decisions
- Submit to AI for Bharat hackathon

---

## MVP Risk Mitigation

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Claude 3.5 Sonnet API rate limiting | Medium | High | Implement request queuing and caching |
| Bedrock Knowledge Base indexing delays | Low | Medium | Pre-index datasets before launch |
| PlantVillage image accuracy issues | Low | High | Use ensemble of multiple disease identifiers |
| PM-Kisan scheme data outdated | Medium | Medium | Set up daily data refresh from data.gov.in |
| DynamoDB throttling under load | Low | High | Enable auto-scaling and provisioned capacity |
| MCP Server unavailability | Medium | Medium | Implement fallback to cached data and retry logic |
| MCP tool permission issues | Low | High | Thorough testing of permission system before launch |
| User adoption in pilot village | High | High | Conduct training sessions and provide support |

---

## MVP Metrics and KPIs

### System Metrics

- **Query Success Rate**: % of queries that return valid responses (Target: 95%)
- **Average Response Time**: Mean time from query to response (Target: < 3 seconds)
- **P95 Response Time**: 95th percentile response time (Target: < 5 seconds)
- **Error Rate**: % of queries that fail (Target: < 1%)
- **Uptime**: % of time system is available (Target: 99.5%)

### Agent Metrics

- **Disease Identification Accuracy**: % of correct disease IDs on test images (Target: 80%)
- **Scheme Eligibility Accuracy**: % of correct PM-Kisan eligibility assessments (Target: 90%)
- **Irrigation Recommendation Validity**: % of valid irrigation recommendations (Target: 90%)
- **Multi-Agent Coordination Success**: % of complex queries handled by multiple agents (Target: 95%)
- **MCP Tool Success Rate**: % of successful MCP tool calls (Target: 95%)
- **MCP Tool Latency**: Average time for MCP tool calls (Target: < 2 seconds)

### User Metrics

- **Farmer Onboarding**: # of farmers using system (Target: 50)
- **Daily Active Users**: # of farmers using system daily (Target: 30)
- **Query Volume**: # of queries per day (Target: 100+)
- **User Satisfaction**: NPS score (Target: ≥ 40)
- **Feature Adoption**: % of farmers using each feature (Target: 70%+)

### Safety Metrics

- **Guardrail Violations**: # of harmful responses blocked (Target: 0 critical)
- **PII Incidents**: # of PII leaks (Target: 0)
- **Data Breaches**: # of unauthorized access incidents (Target: 0)
- **Audit Trail Completeness**: % of actions logged (Target: 100%)

