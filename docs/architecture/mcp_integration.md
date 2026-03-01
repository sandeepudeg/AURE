# URE MCP Integration Architecture

## 1. MCP Integration Overview

```mermaid
graph TB
    subgraph "Lambda Function"
        HANDLER[Lambda Handler]
        MCP[MCP Client]
        CACHE[TTL Cache<br/>5 min, 100 items]
        REG[Tool Registry<br/>JSON Config]
    end
    
    subgraph "MCP Servers"
        AGM[Agmarknet MCP Server<br/>Port 8001]
        WTH[Weather MCP Server<br/>Port 8002]
    end
    
    subgraph "External APIs"
        AGAPI[Agmarknet API<br/>data.gov.in]
        WAPI[OpenWeather API<br/>openweathermap.org]
    end
    
    subgraph "AWS Services"
        S3[S3 Bucket<br/>Tool Registry Storage]
        CW[CloudWatch<br/>Logs & Metrics]
    end
    
    HANDLER --> MCP
    MCP --> REG
    MCP --> CACHE
    MCP --> AGM
    MCP --> WTH
    MCP --> CW
    
    REG --> S3
    
    AGM --> AGAPI
    WTH --> WAPI
    
    style MCP fill:#FFD700
    style AGM fill:#9370DB
    style WTH fill:#9370DB
    style CACHE fill:#87CEEB
    style REG fill:#FFA500
```

## 2. MCP Client Architecture

```mermaid
classDiagram
    class MCPClient {
        -tool_registry: dict
        -servers: dict
        -cache: TTLCache
        -logger: Logger
        +__init__(registry_path, servers)
        +call_tool(tool_id, agent_role, params)
        -_load_registry()
        -_check_permission(tool_id, agent_role)
        -_call_with_retry(url, payload, retries)
        -_cache_result(tool_id, params, result)
        -_get_cached_result(tool_id, params)
        -_log_tool_call(tool_id, status, duration)
    }
    
    class ToolRegistry {
        +tool_id: str
        +server_name: str
        +permissions: list
        +timeout_ms: int
        +retry_count: int
    }
    
    class MCPServer {
        +name: str
        +url: str
        +tools: list
        +health_check()
    }
    
    class TTLCache {
        +maxsize: int
        +ttl: int
        +get(key)
        +set(key, value)
    }
    
    MCPClient --> ToolRegistry
    MCPClient --> MCPServer
    MCPClient --> TTLCache
```

## 3. Tool Registry Structure

```json
{
  "get_mandi_prices": {
    "tool_id": "get_mandi_prices",
    "server_name": "agmarknet",
    "description": "Get current market prices for crops",
    "permissions": ["Agri-Expert", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3,
    "parameters": {
      "crop": "string (required)",
      "district": "string (required)",
      "state": "string (required)"
    }
  },
  "get_nearby_mandis": {
    "tool_id": "get_nearby_mandis",
    "server_name": "agmarknet",
    "description": "Find nearby market locations",
    "permissions": ["Agri-Expert", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3,
    "parameters": {
      "district": "string (required)",
      "radius_km": "number (optional, default: 50)"
    }
  },
  "get_current_weather": {
    "tool_id": "get_current_weather",
    "server_name": "weather",
    "description": "Get current weather conditions",
    "permissions": ["Resource-Optimizer", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3,
    "parameters": {
      "location": "string (required)",
      "units": "string (optional, default: metric)"
    }
  },
  "get_weather_forecast": {
    "tool_id": "get_weather_forecast",
    "server_name": "weather",
    "description": "Get weather forecast for next N days",
    "permissions": ["Resource-Optimizer", "Supervisor"],
    "timeout_ms": 5000,
    "retry_count": 3,
    "parameters": {
      "location": "string (required)",
      "days": "number (optional, default: 3)"
    }
  }
}
```

## 4. MCP Tool Call Flow

