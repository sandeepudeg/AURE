# Requirements Document: Unified Rural Ecosystem (URE)

## Introduction

The Unified Rural Ecosystem (URE) is an AI-powered platform designed to serve rural communities in India by providing intelligent, multi-agent assistance for agricultural, policy, and resource management. The system leverages Amazon Bedrock and Strands Agents SDK to orchestrate specialized AI agents that address farmer needs across three primary domains: agricultural expertise, government policy navigation, and resource optimization.

The architecture uses a supervisor-worker pattern where the Strands Supervisor Agent (powered by Claude 3.5 Sonnet) routes requests to three specialist agents: Agri-Expert, Policy-Navigator, and Resource-Optimizer. All data is grounded in official Indian government datasets via RAG (Retrieval-Augmented Generation).

## Glossary

- **Strands Supervisor Agent**: Orchestration agent using Claude 3.5 Sonnet on Bedrock; routes user requests to specialist agents without solving problems directly
- **Agri-Expert Agent**: Specialist agent for agricultural image analysis, disease/pest identification, and market price retrieval
- **Policy-Navigator Agent**: Specialist agent for government scheme eligibility, subsidy information, and policy guidance
- **Resource-Optimizer Agent**: Python-based tool (not LLM-powered) for irrigation timing and water management logic
- **Amazon Bedrock**: AWS service providing Claude 3.5 Sonnet model and Knowledge Base capabilities
- **Claude 3.5 Sonnet**: Foundation model used for all LLM-based agents; supports multimodal input (text, images)
- **Bedrock Knowledge Base**: Vector database (Pinecone or OpenSearch) for RAG on government schemes and agricultural data
- **Amazon S3**: Cloud storage for images, datasets (Mandi prices, government PDFs, PlantVillage images)
- **Amazon DynamoDB**: NoSQL database storing conversation history and user context
- **Amazon Lambda**: Serverless compute for request handling and agent orchestration
- **Amazon API Gateway**: REST API endpoint for frontend communication
- **Mandi Prices (Agmarknet)**: Daily agricultural market prices from Government of India for crops across districts
- **RAG (Retrieval-Augmented Generation)**: Technique to ground LLM responses with official data from Knowledge Base
- **Multimodal**: System capability to process text, voice, and images
- **Bedrock Guardrails**: Safety mechanisms to prevent harmful advice and off-topic responses
- **S3 Bucket (knowledge-base-bharat)**: Dedicated bucket for storing datasets and documents for Knowledge Base indexing
- **PlantVillage Dataset**: 50,000+ images of healthy and diseased crop leaves for grounding image analysis
- **data.gov.in**: Open Government Data Portal source for scheme information (PM-Kisan, PKVY, etc.)
- **AgriFieldNet**: Geospatial crop data from Radiant Earth for Bihar, Odisha, Rajasthan, UP
- **IMD Agro-Met Data**: Indian Meteorological Department historical rainfall and temperature patterns
- **Model Context Protocol (MCP)**: Standardized protocol for AI agents to access external tools and services
- **MCP Client**: Central hub managing tool requests from agents and responses from external services
- **MCP Server**: Service providing standardized access to external APIs (Agmarknet, Weather, Government APIs)
- **MCP Tool Registry**: Centralized registry storing metadata about available MCP tools (parameters, permissions, timeouts)
- **Tool Permissions**: Access control mechanism ensuring agents can only use authorized MCP tools
- **Circuit Breaker Pattern**: Failure handling mechanism that temporarily disables failing MCP tools and falls back to alternatives

---

## Technology Stack and Toolchain

### Core AI/ML Services

| Component | Technology | Purpose | Details |
| --- | --- | --- | --- |
| **Foundation Model** | Claude 3.5 Sonnet (via Amazon Bedrock) | LLM backbone for all agents | Multimodal (text, images), supports tool calling, code interpretation |
| **Agent Orchestration** | Strands Agents SDK | Multi-agent coordination and execution | Manages agent loops, tool calling, session management |
| **Knowledge Retrieval** | Amazon Bedrock Knowledge Base | RAG implementation for grounded responses | Indexes documents, performs semantic search |
| **Vector Database** | Amazon OpenSearch Serverless or Pinecone | Stores embeddings for semantic search | Powers visual RAG for PlantVillage images and policy documents |
| **Embeddings** | Amazon Titan Multimodal Embeddings | Converts images and text to vectors | Used for image similarity search and document indexing |
| **Safety & Guardrails** | Amazon Bedrock Guardrails | Content filtering and safety validation | Prevents hallucinations, blocks harmful advice, redacts PII |

### AWS Infrastructure Services

| Component | Technology | Purpose | Details |
| --- | --- | --- | --- |
| **Compute** | AWS Lambda | Serverless function execution | Handles API requests, image processing, agent invocation |
| **API Management** | Amazon API Gateway | REST API endpoint | Routes requests from frontend to Lambda functions |
| **Data Storage** | Amazon S3 | Object storage for datasets and images | Stores PlantVillage images, Agmarknet CSVs, government PDFs, user uploads |
| **Database** | Amazon DynamoDB | NoSQL database | Stores conversation history, user context, session state |
| **Encryption** | AWS KMS (Key Management Service) | Data encryption at rest | Encrypts sensitive data in DynamoDB and S3 |
| **Networking** | AWS VPC, HTTPS/TLS | Secure communication | Encrypts data in transit between components |
| **Monitoring** | Amazon CloudWatch | Logging and observability | Tracks agent decisions, audit trails, performance metrics |
| **IAM** | AWS Identity and Access Management | Access control | Manages permissions for Lambda, S3, DynamoDB access |

### Data Sources and Datasets

| Dataset | Source | Format | Use Case | Update Frequency |
| --- | --- | --- | --- | --- |
| **Agmarknet Mandi Prices** | Government of India (agmarknet.gov.in) | CSV | Market price lookups for crop selling decisions | Daily |
| **PlantVillage Dataset** | Kaggle / GitHub (spMohanty) | Images (JPG) | Disease identification via image analysis | Static (50,000+ images) |
| **Government Schemes** | data.gov.in | PDF/CSV | Policy eligibility and subsidy information | Monthly |
| **Village Amenities** | Census 2011 (data.gov.in) | CSV | Infrastructure and eligibility checks | Static |
| **AgriFieldNet** | Radiant Earth Foundation | GeoTIFF | Geospatial crop data for region-specific recommendations | Seasonal |
| **IMD Agro-Met Data** | Indian Meteorological Department | JSON/CSV | Weather forecasts and historical patterns | Daily |

