# URE Data Flow Diagram

## 1. Complete Request-Response Flow

```mermaid
sequenceDiagram
    participant F as Farmer
    participant UI as Streamlit UI
    participant API as API Gateway
    participant L as Lambda Handler
    participant MCP as MCP Client
    participant SUP as Supervisor Agent
    participant AGR as Agri-Expert Agent
    participant POL as Policy-Navigator Agent
    participant RES as Resource-Optimizer Agent
    participant BR as Bedrock (Nova Pro)
    participant KB as Knowledge Base
    participant GR as Guardrails
    participant TR as Translate
    participant S3 as S3 Bucket
    participant DDB as DynamoDB
    participant EXT as External MCP Servers
    participant CW as CloudWatch

    F->>UI: 1. Submit query + image
    UI->>S3: 2. Upload image
    S3-->>UI: 3. Return image URL
    UI->>API: 4. POST /query (user_id, query, image_url, language)
    
    API->>L: 5. Invoke Lambda
    L->>CW: 6. Log request
    L->>GR: 7. Check input guardrails
    GR-->>L: 8. Input approved
    
    L->>DDB: 9. Get user profile
    DDB-->>L: 10. Return profile
    
    L->>MCP: 11. Initialize MCP Client
    MCP->>S3: 12. Load tool registry
    S3-->>MCP: 13. Return registry
    
    L->>SUP: 14. Invoke Supervisor Agent
    SUP->>BR: 15. Classify query type
    BR-->>SUP: 16. Route to Agri-Expert
    
    SUP->>AGR: 17. Invoke Agri-Expert
    AGR->>BR: 18. Analyze image (multimodal)
    BR-->>AGR: 19. Disease identified: Tomato Late Blight
    
    AGR->>KB: 20. Get treatment recommendations
    KB-->>AGR: 21. Return treatment steps
    
    AGR->>MCP: 22. Call get_mandi_prices tool
    MCP->>EXT: 23. Request mandi prices (Agmarknet)
    EXT-->>MCP: 24. Return prices
    MCP->>CW: 25. Log tool call
    MCP-->>AGR: 26. Return prices
    
    AGR-->>SUP: 27. Return response
    SUP-->>L: 28. Return final response
    
    L->>GR: 29. Check output guardrails
    GR-->>L: 30. Output approved
    
    L->>TR: 31. Translate to Hindi/Marathi
    TR-->>L: 32. Return translated response
    
    L->>DDB: 33. Save conversation
    DDB-->>L: 34. Confirm saved
    
    L->>CW: 35. Log response metrics
    L-->>API: 36. Return response (200 OK)
    API-->>UI: 37. Return response
    UI-->>F: 38. Display response
```

## 2. Image Upload Flow

```mermaid
flowchart TD
    A[Farmer selects image] --> B{Validate image}
    B -->|Invalid format| C[Show error: Use JPG/PNG]
    B -->|Too large > 5MB| D[Show error: Compress image]
    B -->|Valid| E[Upload to S3]
    E --> F{Upload successful?}
    F -->|No| G[Show error: Upload failed]
    F -->|Yes| H[Generate S3 URL]
    H --> I[Include URL in API request]
    I --> J[Lambda processes image]
    J --> K[Bedrock analyzes image]
    K --> L[Return disease identification]
    L --> M[Display result to farmer]
    
    style A fill:#90EE90
    style C fill:#FF6B6B
    style D fill:#FF6B6B
    style G fill:#FF6B6B
    style M fill:#87CEEB
```

## 3. Agent Routing Flow

```mermaid
flowchart TD
    A[Query received] --> B[Supervisor Agent]
    B --> C{Query type?}
    
    C -->|Image OR disease/pest| D[Agri-Expert Agent]
    C -->|PM-Kisan/scheme| E[Policy-Navigator Agent]
    C -->|Irrigation/weather| F[Resource-Optimizer Agent]
    C -->|Complex/multiple| G[Multiple Agents]
    
    D --> D1[Analyze image]
    D1 --> D2[Identify disease]
    D2 --> D3[Get treatment from KB]
    D3 --> D4[Get mandi prices via MCP]
    D4 --> H[Synthesize response]
    
    E --> E1[Search Knowledge Base]
    E1 --> E2[Check eligibility]
    E2 --> E3[Get scheme details]
    E3 --> H
    
    F --> F1[Get weather via MCP]
    F1 --> F2[Calculate ET]
    F2 --> F3[Analyze soil moisture]
    F3 --> F4[Generate recommendation]
    F4 --> H
    
    G --> G1[Invoke multiple agents]
    G1 --> G2[Combine responses]
    G2 --> H
    
    H --> I[Apply guardrails]
    I --> J{Content safe?}
    J -->|No| K[Block response]
    J -->|Yes| L[Translate response]
    L --> M[Return to user]
    
    style A fill:#FFD700
    style D fill:#87CEEB
    style E fill:#87CEEB
    style F fill:#87CEEB
    style K fill:#FF6B6B
    style M fill:#90EE90
```

## 4. MCP Tool Call Flow