```mermaid
sequenceDiagram
    participant A as Agent
    participant MCP as MCP Client
    participant REG as Tool Registry
    participant CACHE as TTL Cache
    participant SRV as MCP Server
    participant API as External API
    participant LOG as CloudWatch

    A->>MCP: call_tool("get_mandi_prices", "Agri-Expert", {crop, district, state})
    
    MCP->>REG: Lookup tool metadata
    REG-->>MCP: Tool config (server, permissions, timeout)
    
    MCP->>MCP: Check permission
    alt Permission denied
        MCP->>LOG: Log permission denied
        MCP-->>A: Error: Permission denied
    else Permission granted
        MCP->>CACHE: Check cache
        alt Cache hit
            CACHE-->>MCP: Cached result
            MCP->>LOG: Log cache hit
            MCP-->>A: Return cached result
        else Cache miss
            MCP->>SRV: POST /tools/get_mandi_prices
            SRV->>API: Request data
            
            alt API success
                API-->>SRV: Return data
                SRV-->>MCP: Return result
                MCP->>CACHE: Cache result (TTL: 5 min)
                MCP->>LOG: Log success
                MCP-->>A: Return result
            else API failure
                API-->>SRV: Error
                SRV-->>MCP: Error
                MCP->>MCP: Retry (attempt 2)
                
                alt Retry success
                    SRV-->>MCP: Return result
                    MCP->>CACHE: Cache result
                    MCP->>LOG: Log success (retry)
                    MCP-->>A: Return result
                else Retry failed
                    MCP->>CACHE: Check cache for stale data
                    alt Stale cache available
                        CACHE-->>MCP: Stale result
                        MCP->>LOG: Log fallback to stale cache
                        MCP-->>A: Return stale result + warning
                    else No cache
                        MCP->>LOG: Log failure
                        MCP-->>A: Error: Service unavailable
                    end
                end
            end
        end
    end
```

## 5. Permission System

```mermaid
flowchart TD
    A[Tool call request] --> B{Check tool exists?}
    B -->|No| C[Error: Tool not found]
    B -->|Yes| D{Check agent role?}
    
    D --> E{Role in permissions list?}
    E -->|No| F[Error: Permission denied]
    E -->|Yes| G[Allow tool call]
    
    G --> H{Execute tool}
    H --> I[Return result]
    
    C --> J[Log error]
    F --> J
    I --> K[Log success]
    
    style C fill:#FF6B6B
    style F fill:#FF6B6B
    style I fill:#90EE90
```

### Permission Matrix

| Tool | Agri-Expert | Policy-Navigator | Resource-Optimizer | Supervisor |
|------|-------------|------------------|-------------------|------------|
| get_mandi_prices | ✅ | ❌ | ❌ | ✅ |
| get_nearby_mandis | ✅ | ❌ | ❌ | ✅ |
| get_current_weather | ❌ | ❌ | ✅ | ✅ |
| get_weather_forecast | ❌ | ❌ | ✅ | ✅ |

## 6. Retry Logic with Exponential Backoff

```mermaid
flowchart TD
    A[Tool call] --> B[Attempt 1]
    B --> C{Success?}
    C -->|Yes| D[Return result]
    C -->|No| E[Wait 1 second]
    
    E --> F[Attempt 2]
    F --> G{Success?}
    G -->|Yes| D
    G -->|No| H[Wait 2 seconds]
    
    H --> I[Attempt 3]
    I --> J{Success?}
    J -->|Yes| D
    J -->|No| K{Cache available?}
    
    K -->|Yes| L[Return cached data]
    K -->|No| M[Return error]
    
    style D fill:#90EE90
    style L fill:#FFA500
    style M fill:#FF6B6B
```

### Retry Configuration

```python
# Retry settings
MAX_RETRIES = 3
BACKOFF_FACTOR = 1  # seconds
TIMEOUT = 5  # seconds per request

# Retry delays
# Attempt 1: 0 seconds (immediate)
# Attempt 2: 1 second wait
# Attempt 3: 2 seconds wait
# Total max time: 5s + 1s + 5s + 2s + 5s = 18 seconds
```

## 7. Caching Strategy

```mermaid
flowchart TD
    A[Tool call] --> B{Check cache}
    B -->|Hit| C{Cache fresh?}
    C -->|Yes, < 5 min| D[Return cached data]
    C -->|No, > 5 min| E[Evict from cache]
    
    B -->|Miss| F[Call MCP server]
    E --> F
    
    F --> G{Success?}
    G -->|Yes| H[Cache result]
    G -->|No| I{Stale cache exists?}
    
    H --> J[Return result]
    I -->|Yes| K[Return stale data + warning]
    I -->|No| L[Return error]
    
    style D fill:#90EE90
    style J fill:#90EE90
    style K fill:#FFA500
    style L fill:#FF6B6B
```

### Cache Configuration

```python
# Cache settings
CACHE_TTL = 300  # 5 minutes
CACHE_MAXSIZE = 100  # Max 100 items
CACHE_KEY_FORMAT = "{tool_id}:{params_hash}"

# Cache eviction policy: LRU (Least Recently Used)
# Stale data retention: 30 minutes (for fallback)
```

## 8. MCP Server Implementation

### Agmarknet MCP Server