### Frontend and Integration Technologies

| Component | Technology | Purpose | Details |
| --- | --- | --- | --- |
| **Web Interface** | Streamlit or AWS Amplify | User-facing web application | Handles text/image uploads, displays agent responses |
| **Mobile/Chat** | WhatsApp Business API or Telegram Bot API | Multi-channel access | Enables farmers to interact via messaging apps |
| **Voice Interface** | Amazon Transcribe | Speech-to-text conversion | Converts voice messages to text for agent processing |
| **Text-to-Speech** | Amazon Polly | Voice output | Converts agent responses to audio for voice-based users |
| **Translation** | Amazon Translate | Multi-language support | Translates responses to regional languages (Hindi, Marathi, Kannada, etc.) |

### Development and Deployment Tools

| Tool | Purpose | Details |
| --- | --- | --- |
| **Python 3.9+** | Primary development language | Used for Lambda functions, agent logic, data processing |
| **Boto3** | AWS SDK for Python | Interacts with Bedrock, S3, DynamoDB, Lambda, etc. |
| **Strands SDK** | Agent framework | Provides @tool decorator, Agent class, session management |
| **FastAPI or Flask** | Web framework (optional) | Can wrap Lambda functions for local testing |
| **Pandas** | Data manipulation | Processes CSV datasets (Agmarknet, Census data) |
| **NumPy/SciPy** | Numerical computing | Mathematical models for irrigation calculations (Evapotranspiration) |
| **Pillow (PIL)** | Image processing | Handles image uploads and preprocessing |
| **JSON** | Data serialization | Stores sensor logs, configuration, and API responses |
| **Git/GitHub** | Version control | Manages codebase and collaboration |
| **AWS CloudFormation or Terraform** | Infrastructure as Code | Defines and deploys AWS resources |
| **Docker** | Containerization | Packages Lambda functions and dependencies |
| **pytest** | Testing framework | Unit tests for agent logic and tools |

### External APIs and Services

| Service | Purpose | Integration Method |
| --- | --- | --- |
| **Agmarknet API** | Real-time crop prices | REST API calls from Agri-Expert agent |
| **Weather APIs** | Weather forecasts and historical data | Lambda function fetches from IMD or OpenWeather |
| **Government Scheme APIs** | Policy eligibility checks | Bedrock Knowledge Base retrieval or direct API calls |
| **SMS/Email Services** | Notifications to farmers | AWS SNS (Simple Notification Service) |
| **Payment Gateway** | Optional: Success-based fee collection | Razorpay or AWS Payment Cryptography |

### Data Processing and Analytics

| Component | Technology | Purpose |
| --- | --- | --- |
| **ETL Pipeline** | AWS Glue or Lambda + Pandas | Ingests and transforms datasets into S3 |
| **Data Validation** | Custom Python scripts | Ensures data quality before indexing in Knowledge Base |
| **Vector Indexing** | OpenSearch Ingestion or Pinecone SDK | Converts documents/images to embeddings |
| **Query Analytics** | Amazon Athena or QuickSight | Analyzes agent usage patterns and farmer queries |
| **Audit Logging** | CloudWatch Logs + S3 | Maintains compliance and explainability records |

### Security and Compliance Tools

| Tool | Purpose | Details |
| --- | --- | --- |
| **AWS Secrets Manager** | Credential management | Stores API keys, database passwords securely |
| **AWS WAF** | Web Application Firewall | Protects API Gateway from attacks |
| **VPC Security Groups** | Network access control | Restricts traffic to Lambda, DynamoDB, S3 |
| **Data Encryption** | AWS KMS + TLS | Encrypts data at rest and in transit |
| **Audit Trail** | CloudTrail | Logs all AWS API calls for compliance |
| **PII Detection** | Amazon Macie or custom regex | Identifies and masks sensitive information |

### Deployment and Monitoring

| Tool | Purpose | Details |
| --- | --- | --- |
| **AWS SAM (Serverless Application Model)** | Infrastructure deployment | Simplifies Lambda and API Gateway setup |
| **CloudWatch Dashboards** | Real-time monitoring | Visualizes agent performance, error rates, latency |
| **CloudWatch Alarms** | Alerting | Notifies on failures, high latency, or quota breaches |
| **X-Ray** | Distributed tracing | Traces requests through Lambda, Bedrock, DynamoDB |
| **Cost Explorer** | Budget tracking | Monitors AWS spending and optimizes costs |

### Optional/Future Technologies

| Technology | Purpose | Timeline |
| --- | --- | --- |
| **BharatGen (Sovereign LLM)** | Replace Claude with Indian LLM | Phase 3 (2027) |
| **IoT Sensors** | Real-time soil/weather data | Phase 2 (Q3-Q4 2026) |
| **Federated Learning** | Privacy-preserving model training | Phase 3+ (2027+) |
| **Blockchain** | Immutable audit trails for subsidies | Phase 4 (2028+) |
| **5G/Edge Computing** | Low-latency processing in rural areas | Phase 4 (2028+) |

---

## Toolchain Integration Flow

```
User Input (Web/WhatsApp/Voice)
    ↓
Amazon API Gateway
    ↓
AWS Lambda (Request Handler)
    ↓
Strands Supervisor Agent (Claude 3.5 Sonnet on Bedrock)
    ├─→ Agri-Expert Agent
    │   ├─→ Amazon S3 (Image retrieval)
    │   ├─→ Amazon OpenSearch (PlantVillage embeddings)
    │   ├─→ Bedrock Knowledge Base (Disease metadata)
    │   └─→ External APIs (Agmarknet prices)
    │
    ├─→ Policy-Navigator Agent
    │   ├─→ Bedrock Knowledge Base (Government schemes)
    │   ├─→ Amazon DynamoDB (Village eligibility data)
    │   └─→ data.gov.in (Scheme information)
    │
    └─→ Resource-Optimizer Agent
        ├─→ Amazon S3 (Sensor JSON logs)
        ├─→ Python Code Interpreter (Evapotranspiration calculations)
        └─→ Weather APIs (Forecasts)

    ↓
Bedrock Guardrails (Safety validation)
    ↓
Amazon Translate (Multi-language conversion)
    ↓
Amazon Polly (Text-to-speech, optional)
    ↓
Response to User (via API Gateway / WhatsApp / Voice)
    ↓
Amazon DynamoDB (Store conversation history)
    ↓
CloudWatch (Audit logging)
```