```mermaid
sequenceDiagram
    participant A as Agent
    participant MCP as MCP Client
    participant REG as Tool Registry
    participant SRV as MCP Server
    participant CACHE as Cache
    participant LOG as CloudWatch

    A->>MCP: 1. Call tool (tool_id, agent_role, params)
    MCP->>REG: 2. Lookup tool metadata
    REG-->>MCP: 3. Return tool config
    
    MCP->>MCP: 4. Check permissions
    alt Permission denied
        MCP-->>A: 5a. Return error: Permission denied
    else Permission granted
        MCP->>SRV: 5b. HTTP POST to MCP server
        
        alt Server responds
            SRV-->>MCP: 6a. Return result
            MCP->>CACHE: 7a. Cache result (TTL: 5 min)
            MCP->>LOG: 8a. Log success
            MCP-->>A: 9a. Return result
        else Server timeout/error
            MCP->>MCP: 6b. Retry (attempt 2)
            SRV-->>MCP: 7b. Still failing
            MCP->>MCP: 8b. Retry (attempt 3)
            SRV-->>MCP: 9b. Still failing
            MCP->>CACHE: 10b. Check cache
            alt Cache hit
                CACHE-->>MCP: 11b. Return cached data
                MCP->>LOG: 12b. Log fallback to cache
                MCP-->>A: 13b. Return cached result
            else Cache miss
                MCP->>LOG: 11c. Log failure
                MCP-->>A: 12c. Return error
            end
        end
    end
```

## 5. Guardrails Flow

```mermaid
flowchart TD
    A[Input/Output text] --> B[Bedrock Guardrails]
    B --> C{Check harmful content}
    C -->|Banned pesticides| D[Block: DDT, Endosulfan]
    C -->|Violence/hate| E[Block: Harmful advice]
    C -->|Off-topic| F[Block: Politics, religion]
    C -->|Safe| G{Check PII}
    
    D --> H[Return BLOCKED status]
    E --> H
    F --> H
    
    G -->|Email found| I[Anonymize: ***@***.com]
    G -->|Phone found| J[Anonymize: +91-XXXX-XXXX]
    G -->|Address found| K[Anonymize: [ADDRESS]]
    G -->|No PII| L[Return ALLOWED status]
    
    I --> L
    J --> L
    K --> L
    
    H --> M[Show error to user]
    L --> N[Continue processing]
    
    style D fill:#FF6B6B
    style E fill:#FF6B6B
    style F fill:#FF6B6B
    style H fill:#FF6B6B
    style M fill:#FF6B6B
    style N fill:#90EE90
```

## 6. Translation Flow

```mermaid
flowchart LR
    A[English response] --> B{User language?}
    B -->|English| C[No translation needed]
    B -->|Hindi| D[Amazon Translate]
    B -->|Marathi| E[Amazon Translate]
    
    D --> F[Hindi response]
    E --> G[Marathi response]
    C --> H[Return to user]
    F --> H
    G --> H
    
    style A fill:#FFD700
    style D fill:#87CEEB
    style E fill:#87CEEB
    style H fill:#90EE90
```

## 7. Error Handling Flow

```mermaid
flowchart TD
    A[Request received] --> B{Validate input}
    B -->|Invalid JSON| C[Return 400: Bad Request]
    B -->|Valid| D[Process request]
    
    D --> E{Lambda timeout?}
    E -->|Yes > 30s| F[Return 504: Gateway Timeout]
    E -->|No| G{Bedrock error?}
    
    G -->|Yes| H[Return 500: Internal Server Error]
    G -->|No| I{Guardrails block?}
    
    I -->|Yes| J[Return 403: Content Blocked]
    I -->|No| K{MCP server error?}
    
    K -->|Yes| L{Cache available?}
    L -->|Yes| M[Use cached data]
    L -->|No| N[Return partial response]
    
    K -->|No| O[Return 200: Success]
    
    M --> O
    N --> O
    
    C --> P[Log error to CloudWatch]
    F --> P
    H --> P
    J --> P
    O --> Q[Return response to user]
    
    style C fill:#FF6B6B
    style F fill:#FF6B6B
    style H fill:#FF6B6B
    style J fill:#FFA500
    style O fill:#90EE90
```

## 8. Monitoring Flow

```mermaid
flowchart TD
    A[Lambda execution] --> B[CloudWatch Logs]
    B --> C[CloudWatch Metrics]
    
    C --> D{Check thresholds}
    D -->|Lambda errors > 5| E[Trigger alarm]
    D -->|Lambda duration > 30s| F[Trigger alarm]
    D -->|API 5xx > 10| G[Trigger alarm]
    D -->|API latency > 5s| H[Trigger alarm]
    D -->|Normal| I[Update dashboard]
    
    E --> J[SNS notification]
    F --> J
    G --> J
    H --> J
    
    J --> K[Email to admin]
    I --> L[Dashboard widgets]
    
    L --> M[Lambda invocations chart]
    L --> N[Lambda errors chart]
    L --> O[API Gateway requests chart]
    L --> P[DynamoDB capacity chart]
    
    style E fill:#FF6B6B
    style F fill:#FF6B6B
    style G fill:#FF6B6B
    style H fill:#FF6B6B
    style K fill:#FFA500
    style I fill:#90EE90
```

## 9. Data Persistence Flow

```mermaid
flowchart TD
    A[Conversation data] --> B{Encrypt with KMS}
    B --> C[Store in DynamoDB]
    C --> D[Set TTL: 30 days]
    
    E[Image data] --> F{Encrypt with KMS}
    F --> G[Store in S3]
    G --> H[Set lifecycle: Delete after 30 days]
    
    I[User profile] --> J{Encrypt with KMS}
    J --> K[Store in DynamoDB]
    K --> L[No TTL - persistent]
    
    D --> M[Auto-delete after 30 days]
    H --> N[Auto-delete after 30 days]
    L --> O[Retained indefinitely]
    
    style B fill:#DC143C
    style F fill:#DC143C
    style J fill:#DC143C
    style M fill:#FFA500
    style N fill:#FFA500
    style O fill:#90EE90
```

---

**Version**: 1.0.0  
**Last Updated**: February 28, 2026
