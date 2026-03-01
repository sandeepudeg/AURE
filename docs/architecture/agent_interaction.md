# URE Agent Interaction Diagram

## 1. Agent Architecture Overview

```mermaid
graph TB
    subgraph "Agent Layer"
        SUP[Supervisor Agent<br/>Query Router]
        
        subgraph "Specialist Agents"
            AGR[Agri-Expert Agent<br/>Disease & Prices]
            POL[Policy-Navigator Agent<br/>PM-Kisan Schemes]
            RES[Resource-Optimizer Agent<br/>Irrigation & Weather]
        end
    end
    
    subgraph "AI Foundation"
        BEDROCK[Amazon Bedrock<br/>Nova Pro Model]
        KB[Knowledge Base<br/>RAG for Schemes]
    end
    
    subgraph "Tools & Services"
        T1[analyze_image<br/>Multimodal Vision]
        T2[search_plantvillage<br/>Disease Database]
        T3[get_treatment<br/>Knowledge Base]
        T4[get_mandi_prices<br/>MCP Tool]
        T5[get_nearby_mandis<br/>MCP Tool]
        T6[search_schemes<br/>Knowledge Base]
        T7[check_eligibility<br/>Logic + DynamoDB]
        T8[get_scheme_details<br/>Knowledge Base]
        T9[calculate_et<br/>Math Formula]
        T10[analyze_soil<br/>Sensor Data]
        T11[get_weather_forecast<br/>MCP Tool]
        T12[get_current_weather<br/>MCP Tool]
    end
    
    SUP --> AGR
    SUP --> POL
    SUP --> RES
    
    AGR --> BEDROCK
    POL --> BEDROCK
    RES --> BEDROCK
    
    AGR --> T1
    AGR --> T2
    AGR --> T3
    AGR --> T4
    AGR --> T5
    
    POL --> T6
    POL --> T7
    POL --> T8
    POL --> KB
    
    RES --> T9
    RES --> T10
    RES --> T11
    RES --> T12
    
    T1 --> BEDROCK
    T2 --> KB
    T3 --> KB
    T6 --> KB
    T8 --> KB
    
    style SUP fill:#FFD700
    style AGR fill:#87CEEB
    style POL fill:#87CEEB
    style RES fill:#87CEEB
    style BEDROCK fill:#FF6B6B
    style KB fill:#FFA500
    style T4 fill:#9370DB
    style T5 fill:#9370DB
    style T11 fill:#9370DB
    style T12 fill:#9370DB
```

## 2. Supervisor Agent Routing Logic

```mermaid
flowchart TD
    A[Query received] --> B[Supervisor Agent]
    B --> C{Analyze query}
    
    C --> D{Has image?}
    D -->|Yes| E[Route to Agri-Expert]
    D -->|No| F{Keywords?}
    
    F --> G{Disease/pest/crop?}
    G -->|Yes| E
    G -->|No| H{PM-Kisan/scheme/subsidy?}
    
    H -->|Yes| I[Route to Policy-Navigator]
    H -->|No| J{Irrigation/water/weather?}
    
    J -->|Yes| K[Route to Resource-Optimizer]
    J -->|No| L{Multiple domains?}
    
    L -->|Yes| M[Route to multiple agents]
    L -->|No| N[Default to Agri-Expert]
    
    E --> O[Execute Agri-Expert]
    I --> P[Execute Policy-Navigator]
    K --> Q[Execute Resource-Optimizer]
    M --> R[Execute multiple agents]
    N --> O
    
    O --> S[Return response]
    P --> S
    Q --> S
    R --> T[Synthesize responses]
    T --> S
    
    style A fill:#FFD700
    style B fill:#FFD700
    style E fill:#87CEEB
    style I fill:#87CEEB
    style K fill:#87CEEB
    style M fill:#87CEEB
    style S fill:#90EE90
```

## 3. Agri-Expert Agent Workflow