## Requirements

### Requirement 1: User Interface and Entry Point

**User Story:** As a farmer, I want to interact with the system through multiple channels (web app, WhatsApp, or voice), so that I can access agricultural assistance using my preferred communication method.

#### Acceptance Criteria

1. WHEN a user sends a message through any supported interface (web, WhatsApp, or voice), THE System SHALL receive the input through Amazon API Gateway and route it to a Lambda function
2. WHEN a user uploads an image through the interface, THE System SHALL store the image in S3 bucket (knowledge-base-bharat) and make it available for analysis
3. WHEN a user sends a voice message, THE System SHALL convert it to text before routing to the Supervisor Agent
4. WHEN a user sends a request, THE Lambda function SHALL invoke the Strands Supervisor Agent with the user input and conversation history from DynamoDB
5. THE System SHALL maintain a consistent user experience across all interface channels

_Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

---

### Requirement 2: Orchestration and Routing via Strands Supervisor

**User Story:** As a system architect, I want the Supervisor Agent to intelligently route requests to specialist agents, so that each query is handled by the most appropriate expert.

#### Acceptance Criteria

1. WHEN a user sends a request, THE Strands Supervisor Agent (Claude 3.5 Sonnet on Bedrock) SHALL analyze the request and determine which specialist agent(s) should handle it
2. WHEN a farmer sends a photo of a diseased leaf, THE Supervisor Agent SHALL invoke the Agri-Expert Agent tool with the image URL from S3
3. WHEN a farmer asks about government subsidies or schemes, THE Supervisor Agent SHALL invoke the Policy-Navigator Agent tool with a retrieval_tool to query the Bedrock Knowledge Base
4. WHEN a farmer asks about water management or irrigation, THE Supervisor Agent SHALL invoke the Resource-Optimizer Agent tool with weather/soil JSON data
5. WHEN a request requires multiple specialist agents, THE Supervisor Agent SHALL coordinate responses from all relevant agents and synthesize a comprehensive answer
6. WHEN the Supervisor Agent generates a response, THE System SHALL apply Bedrock Guardrails to validate content safety before returning to user

_Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

---

### Requirement 3: Conversation History and State Management

**User Story:** As a farmer, I want the system to remember my previous conversations and context, so that I don't have to repeat information in follow-up queries.

#### Acceptance Criteria

1. WHEN a user sends a message, THE System SHALL store the conversation in DynamoDB with user ID, timestamp, and message content
2. WHEN a user references earlier information (e.g., "Earlier you mentioned I have 5 acres of wheat"), THE System SHALL retrieve conversation history from DynamoDB and pass it to the Supervisor Agent
3. WHEN a conversation session ends, THE System SHALL persist all conversation history in DynamoDB for future reference
4. WHEN a user starts a new session, THE System SHALL load relevant conversation history from DynamoDB to provide continuity
5. WHEN retrieving conversation history, THE System SHALL include user context (farm size, crop type, location) for personalized responses

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

---

### Requirement 4: Agricultural Image Analysis via Agri-Expert Agent

**User Story:** As a farmer, I want to upload photos of my crops and receive expert analysis on diseases, pests, and treatment recommendations, so that I can address agricultural problems quickly.

#### Acceptance Criteria

1. WHEN a farmer uploads a leaf or crop image, THE System SHALL store it in S3 (knowledge-base-bharat) and pass the image URL to the Agri-Expert Agent
2. WHEN the Agri-Expert Agent receives an image, THE System SHALL invoke Claude 3.5 Sonnet's multimodal capabilities on Bedrock to analyze the image
3. WHEN an image is analyzed, THE Agri-Expert Agent SHALL identify any diseases, pests, or health issues present using PlantVillage Dataset as grounding
4. WHEN a disease or pest is identified, THE Agri-Expert Agent SHALL provide treatment recommendations including organic and chemical options
5. WHEN a disease is identified, THE Supervisor Agent SHALL simultaneously invoke the Policy-Navigator Agent to check for available government subsidies or schemes related to that disease
6. WHEN treatment recommendations are provided, THE System SHALL include cost estimates and subsidy information retrieved from the Bedrock Knowledge Base

_Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

---

### Requirement 5: Market Price Information via Agri-Expert Agent

**User Story:** As a farmer, I want to access current market prices for my crops, so that I can make informed decisions about when and where to sell.

#### Acceptance Criteria

1. WHEN a farmer asks about crop prices, THE Agri-Expert Agent SHALL use the retrieval_tool to query the Bedrock Knowledge Base for Mandi prices from Agmarknet dataset
2. WHEN price data is retrieved, THE System SHALL provide prices for the farmer's region and crop type from the S3-stored Agmarknet CSV data
3. WHEN multiple markets are available, THE System SHALL compare prices across different Mandi locations and recommend the best market
4. WHEN historical price trends are requested, THE System SHALL retrieve and display price history from the Agmarknet dataset stored in S3
5. WHEN price data is queried, THE System SHALL ensure data freshness by using the latest Agmarknet dataset (updated daily)

_Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

---

### Requirement 6: Government Scheme Navigation via Policy-Navigator Agent

**User Story:** As a farmer, I want to find government schemes and subsidies I'm eligible for, so that I can access financial support and resources.

#### Acceptance Criteria

1. WHEN a farmer asks about government schemes, THE Policy-Navigator Agent SHALL use the retrieval_tool to query the Bedrock Knowledge Base containing government scheme PDFs
2. WHEN a scheme is identified, THE Policy-Navigator Agent SHALL provide eligibility criteria, application process, and subsidy amounts from data.gov.in sources
3. WHEN a farmer describes their situation, THE Policy-Navigator Agent SHALL use RAG to match them with relevant schemes (e.g., PM-Kisan, PKVY, Paramparagat Krishi Vikas Yojana)
4. WHEN multiple schemes apply, THE System SHALL present all options with comparison information retrieved from the Knowledge Base
5. WHEN a farmer asks about a specific scheme, THE System SHALL provide accurate, ground-truthed information from official government sources stored in S3
6. WHEN scheme information is retrieved, THE System SHALL include eligibility criteria, subsidy amounts, and application deadlines

_Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

---

### Requirement 7: Resource Optimization and Irrigation Management

**User Story:** As a farmer, I want recommendations on irrigation timing and water management, so that I can optimize water usage and improve crop yield.

#### Acceptance Criteria