```mermaid
graph LR
    A[MCP Server] --> B[FastAPI App]
    B --> C[/tools/get_mandi_prices]
    B --> D[/tools/get_nearby_mandis]
    B --> E[/health]
    
    C --> F[Agmarknet API]
    D --> F
    
    F --> G[data.gov.in]
    
    style A fill:#9370DB
    style B fill:#87CEEB
    style F fill:#FFA500
```

### Weather MCP Server

```mermaid
graph LR
    A[MCP Server] --> B[FastAPI App]
    B --> C[/tools/get_current_weather]
    B --> D[/tools/get_weather_forecast]
    B --> E[/health]
    
    C --> F[OpenWeather API]
    D --> F
    
    F --> G[openweathermap.org]
    
    style A fill:#9370DB
    style B fill:#87CEEB
    style F fill:#FFA500
```

## 9. Error Handling

```mermaid
flowchart TD
    A[MCP Tool Call] --> B{Validate input}
    B -->|Invalid| C[Error: Invalid parameters]
    B -->|Valid| D{Check permissions}
    
    D -->|Denied| E[Error: Permission denied]
    D -->|Allowed| F{Call MCP server}
    
    F --> G{Server response}
    G -->|Timeout| H[Retry with backoff]
    G -->|Connection error| H
    G -->|HTTP 5xx| H
    G -->|HTTP 4xx| I[Error: Client error]
    G -->|HTTP 200| J[Success]
    
    H --> K{Retries exhausted?}
    K -->|No| F
    K -->|Yes| L{Cache available?}
    
    L -->|Yes| M[Return cached data]
    L -->|No| N[Error: Service unavailable]
    
    J --> O[Cache result]
    O --> P[Return result]
    
    style C fill:#FF6B6B
    style E fill:#FF6B6B
    style I fill:#FF6B6B
    style N fill:#FF6B6B
    style M fill:#FFA500
    style P fill:#90EE90
```

## 10. Monitoring & Logging

```mermaid
flowchart TD
    A[MCP Tool Call] --> B[Log: Tool invocation]
    B --> C[Execute tool]
    C --> D{Result}
    
    D -->|Success| E[Log: Success]
    D -->|Cache hit| F[Log: Cache hit]
    D -->|Retry| G[Log: Retry attempt]
    D -->|Fallback| H[Log: Fallback to cache]
    D -->|Error| I[Log: Error]
    
    E --> J[CloudWatch Metrics]
    F --> J
    G --> J
    H --> J
    I --> J
    
    J --> K[Dashboard Widget]
    J --> L[Alarm Threshold]
    
    L --> M{Threshold exceeded?}
    M -->|Yes| N[Trigger alarm]
    M -->|No| O[Continue monitoring]
    
    style E fill:#90EE90
    style F fill:#87CEEB
    style G fill:#FFA500
    style H fill:#FFA500
    style I fill:#FF6B6B
```

### Logged Metrics

```python
# CloudWatch metrics
metrics = {
    "mcp_tool_calls_total": "Counter",
    "mcp_tool_calls_success": "Counter",
    "mcp_tool_calls_failure": "Counter",
    "mcp_tool_calls_cache_hit": "Counter",
    "mcp_tool_calls_retry": "Counter",
    "mcp_tool_calls_fallback": "Counter",
    "mcp_tool_call_duration_ms": "Histogram",
    "mcp_cache_size": "Gauge",
    "mcp_permission_denied": "Counter"
}
```

## 11. MCP Integration Benefits

```mermaid
mindmap
  root((MCP Integration))
    Standardization
      Unified tool interface
      Consistent error handling
      Common logging format
    Security
      Permission-based access
      Role-based authorization
      Audit trail
    Reliability
      Retry with backoff
      Fallback to cache
      Graceful degradation
    Performance
      TTL caching
      Reduced API calls
      Lower latency
    Observability
      Comprehensive logging
      Metrics tracking
      Error monitoring
    Maintainability
      Centralized config
      Easy tool addition
      Version management
```

## 12. Future Enhancements

```mermaid
flowchart LR
    A[Current MCP] --> B[Phase 2]
    B --> C[More MCP Servers]
    B --> D[Advanced Caching]
    B --> E[Circuit Breaker]
    B --> F[Rate Limiting]
    
    C --> G[Soil Testing API]
    C --> H[Satellite Imagery API]
    C --> I[Pest Alert API]
    
    D --> J[Redis Cache]
    D --> K[Multi-level Cache]
    
    E --> L[Prevent cascade failures]
    F --> M[Protect external APIs]
    
    style A fill:#FFD700
    style B fill:#87CEEB
    style C fill:#9370DB
    style D fill:#FFA500
    style E fill:#FF6B6B
    style F fill:#FF6B6B
```

---

**Version**: 1.0.0  
**Last Updated**: February 28, 2026