```mermaid
sequenceDiagram
    participant SUP as Supervisor
    participant AGR as Agri-Expert
    participant BR as Bedrock
    participant KB as Knowledge Base
    participant MCP as MCP Client
    participant EXT as Agmarknet API

    SUP->>AGR: Route query (image + text)
    
    AGR->>AGR: Check if image provided
    
    alt Image provided
        AGR->>BR: analyze_image(image_url)
        BR-->>AGR: Disease: Tomato Late Blight (confidence: 85%)
        
        AGR->>KB: search_plantvillage("Tomato Late Blight")
        KB-->>AGR: Similar images + metadata
        
        AGR->>KB: get_treatment("Tomato Late Blight")
        KB-->>AGR: Treatment steps + fungicides
    else No image
        AGR->>BR: Analyze text query
        BR-->>AGR: Extract disease name
        
        AGR->>KB: get_treatment(disease_name)
        KB-->>AGR: Treatment recommendations
    end
    
    AGR->>AGR: Extract crop name + location
    
    AGR->>MCP: get_mandi_prices(crop, district, state)
    MCP->>EXT: Request prices
    EXT-->>MCP: Return prices
    MCP-->>AGR: Prices data
    
    AGR->>MCP: get_nearby_mandis(district, radius_km)
    MCP->>EXT: Request mandis
    EXT-->>MCP: Return mandis
    MCP-->>AGR: Mandi locations
    
    AGR->>AGR: Synthesize response
    AGR-->>SUP: Return complete response
```

## 4. Policy-Navigator Agent Workflow

```mermaid
sequenceDiagram
    participant SUP as Supervisor
    participant POL as Policy-Navigator
    participant BR as Bedrock
    participant KB as Knowledge Base
    participant DDB as DynamoDB

    SUP->>POL: Route query (PM-Kisan eligibility)
    
    POL->>BR: Analyze query intent
    BR-->>POL: Intent: Check PM-Kisan eligibility
    
    POL->>KB: search_schemes("PM-Kisan")
    KB-->>POL: PM-Kisan scheme details
    
    POL->>DDB: Get user profile (land size, income, etc.)
    DDB-->>POL: User profile data
    
    POL->>POL: check_eligibility(profile, scheme_criteria)
    
    alt Eligible
        POL->>KB: get_scheme_details("PM-Kisan application")
        KB-->>POL: Application process + documents
        POL->>POL: Format response: Eligible + steps
    else Not eligible
        POL->>KB: get_scheme_details("PM-Kisan criteria")
        KB-->>POL: Eligibility criteria
        POL->>POL: Format response: Not eligible + reasons
    end
    
    POL-->>SUP: Return eligibility response
```

## 5. Resource-Optimizer Agent Workflow

```mermaid
sequenceDiagram
    participant SUP as Supervisor
    participant RES as Resource-Optimizer
    participant BR as Bedrock
    participant MCP as MCP Client
    participant EXT as Weather API
    participant DDB as DynamoDB

    SUP->>RES: Route query (irrigation advice)
    
    RES->>BR: Analyze query intent
    BR-->>RES: Intent: Irrigation recommendation
    
    RES->>RES: Extract location + crop type
    
    RES->>MCP: get_current_weather(location)
    MCP->>EXT: Request current weather
    EXT-->>MCP: Temp, humidity, wind
    MCP-->>RES: Weather data
    
    RES->>MCP: get_weather_forecast(location, days=3)
    MCP->>EXT: Request forecast
    EXT-->>MCP: 3-day forecast
    MCP-->>RES: Forecast data
    
    RES->>DDB: Get soil moisture data (if available)
    DDB-->>RES: Soil moisture readings
    
    RES->>RES: calculate_evapotranspiration(temp, humidity, wind)
    RES->>RES: analyze_soil_moisture(moisture_data)
    RES->>RES: optimize_pump_schedule(et, moisture, forecast)
    
    RES->>RES: Generate recommendation
    RES-->>SUP: Return irrigation advice
```

## 6. Multi-Agent Coordination

```mermaid
sequenceDiagram
    participant U as User
    participant SUP as Supervisor
    participant AGR as Agri-Expert
    participant RES as Resource-Optimizer
    participant BR as Bedrock

    U->>SUP: "My tomato crop has disease. Should I water it today?"
    
    SUP->>BR: Analyze query complexity
    BR-->>SUP: Multiple domains: Disease + Irrigation
    
    par Parallel execution
        SUP->>AGR: Get disease information
        AGR->>BR: Identify disease
        BR-->>AGR: Tomato Late Blight
        AGR-->>SUP: Disease + treatment
    and
        SUP->>RES: Get irrigation advice
        RES->>BR: Calculate irrigation need
        BR-->>RES: Recommendation
        RES-->>SUP: Irrigation advice
    end
    
    SUP->>SUP: Synthesize responses
    SUP->>BR: Combine disease + irrigation advice
    BR-->>SUP: Unified response
    
    SUP-->>U: "Your crop has Late Blight. Treat with fungicide. Wait 2 days before watering."
```

## 7. Agent Tool Usage Matrix