1. WHEN a farmer provides weather and soil data (JSON format), THE Resource-Optimizer Agent SHALL analyze the data using Python-based logic
2. WHEN irrigation timing is calculated, THE System SHALL provide specific recommendations based on rainfall patterns and soil moisture from IMD Agro-Met Data
3. WHEN sustainability concerns are present, THE Resource-Optimizer Agent SHALL suggest water-efficient irrigation methods
4. WHEN historical weather data is available, THE System SHALL use IMD Agro-Met data to inform recommendations
5. WHEN crop type and field size are known, THE System SHALL provide irrigation recommendations tailored to those parameters
6. WHEN resource optimization is requested, THE System SHALL retrieve geospatial crop data from AgriFieldNet for region-specific recommendations

_Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

---

### Requirement 8: Data Integration and Bedrock Knowledge Base

**User Story:** As a system administrator, I want to integrate ground-truthed Indian agricultural datasets into the system, so that all recommendations are based on accurate, official data.

#### Acceptance Criteria

1. WHEN the system is initialized, THE Knowledge Base SHALL be populated with official datasets from Agmarknet, data.gov.in, and IMD
2. WHEN a Bedrock Knowledge Base is created, THE System SHALL index agricultural datasets including Mandi prices, government schemes, and weather data using vector database (Pinecone or OpenSearch)
3. WHEN new data is available, THE System SHALL support updating the knowledge base with fresh information from S3 bucket (knowledge-base-bharat)
4. WHEN RAG queries are performed, THE System SHALL retrieve information from the indexed knowledge base and ground responses in official data
5. WHEN data quality issues are detected, THE System SHALL flag them for administrator review
6. WHEN datasets are indexed, THE System SHALL store PlantVillage images, Agmarknet CSVs, government scheme PDFs, and AgriFieldNet geospatial data in S3

_Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

---

### Requirement 9: Safety and Guardrails

**User Story:** As a system administrator, I want to ensure the AI provides safe, accurate, and on-topic responses, so that farmers receive reliable guidance.

#### Acceptance Criteria

1. WHEN an agent generates a response, THE System SHALL apply Amazon Bedrock Guardrails to validate content safety
2. WHEN a response contains potentially harmful advice, THE System SHALL reject it and provide a safe alternative
3. WHEN a user asks off-topic questions, THE System SHALL redirect them to relevant agricultural topics
4. WHEN medical or legal advice is requested, THE System SHALL decline and suggest appropriate professional resources
5. WHEN guardrail violations occur, THE System SHALL log the incident for review
6. WHEN responses are generated, THE System SHALL ensure they are grounded in official data and not hallucinated

_Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

---

### Requirement 10: Scalability and Performance

**User Story:** As a system architect, I want the system to scale from supporting a few users to thousands of concurrent users, so that the platform can grow with demand.

#### Acceptance Criteria

1. WHEN user load increases, THE System SHALL automatically scale Lambda functions to handle increased requests
2. WHEN multiple users submit requests simultaneously, THE System SHALL process them without degradation in response time
3. WHEN S3 storage grows, THE System SHALL maintain fast image retrieval and processing
4. WHEN DynamoDB usage increases, THE System SHALL maintain consistent query performance through auto-scaling
5. WHEN system load is high, THE System SHALL maintain response times under 5 seconds for typical queries
6. WHEN Bedrock API calls increase, THE System SHALL handle concurrent invocations of Claude 3.5 Sonnet without throttling

_Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

---

### Requirement 11: Multi-Agent Coordination via Strands Agents SDK

**User Story:** As a system designer, I want multiple specialist agents to work together seamlessly, so that complex queries receive comprehensive answers.

#### Acceptance Criteria

1. WHEN a query requires multiple agents, THE Supervisor Agent SHALL coordinate their execution using Strands Agents SDK
2. WHEN the Agri-Expert identifies a disease, THE Policy-Navigator Agent SHALL simultaneously search for related subsidies via the Knowledge Base
3. WHEN responses from multiple agents are received, THE Supervisor Agent SHALL synthesize them into a coherent answer
4. WHEN agents have conflicting information, THE System SHALL prioritize ground-truthed data from official sources
5. WHEN agent responses are combined, THE System SHALL maintain response coherence and avoid duplication
6. WHEN agents communicate, THE System SHALL use Strands Agents SDK tool calling mechanism for reliable coordination

_Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

---

### Requirement 12: Data Privacy and Security

**User Story:** As a farmer, I want my personal information and conversation history to be protected, so that my data remains private and secure.

#### Acceptance Criteria

1. WHEN user data is stored in DynamoDB, THE System SHALL encrypt it at rest using AWS KMS
2. WHEN data is transmitted between components, THE System SHALL use HTTPS/TLS encryption
3. WHEN a user requests data deletion, THE System SHALL remove their conversation history and personal information from DynamoDB
4. WHEN access logs are generated, THE System SHALL maintain audit trails for compliance
5. WHEN sensitive information is detected, THE System SHALL mask it in logs and monitoring systems
6. WHEN images are stored in S3, THE System SHALL apply appropriate access controls and encryption

_Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

---

### Requirement 13: Model Context Protocol (MCP) Integration

**User Story:** As a system architect, I want to standardize external service access through MCP, so that agents can reliably access market prices, weather data, and government APIs without tight coupling.

#### Acceptance Criteria

1. WHEN the system initializes, THE MCP Client SHALL be configured with access to three MCP Servers: Agmarknet, Weather, and Government API
2. WHEN an agent requests market price data, THE MCP Client SHALL route the request to the Agmarknet MCP Server using standardized tool calling
3. WHEN an MCP tool is invoked, THE System SHALL verify the requesting agent has permission to use that tool before execution
4. WHEN an MCP tool call fails, THE System SHALL retry up to 3 times with exponential backoff before returning an error
5. WHEN an MCP tool is invoked, THE System SHALL log the tool call, parameters, response, execution time, and success status to CloudWatch
6. WHEN an MCP server becomes unavailable, THE System SHALL gracefully fall back to cached data or alternative data sources
7. WHEN an MCP tool call involves farmer data, THE System SHALL ensure no PII is transmitted to external services without proper anonymization

**Available MCP Tools**:
- `get_mandi_prices`: Fetch current market prices for crops by location
- `get_price_trends`: Retrieve historical price data for trend analysis
- `get_nearby_mandis`: Discover nearby market locations
- `get_crop_availability`: Check crop availability in specific regions
- `get_current_weather`: Retrieve real-time weather conditions
- `get_weather_forecast`: Get weather forecasts for planning
- `get_rainfall_data`: Access rainfall patterns and predictions
- `get_soil_conditions`: Retrieve soil moisture and nutrient data
- `search_schemes`: Query government schemes database
- `check_eligibility`: Validate farmer eligibility for schemes
- `get_subsidy_info`: Retrieve subsidy amounts and details
- `get_application_status`: Check application status for schemes

_Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_

---

### Requirement 14: MCP Tool Registry and Discovery

**User Story:** As a system administrator, I want a centralized registry of all MCP tools, so that agents can discover available tools and understand their parameters and permissions.

#### Acceptance Criteria

1. WHEN the system initializes, THE MCP Tool Registry SHALL be populated with metadata for all available MCP tools
2. WHEN an agent queries for available tools, THE System SHALL return tool metadata including parameters, permissions, timeouts, and retry policies
3. WHEN a new MCP tool is added, THE System SHALL register it in the Tool Registry with complete metadata
4. WHEN tool metadata is updated, THE System SHALL propagate changes to all agents without requiring system restart
5. WHEN an agent attempts to use a tool, THE System SHALL validate the tool exists in the registry before execution
6. WHEN tool metadata includes permission requirements, THE System SHALL enforce access control based on agent roles

**Tool Registry Metadata Structure**:
- tool_id: Unique identifier for the tool
- server_name: Name of the MCP server providing the tool
- description: Human-readable description of tool functionality
- parameters_schema: JSON schema defining required and optional parameters
- permissions: List of agent roles authorized to use the tool
- timeout_ms: Maximum execution time before timeout
- retry_count: Number of retry attempts on failure
- circuit_breaker: Configuration for failure threshold and recovery timeout

_Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

---

### Requirement 15: MCP Error Handling and Resilience

**User Story:** As a system architect, I want robust error handling for MCP tool failures, so that the system gracefully degrades when external services are unavailable.

#### Acceptance Criteria

1. WHEN an MCP server fails to respond within timeout, THE System SHALL log the incident and attempt reconnection
2. WHEN an MCP tool is not found, THE System SHALL return a user-friendly error message and suggest alternative data sources
3. WHEN an MCP server authentication fails, THE System SHALL retry with token refresh and fall back to cached data
4. WHEN an agent lacks permission for an MCP tool, THE System SHALL block the request and log a security incident
5. WHEN an MCP tool failure rate exceeds threshold, THE System SHALL activate circuit breaker and temporarily disable the tool
6. WHEN circuit breaker is active, THE System SHALL automatically retry after recovery timeout
7. WHEN MCP fallback is triggered, THE System SHALL provide cached data with timestamp disclaimer to the user

**Error Handling Strategies**:
- MCP Server Unavailable: Fall back to cached data from last 24 hours
- Tool Not Found: Suggest alternative tools or manual data entry
- Authentication Failure: Retry with token refresh, then use cached data
- Permission Denied: Block request and log security incident
- Circuit Breaker Triggered: Use alternative data sources or cached results

_Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_

---



### Gram-Setu Identity (Supervisor Agent)

The Strands Supervisor Agent operates as "Gram-Setu" (Village Bridge), bridging advanced technology with rural livelihoods. The agent:
- Analyzes user input to classify queries into three domains: Agricultural, Policy, or Resource-based
- Routes to appropriate specialist agents without solving problems directly
- Synthesizes responses from multiple agents when complex queries require cross-domain expertise
- Uses simple, non-technical language avoiding jargon like "optimization" or "parameters"
- Prioritizes lowest-cost solutions first to ensure sustainability
- Maintains empathetic, encouraging tone while being professional
- Operates with contextual awareness of user persona (marginalized farmers or rural entrepreneurs with limited resources)
- Delivers actionable, resource-efficient, and sustainable advice

**System Prompt for Gram-Setu:**
```
You are the "Gram-Setu" (Village Bridge) AI Orchestrator. Your mission is to bridge the gap between advanced technology and rural livelihoods.

CONTEXTUAL AWARENESS:
- User Persona: Marginalized farmers or rural entrepreneurs with limited resources
- Technical Environment: Operating within an AWS ecosystem (Bedrock, Strands, S3)
- Primary Value: Delivering actionable, resource-efficient, and sustainable advice

TASK:
Analyze the user's input to determine which specialized Strands Agent(s) are required:
1. [AGRI_AGENT]: For crop health, pest IDs, or market price requests
2. [GOVT_POLICY_AGENT]: For subsidies, welfare schemes, or document help
3. [RESOURCE_AGENT]: For water management, solar energy logs, or weather planning

EXECUTION STEPS:
1. CLASSIFY: Identify the domain of the query
2. DELEGATE: Pass the intent and relevant data (like S3 file paths) to the specific agent
3. SYNTHESIZE: If multiple agents are involved, merge their outputs into a "Life-Plan"

CONSTRAINTS:
- Use simple, non-technical language (avoid words like 'optimization' or 'parameters')
- Always suggest the lowest-cost option first to ensure sustainability
- If the query is ambiguous, ask a clarifying question about their specific location or crop
```

### Agri-Expert Agent Personality

The Agri-Expert operates as a Senior Agricultural Scientist specializing in Indian conditions:
- Identifies 50+ common Indian crop diseases via image analysis using PlantVillage dataset grounding
- Masters Integrated Pest Management (IPM) focusing on organic/low-cost interventions
- Understands real-time Mandi (market) dynamics via Agmarknet API integration
- Provides treatment recommendations: Organic first, then low-cost chemical, chemical as last resort
- Uses `fetch_mandi_prices` tool for district-specific market data
- Recommends best "Net Profit" option (Price minus estimated transport cost)
- Tone: Supportive, like a wise village elder who understands modern science

**System Prompt for Agri-Expert:**
```
You are a Senior Agricultural Scientist specializing in Indian soil and climate conditions.

KNOWLEDGE DOMAIN:
- Expertise in identifying 50+ common Indian crop diseases via image analysis
- Mastery of IPM (Integrated Pest Management) focusing on organic/low-cost interventions
- Real-time understanding of Mandi (market) dynamics

INSTRUCTIONS FOR IMAGE ANALYSIS (S3 INPUT):
When an image is provided from the S3 bucket:
1. Identify: State the likely disease or nutrient deficiency
2. Probability: Give a confidence level (e.g., "I am 80% sure this is Late Blight")
3. Actionable Fix:
   - Immediate Step: (e.g., "Remove the infected leaves immediately")
   - Low-Cost Treatment: (e.g., "Mix neem oil with soap water")
   - Chemical Option: Only suggest as a last resort

MARKET LINKAGE LOGIC:
If the user asks about selling crops:
1. Use the `fetch_mandi_prices` tool for their district
2. Compare the price at the nearest 3 Mandis
3. Suggest the best "Net Profit" option (Price minus estimated transport cost)

TONE:
Supportive, like a wise village elder who understands modern science
```

### Resource-Optimizer Agent Logic

The Resource-Optimizer operates as a Sustainability Intelligence Agent:
- Receives JSON logs from S3 containing soil_moisture_index (0.0-1.0), weather_forecast, electricity_availability
- Applies deterministic logic: If moisture > 0.7, advise AGAINST irrigation
- If moisture < 0.3 and rain predicted within 12 hours, advise "Wait for rain"
- Cross-references electricity hours to suggest optimal pump operation times
- Provides "Daily Resource Plan" with specific "Stop/Start" instructions
- Maximizes crop yield while minimizing water and electricity usage
- Uses Python-based code interpreter for mathematical models (e.g., Evapotranspiration calculations)

**System Prompt for Resource-Optimizer:**
```
You are a Sustainability Intelligence Agent. Your goal is to maximize crop yield while minimizing water and electricity usage.

DATA HANDLING:
You will receive JSON logs from S3 containing:
- soil_moisture_index: (0.0 to 1.0)
- weather_forecast: (Probability of rain, Temperature)
- electricity_availability: (Hours of grid power)

REASONING PROCESS:
1. Check the moisture level. If above 0.7, strictly advise AGAINST irrigation
2. If moisture is low (<0.3), check the weather forecast. If rain is predicted within 12 hours, advise "Wait for rain" to save water/energy
3. If irrigation is needed, cross-reference with electricity hours to suggest the best time to turn on pumps

OUTPUT:
Provide a "Daily Resource Plan" with specific "Stop/Start" instructions
```

### Policy-Navigator Agent Approach

The Policy-Navigator operates as a Government Scheme Expert:
- Performs RAG on government scheme PDFs from Bedrock Knowledge Base
- Matches farmers to relevant schemes (PM-Kisan, PKVY, etc.) based on their situation
- Provides eligibility criteria, application process, subsidy amounts, and deadlines
- Ensures responses are grounded in official data without hallucination
- Coordinates with Agri-Expert when disease-specific subsidies are available
- Uses citations from Knowledge Base to show exact source of information

**System Prompt for Policy-Navigator:**
```
You are a Legal & Welfare Officer specializing in Indian government schemes.

ROLE:
Search the Bedrock Knowledge Base to find the exact eligibility criteria for schemes. Perform RAG on government scheme PDFs from data.gov.in.

INSTRUCTIONS:
1. Match farmers to relevant schemes (PM-Kisan, PKVY, etc.) based on their situation
2. Provide eligibility criteria, application process, subsidy amounts, and deadlines
3. Ensure responses are grounded in official data without hallucination
4. Always cite the source document and page number from the Knowledge Base
5. Coordinate with Agri-Expert when disease-specific subsidies are available

TONE:
Clear, professional, and farmer-first. Simplify legal language into actionable steps
```

## Competitive Positioning

The URE system differentiates from existing agritech platforms through:

### Modularity
The supervisor-worker architecture is "pluggable"—additional agents (Education, Healthcare) can be added using the same framework without changing core infrastructure.

### Multi-Agent Synthesis
Unlike siloed apps (one for weather, another for schemes), URE synthesizes cross-domain expertise in single responses. The Supervisor doesn't just call agents sequentially; it orchestrates them to deliver holistic recommendations.

### Low-Code Scalability
Using Strands SDK enables easier updates and scaling compared to rigid codebases of older agritech startups. New agents can be added by defining system prompts and tools without rewriting infrastructure.

### Contextual Synthesis
The system doesn't just provide three separate tools; it orchestrates them to deliver holistic recommendations. When a farmer asks a complex question, the Supervisor automatically determines which agents to invoke and synthesizes their outputs.

### Proactive vs. Reactive
Existing apps wait for user queries. URE's architecture (using AWS Lambda and S3 triggers) allows for proactive alerts. If sensor data in S3 shows a drop in soil moisture, the Resource-Agent notifies the user before the crop is stressed.

### Orchestration vs. Simple Search
While a bot like Kisan e-Mitra answers policy questions, URE's Strands Supervisor can reason across domains. If the Agri-Agent detects a pest, the Supervisor automatically triggers the Policy-Agent to check for subsidies on the recommended organic pesticide without the user asking.

### Example Winning Scenario
A farmer asks "What should I plant given water shortage and current government subsidies?" The system:
1. Calls Resource-Optimizer Agent for water availability analysis
2. Calls Policy-Navigator for subsidy-eligible crops
3. Calls Agri-Expert for market prices
4. Supervisor synthesizes: "Plant X (drought-resistant, 20% subsidy available, current market price ₹Y, irrigation needed only 2x per month)"

### Competitive Landscape (2025-2026)

| Solution Category | Key Players | Their Focus | URE's Competitive Advantage |
| --- | --- | --- | --- |
| **Pure Advisory Apps** | AgroStar, DeHaat, Kisan Suvidha | Large-scale, expert-led or rule-based crop advice | Contextual Cross-Talk: Links pest diagnosis directly to government subsidy search without user prompting |
| **Agentic Platforms** | Cropin "Orion", Tech Mahindra "Orion" | Enterprise-grade "Agentic AI" for supply chains | Community-Centric: Built for rural ecosystem, focusing on resource-efficiency (water/electricity) rather than just corporate yield |
| **Government Bots** | Kisan e-Mitra, AgriGOI | Information retrieval for schemes and grievances | Multimodal Reasoning: Processes images (pests) and sensor data (moisture) to provide holistic "Life-Plan" |
| **IoT/Precision Ag** | Fasal, BharatAgri | Use IoT sensors and AI for precision irrigation | Synthesis: Combines disease detection, market prices, and resource optimization in one response |

### Why URE Wins the Professional Track

1. **Verification Loop**: Uses Bedrock Guardrails to prevent "hallucinations" in policy advice—a common flaw in competitors using basic LLM wrappers
2. **Explainability**: Agents show their reasoning (e.g., "Based on 35°C temperature and 10% humidity, I calculated high evaporation rate...")
3. **Scalability**: Serverless architecture (Lambda, Bedrock, S3) scales from 10 to 10,000 users without infrastructure changes
4. **Sovereignty**: Can migrate to sovereign LLMs (like BharatGen) to ensure data privacy and cultural nuance