| Agent | Tool | Type | Purpose |
|-------|------|------|---------|
| **Agri-Expert** | analyze_image | Bedrock | Identify crop disease from image |
| | search_plantvillage | Knowledge Base | Find similar disease images |
| | get_treatment | Knowledge Base | Retrieve treatment recommendations |
| | get_mandi_prices | MCP Tool | Fetch current market prices |
| | get_nearby_mandis | MCP Tool | Find nearby market locations |
| **Policy-Navigator** | search_schemes | Knowledge Base | Search government schemes |
| | check_eligibility | Logic + DynamoDB | Verify farmer eligibility |
| | get_scheme_details | Knowledge Base | Get scheme application details |
| **Resource-Optimizer** | calculate_et | Math Formula | Calculate evapotranspiration |
| | analyze_soil | Sensor Data | Interpret soil moisture levels |
| | get_weather_forecast | MCP Tool | Fetch weather forecast |
| | get_current_weather | MCP Tool | Get current weather conditions |

## 8. Agent Decision Tree

```mermaid
flowchart TD
    A[Query Analysis] --> B{Query Type}
    
    B -->|Image-based| C[Agri-Expert]
    B -->|Text-based| D{Domain}
    
    D -->|Disease/Pest| C
    D -->|Market Prices| C
    D -->|Government Schemes| E[Policy-Navigator]
    D -->|Irrigation/Weather| F[Resource-Optimizer]
    D -->|Multiple| G[Multi-Agent]
    
    C --> C1{Has image?}
    C1 -->|Yes| C2[Vision analysis]
    C1 -->|No| C3[Text analysis]
    C2 --> C4[Disease identification]
    C3 --> C4
    C4 --> C5[Treatment lookup]
    C5 --> C6[Price lookup via MCP]
    C6 --> H[Response]
    
    E --> E1[Scheme search]
    E1 --> E2[Eligibility check]
    E2 --> E3{Eligible?}
    E3 -->|Yes| E4[Application steps]
    E3 -->|No| E5[Criteria explanation]
    E4 --> H
    E5 --> H
    
    F --> F1[Weather lookup via MCP]
    F1 --> F2[ET calculation]
    F2 --> F3[Soil analysis]
    F3 --> F4[Irrigation recommendation]
    F4 --> H
    
    G --> G1[Parallel agent execution]
    G1 --> G2[Response synthesis]
    G2 --> H
    
    style A fill:#FFD700
    style C fill:#87CEEB
    style E fill:#87CEEB
    style F fill:#87CEEB
    style G fill:#87CEEB
    style H fill:#90EE90
```

## 9. Agent Communication Protocol

```mermaid
sequenceDiagram
    participant L as Lambda Handler
    participant SUP as Supervisor
    participant AGT as Specialist Agent
    participant BR as Bedrock
    participant TOOL as Tool/Service

    L->>SUP: invoke(query, context)
    SUP->>BR: classify_query(query)
    BR-->>SUP: query_type + confidence
    
    SUP->>SUP: select_agent(query_type)
    SUP->>AGT: invoke(query, context, tools)
    
    loop Tool execution
        AGT->>BR: analyze_and_plan()
        BR-->>AGT: next_action
        AGT->>TOOL: execute_tool(params)
        TOOL-->>AGT: result
        AGT->>BR: process_result(result)
    end
    
    BR-->>AGT: final_response
    AGT-->>SUP: response + metadata
    SUP->>SUP: validate_response()
    SUP-->>L: final_response
```

## 10. Agent Performance Metrics

```mermaid
graph LR
    subgraph "Supervisor Metrics"
        S1[Routing Accuracy: 90%+]
        S2[Response Time: < 1s]
        S3[Multi-agent Coordination: 95%+]
    end
    
    subgraph "Agri-Expert Metrics"
        A1[Disease ID Accuracy: 80%+]
        A2[Response Time: < 5s]
        A3[MCP Tool Success: 95%+]
    end
    
    subgraph "Policy-Navigator Metrics"
        P1[Eligibility Accuracy: 95%+]
        P2[Response Time: < 3s]
        P3[KB Retrieval Success: 98%+]
    end
    
    subgraph "Resource-Optimizer Metrics"
        R1[Recommendation Validity: 90%+]
        R2[Response Time: < 4s]
        R3[Weather Data Accuracy: 95%+]
    end
    
    style S1 fill:#90EE90
    style S2 fill:#90EE90
    style S3 fill:#90EE90
    style A1 fill:#87CEEB
    style A2 fill:#87CEEB
    style A3 fill:#87CEEB
    style P1 fill:#FFD700
    style P2 fill:#FFD700
    style P3 fill:#FFD700
    style R1 fill:#FFA500
    style R2 fill:#FFA500
    style R3 fill:#FFA500
```

---

**Version**: 1.0.0  
**Last Updated**: February 28, 2026