---

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Core System Properties

**Property 1: Message Routing Consistency**
For any user message from any supported interface (web, WhatsApp, voice), the message SHALL be received by Lambda and routed to the Supervisor Agent without loss or corruption.
Validates: Requirements 1.1, 1.4

**Property 2: Image Storage and Retrieval**
For any image uploaded by a farmer, the image SHALL be stored in S3 (knowledge-base-bharat) with correct metadata and be retrievable via the stored URL.
Validates: Requirements 1.2, 4.1

**Property 3: Voice-to-Text Conversion**
For any voice message from a user, the system SHALL convert it to text using Amazon Transcribe and route the text to the Supervisor Agent.
Validates: Requirements 1.3

**Property 4: Conversation History Persistence**
For any user message, the system SHALL store it in DynamoDB with user ID, timestamp, and content, and retrieve it in subsequent sessions.
Validates: Requirements 3.1, 3.2, 3.3, 3.4

**Property 5: Agent Routing Correctness**
For any user query, the Supervisor Agent SHALL route to the correct specialist agent(s) based on query domain (Agricultural/Policy/Resource).
Validates: Requirements 2.1, 2.2, 2.3, 2.4

**Property 6: Multi-Agent Coordination**
For any query requiring multiple agents, the Supervisor Agent SHALL invoke all relevant agents in parallel and synthesize their responses into a coherent answer.
Validates: Requirements 2.5, 11.1, 11.2, 11.3

**Property 7: Disease Identification Accuracy**
For any crop leaf image from the PlantVillage dataset, the Agri-Expert Agent SHALL identify the disease with accuracy ≥ 80% when compared to ground truth labels.
Validates: Requirements 4.2, 4.3

**Property 8: Treatment Recommendation Completeness**
For any identified disease, the Agri-Expert Agent SHALL provide treatment recommendations including at least one organic option and one chemical option.
Validates: Requirements 4.4

**Property 9: Market Price Accuracy**
For any crop price query, the system SHALL retrieve prices from Agmarknet that match the farmer's region and crop type.
Validates: Requirements 5.1, 5.2, 5.3

**Property 10: Scheme Matching Correctness**
For any farmer situation, the Policy-Navigator Agent SHALL match them with all applicable government schemes from the Knowledge Base.
Validates: Requirements 6.1, 6.3, 6.4

**Property 11: Scheme Information Completeness**
For any government scheme retrieved, the system SHALL include eligibility criteria, subsidy amounts, and application deadlines.
Validates: Requirements 6.2, 6.6

**Property 12: Irrigation Recommendation Validity**
For any weather and soil data provided, the Resource-Optimizer Agent SHALL generate irrigation recommendations based on soil moisture, rainfall forecast, and electricity availability.
Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5

**Property 13: Knowledge Base Indexing**
For any dataset (Agmarknet, government schemes, PlantVillage), the system SHALL index it in the Bedrock Knowledge Base and make it searchable via RAG queries.
Validates: Requirements 8.1, 8.2, 8.3, 8.4

**Property 14: Guardrail Safety Filtering**
For any agent response, the system SHALL apply Bedrock Guardrails and block responses containing harmful advice, off-topic content, or medical/legal guidance.
Validates: Requirements 9.1, 9.2, 9.3, 9.4

**Property 15: Response Grounding**
For any system response, it SHALL cite official data sources (Agmarknet, data.gov.in, IMD) and not contain hallucinated information.
Validates: Requirements 9.6

**Property 16: Scalability Under Load**
For any concurrent user load up to 1000 simultaneous requests, the system SHALL maintain response times under 5 seconds and process all requests without dropping.
Validates: Requirements 10.1, 10.2, 10.4, 10.5, 10.6

**Property 17: Data Encryption**
For any user data stored in DynamoDB or transmitted between components, it SHALL be encrypted using AWS KMS (at rest) and HTTPS/TLS (in transit).
Validates: Requirements 12.1, 12.2

**Property 18: Data Deletion Compliance**
For any user requesting data deletion, the system SHALL remove all their conversation history and personal information from DynamoDB within 24 hours.
Validates: Requirements 12.3

**Property 19: Audit Trail Completeness**
For any agent decision or system action, it SHALL be logged to CloudWatch with timestamp, user ID, action, and outcome for compliance.
Validates: Requirements 12.4, 12.5

**Property 20: PII Masking**
For any sensitive information (Aadhaar, bank account, phone) detected in logs or monitoring systems, it SHALL be automatically masked or redacted.
Validates: Requirements 12.5

### MCP Integration Properties

**Property 21: MCP Tool Registration**
For any MCP tool added to the system, it SHALL be registered in the Tool Registry with complete metadata (parameters, permissions, timeouts) and be discoverable by authorized agents.
Validates: Requirements 13.1, 14.1, 14.2

**Property 22: MCP Tool Access Control**
For any MCP tool request from an agent, the MCP Client SHALL verify the agent has permission to use that tool before executing the request.
Validates: Requirements 13.3, 14.6

**Property 23: MCP Tool Retry Logic**
For any MCP tool call that fails, the system SHALL retry up to 3 times with exponential backoff before returning an error to the requesting agent.
Validates: Requirements 13.4, 15.1

**Property 24: MCP Tool Logging**
For any MCP tool invocation, the system SHALL log the tool call, parameters, response, execution time, and success status for audit and debugging purposes.
Validates: Requirements 13.5, 15.1

**Property 25: MCP Fallback Handling**
For any MCP server that becomes unavailable, the system SHALL gracefully handle the failure and provide cached data or alternative data sources when possible.
Validates: Requirements 13.6, 15.1, 15.7

**Property 26: MCP Data Privacy**
For any MCP tool call involving farmer data, the system SHALL ensure no PII is transmitted to external services without explicit consent and proper anonymization.
Validates: Requirements 13.7, 15.3

**Property 27: MCP Tool Discovery**
For any agent querying available tools, the system SHALL return complete tool metadata including parameters, permissions, and timeout configurations from the Tool Registry.
Validates: Requirements 14.2, 14.3

**Property 28: MCP Circuit Breaker**
For any MCP tool with failure rate exceeding configured threshold, the system SHALL activate circuit breaker, temporarily disable the tool, and automatically retry after recovery timeout.
Validates: Requirements 15.5, 15.6

---

## Responsible AI and Governance

### Responsible AI Parameters for Agriculture Applications

**Fairness**
- Ensure recommendations (fertilizer use, irrigation schedules, crop selection) are unbiased across farm sizes, regions, and socio-economic groups
- Avoid favoring large-scale farms over smallholders
- Example: AI should not recommend expensive inputs only accessible to wealthy farmers

**Reliability & Safety**
- Models must handle uncertainty in weather, soil, and market data
- Fail-safe design: if confidence is low, flag for human agronomist review
- Example: Avoid overconfident pesticide recommendations that could harm crops or ecosystems

**Privacy & Security**
- Protect farmer identity, land ownership records, and yield data
- Use secure data-sharing protocols (e.g., federated learning for soil data)
- Example: Farmer-specific yield predictions should not be exposed to competitors or buyers without consent

**Inclusiveness**
- Design for farmers with varying literacy and digital access
- Support local languages (Marathi, Hindi, Kannada, etc.)
- Provide voice-based interfaces for low-literacy users

**Transparency**
- Explain why a recommendation was made (e.g., "Based on rainfall forecast and soil nitrogen levels, apply 20kg urea")
- Show data sources (satellite, IoT sensors, government guidelines)
- Example: Farmers should see the reasoning behind crop rotation advice

**Accountability**
- Keep audit trails of recommendations and farmer decisions
- Responsibility remains with the farmer/agronomist—AI is a copilot, not a decision-maker
- Example: If AI suggests irrigation and farmer disagrees, the override is logged

**Sustainability**
- Encourage eco-friendly practices (reduced chemical use, water conservation, biodiversity)
- Align with UN SDGs and local agricultural policies
- Example: AI should prioritize organic pest control methods when feasible

### Implementation of Responsible AI

1. **Input Filtering**: Bedrock Guardrails detect "Prompt Injection" or requests for restricted topics (illegal chemical recipes)
2. **Output Grounding**: Guardrails verify agent responses are found in Knowledge Base; blocks hallucinated schemes
3. **PII Redaction**: Automatically detects and masks sensitive data (Aadhaar numbers, bank details) in conversation history
4. **Denied Topics Configuration**:
   - Chemical Hazards: Block advice on creating unregulated or dangerous homemade pesticides
   - Financial Coaching: Policy-Agent explains eligibility but does not give investment advice
   - Hate Speech & Polarization: Filter responses in regional languages for cultural sensitivity
5. **Explainability Logging**: Every agent decision is logged with reasoning for audit trails and compliance

---

## Implementation Architecture and Data Flow

### End-to-End Data Flow

1. **Ingestion**: User uploads a leaf photo → Stored in Amazon S3 (knowledge-base-bharat bucket)
2. **Routing**: Strands Supervisor sees the image → Signals the Agri-Expert Agent
3. **Processing**: 
   - Agri-Expert pulls image from S3
   - Claude 3.5 Sonnet identifies disease (e.g., "Yellow Rust")
   - Policy-Navigator Agent simultaneously checks for "Yellow Rust Subsidies" via Bedrock Knowledge Base
4. **Delivery**: Supervisor combines both answers: "You have Yellow Rust. Use Neem Oil. Also, you can claim a 20% subsidy on organic pesticides under the PM-Kisan scheme."

### Multimodal RAG Pattern (Visual Grounding)

The Agri-Expert uses a "Visual RAG" approach:
1. **Input**: Farmer uploads a query image of their crop
2. **Visual Search**: Lambda function uses Amazon Titan Multimodal Embeddings to generate vector representation
3. **Retrieval**: System searches S3-backed vector database (Amazon OpenSearch) to find 3 most similar images from PlantVillage dataset
4. **Grounding**: Both farmer's image and 3 reference images sent to Claude 3.5 Sonnet with system prompt
5. **Output**: Agent identifies disease and provides treatment from verified metadata

### Knowledge Base Integration

1. **Data Ingestion**: CSV/PDF datasets stored in S3 bucket (knowledge-base-bharat)
2. **Indexing**: Bedrock Knowledge Base indexes agricultural datasets using vector database (Pinecone or OpenSearch)
3. **Retrieval**: When farmer asks about crop price, Strands Agent uses retrieval_tool to query Knowledge Base
4. **Grounding**: Responses grounded in official data from Agmarknet, data.gov.in, IMD, and AgriFieldNet

### Memory Management

**Short-Term (Session) Memory**:
- Strands Agents use ConversationManager that keeps recent messages
- Supervisor remembers context (e.g., "5 acres of wheat") across agent calls
- Uses FileSessionManager for local testing or S3SessionManager for cloud deployment

**Long-Term (Persistent) Memory**:
- Episodic Memory: Stores summaries of past sessions for continuity
- Semantic Memory: Uses Vector Store (OpenSearch/Chroma) to search through historical facts
- Cross-Agent Memory: Supervisor acts as central memory hub, passing context between agents

### Strands SDK Integration

The Strands Agents SDK provides:
- **Agent Initialization**: Define agents with system prompts and tool access
- **Tool Calling**: Agents use @tool decorator to wrap API calls and database queries
- **Agentic Loop**: Agents observe, plan, act, and reflect on outcomes
- **Session Management**: Built-in conversation and state management
- **Code Interpreter**: Agents can run Python code for mathematical models (e.g., Evapotranspiration calculations)

---

## Implementation Roadmap

### Phase 1: MVP & Pilot (Q1-Q2 2026)
- Deployment in 5 "Adopter" villages
- Fine-tuning Strands Agent logic
- Grounding Bedrock RAG with local soil and scheme data
- Integration of PlantVillage dataset for image analysis
- Testing Bedrock Guardrails for safety

### Phase 2: Regional Scaling (Q3-Q4 2026)
- Partnering with 10+ FPOs (Farmer Producer Organizations)
- Integrating real-time IoT sensors into Resource-Agent
- Expanding Knowledge Base with regional scheme variations
- Multi-language support (Hindi, Marathi, Kannada, etc.)

### Phase 3: Platform Maturity (2027)
- Integration with IndiaAI Compute Pillar
- Migration to Sovereign LLMs (BharatGen) for data privacy
- Opening APIs for private agritech companies
- Advanced analytics and impact measurement

### Phase 4: Nationwide Rollout (2028+)
- Integration with Digital ShramSetu
- Expansion to 1000+ villages
- Sovereign infrastructure deployment
- Ecosystem partnerships with government and NGOs
