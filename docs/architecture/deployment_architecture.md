# URE Deployment Architecture

## 1. AWS Deployment Architecture

```mermaid
graph TB
    subgraph "Internet"
        USER[Farmers<br/>Web/Mobile Browsers]
    end
    
    subgraph "AWS Cloud - us-east-1"
        subgraph "Edge Layer"
            CF[CloudFront CDN<br/>(Future)]
            R53[Route 53<br/>DNS (Future)]
        end
        
        subgraph "Application Layer"
            APIGW[API Gateway<br/>REST API<br/>Throttling: 1000/s]
            
            subgraph "Compute"
                LAMBDA[Lambda Function<br/>ure-mvp-handler<br/>Memory: 512MB<br/>Timeout: 30s<br/>Concurrency: 100]
            end
        end
        
        subgraph "AI/ML Services"
            BEDROCK[Amazon Bedrock<br/>Nova Pro Model<br/>Inference Profile]
            KB[Bedrock Knowledge Base<br/>OpenSearch Serverless]
            GUARD[Bedrock Guardrails<br/>Content Filtering]
            TRANS[Amazon Translate<br/>Hindi/Marathi]
        end
        
        subgraph "Storage Services"
            S3[S3 Bucket<br/>ure-mvp-data<br/>Versioning: Enabled<br/>Encryption: KMS]
            
            DDB1[DynamoDB<br/>ure-conversations<br/>On-Demand<br/>TTL: 30 days]
            
            DDB2[DynamoDB<br/>ure-user-profiles<br/>On-Demand<br/>No TTL]
            
            DDB3[DynamoDB<br/>ure-village-amenities<br/>On-Demand<br/>No TTL]
        end
        
        subgraph "Security Services"
            KMS[KMS Key<br/>Encryption<br/>Auto-rotation]
            IAM[IAM Role<br/>ure-lambda-role<br/>Least Privilege]
            SECRETS[Secrets Manager<br/>API Keys (Future)]
        end
        
        subgraph "Monitoring Services"
            CW[CloudWatch<br/>Logs & Metrics]
            DASH[CloudWatch Dashboard<br/>ure-mvp-dashboard]
            ALARM[CloudWatch Alarms<br/>7 Alarms]
            SNS[SNS Topic<br/>ure-mvp-alarms]
        end
        
        subgraph "External Services"
            MCP1[MCP Server<br/>Agmarknet<br/>Port 8001]
            MCP2[MCP Server<br/>Weather<br/>Port 8002]
        end
    end
    
    subgraph "External APIs"
        AGAPI[Agmarknet API<br/>data.gov.in]
        WAPI[OpenWeather API<br/>openweathermap.org]
    end
    
    USER --> APIGW
    APIGW --> LAMBDA
    
    LAMBDA --> BEDROCK
    LAMBDA --> KB
    LAMBDA --> GUARD
    LAMBDA --> TRANS
    LAMBDA --> S3
    LAMBDA --> DDB1
    LAMBDA --> DDB2
    LAMBDA --> DDB3
    LAMBDA --> MCP1
    LAMBDA --> MCP2
    
    MCP1 --> AGAPI
    MCP2 --> WAPI
    
    KMS -.encrypts.-> S3
    KMS -.encrypts.-> DDB1
    KMS -.encrypts.-> DDB2
    KMS -.encrypts.-> DDB3
    KMS -.encrypts.-> CW
    
    IAM -.authorizes.-> LAMBDA
    
    LAMBDA --> CW
    CW --> DASH
    CW --> ALARM
    ALARM --> SNS
    
    style USER fill:#90EE90
    style APIGW fill:#87CEEB
    style LAMBDA fill:#FFD700
    style BEDROCK fill:#FF6B6B
    style S3 fill:#FFA500
    style DDB1 fill:#FFA500
    style KMS fill:#DC143C
    style CW fill:#20B2AA
```

## 2. CloudFormation Stack Resources

```mermaid
graph TB
    subgraph "CloudFormation Stack: ure-mvp-stack"
        subgraph "Security Resources"
            KMS[KMS Key<br/>URE-KMS-Key]
            IAM[IAM Role<br/>ure-mvp-lambda-role]
        end
        
        subgraph "Storage Resources"
            S3[S3 Bucket<br/>ure-mvp-data-{region}-{account}]
            DDB1[DynamoDB Table<br/>ure-conversations]
            DDB2[DynamoDB Table<br/>ure-user-profiles]
            DDB3[DynamoDB Table<br/>ure-village-amenities]
        end
        
        subgraph "Compute Resources"
            LAMBDA[Lambda Function<br/>ure-mvp-handler]
            APIGW[API Gateway<br/>ure-mvp-api]
            STAGE[API Stage<br/>dev/staging/prod]
        end
        
        subgraph "Monitoring Resources"
            LOG[Log Group<br/>/aws/lambda/ure-mvp-handler]
            DASH[Dashboard<br/>ure-mvp-dashboard]
            
            subgraph "Alarms"
                A1[Lambda Error Alarm]
                A2[Lambda Duration Alarm]
                A3[Lambda Throttle Alarm]
                A4[API 5xx Alarm]
                A5[API 4xx Alarm]
                A6[API Latency Alarm]
                A7[DynamoDB Throttle Alarm]
            end
            
            SNS[SNS Topic<br/>ure-mvp-alarms]
        end
    end
    
    KMS --> S3
    KMS --> DDB1
    KMS --> DDB2
    KMS --> DDB3
    KMS --> LOG
    
    IAM --> LAMBDA
    
    LAMBDA --> APIGW
    APIGW --> STAGE
    
    LAMBDA --> LOG
    LOG --> DASH
    
    A1 --> SNS
    A2 --> SNS
    A3 --> SNS
    A4 --> SNS
    A5 --> SNS
    A6 --> SNS
    A7 --> SNS
    
    style KMS fill:#DC143C
    style IAM fill:#DC143C
    style LAMBDA fill:#FFD700
    style S3 fill:#FFA500
    style DDB1 fill:#FFA500
    style DASH fill:#20B2AA
    style SNS fill:#20B2AA
```

## 3. Deployment Pipeline

```mermaid
flowchart LR
    A[Local Development] --> B[Git Push]
    B --> C[CloudFormation Deploy]
    C --> D[Create/Update Stack]
    
    D --> E[Deploy Infrastructure]
    E --> F[KMS Key]
    E --> G[IAM Role]
    E --> H[S3 Bucket]
    E --> I[DynamoDB Tables]
    E --> J[Lambda Function]
    E --> K[API Gateway]
    E --> L[CloudWatch Resources]
    
    F --> M[Stack Complete]
    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N[Deploy Lambda Code]
    N --> O[Package Dependencies]
    O --> P[Upload to Lambda]
    P --> Q[Update Function Code]
    
    Q --> R[Deploy MCP Servers]
    R --> S[Start Agmarknet Server]
    R --> T[Start Weather Server]
    
    S --> U[Deployment Complete]
    T --> U
    
    U --> V[Run Tests]
    V --> W[Verify Endpoints]
    W --> X[Production Ready]
    
    style A fill:#90EE90
    style M fill:#87CEEB
    style U fill:#FFD700
    style X fill:#90EE90
```

## 4. Multi-Environment Strategy

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_STACK[CloudFormation Stack<br/>ure-mvp-dev]
        DEV_LAMBDA[Lambda: ure-mvp-handler-dev]
        DEV_API[API: /dev/query]
        DEV_DDB[DynamoDB: ure-conversations-dev]
    end
    
    subgraph "Staging Environment"
        STG_STACK[CloudFormation Stack<br/>ure-mvp-staging]
        STG_LAMBDA[Lambda: ure-mvp-handler-staging]
        STG_API[API: /staging/query]
        STG_DDB[DynamoDB: ure-conversations-staging]
    end
    
    subgraph "Production Environment"
        PROD_STACK[CloudFormation Stack<br/>ure-mvp-prod]
        PROD_LAMBDA[Lambda: ure-mvp-handler-prod]
        PROD_API[API: /prod/query]
        PROD_DDB[DynamoDB: ure-conversations-prod]
    end
    
    DEV_STACK --> STG_STACK
    STG_STACK --> PROD_STACK
    
    style DEV_STACK fill:#87CEEB
    style STG_STACK fill:#FFD700
    style PROD_STACK fill:#90EE90
```

## 5. Scaling Architecture

```mermaid
graph TB
    subgraph "Auto-Scaling Components"
        subgraph "Lambda Scaling"
            L1[Lambda Instance 1]
            L2[Lambda Instance 2]
            L3[Lambda Instance N]
            LC[Concurrency: 100<br/>Max: 1000]
        end
        
        subgraph "API Gateway Scaling"
            API[API Gateway]
            THROTTLE[Throttling<br/>Rate: 1000/s<br/>Burst: 2000]
        end
        
        subgraph "DynamoDB Scaling"
            DDB[DynamoDB Tables]
            ONDEMAND[On-Demand Billing<br/>Auto-scales capacity]
        end
        
        subgraph "S3 Scaling"
            S3[S3 Bucket]
            UNLIMITED[Unlimited storage<br/>Unlimited requests]
        end
    end
    
    USER[Users] --> API
    API --> THROTTLE
    THROTTLE --> L1
    THROTTLE --> L2
    THROTTLE --> L3
    
    L1 --> DDB
    L2 --> DDB
    L3 --> DDB
    
    L1 --> S3
    L2 --> S3
    L3 --> S3
    
    LC -.controls.-> L1
    LC -.controls.-> L2
    LC -.controls.-> L3
    
    ONDEMAND -.controls.-> DDB
    
    style USER fill:#90EE90
    style API fill:#87CEEB
    style L1 fill:#FFD700
    style L2 fill:#FFD700
    style L3 fill:#FFD700
    style DDB fill:#FFA500
    style S3 fill:#FFA500
```

## 6. High Availability Architecture

```mermaid
graph TB
    subgraph "Multi-AZ Deployment"
        subgraph "Availability Zone 1"
            AZ1_LAMBDA[Lambda Instances]
            AZ1_DDB[DynamoDB Replica]
        end
        
        subgraph "Availability Zone 2"
            AZ2_LAMBDA[Lambda Instances]
            AZ2_DDB[DynamoDB Replica]
        end
        
        subgraph "Availability Zone 3"
            AZ3_LAMBDA[Lambda Instances]
            AZ3_DDB[DynamoDB Replica]
        end
    end
    
    subgraph "Regional Services"
        APIGW[API Gateway<br/>Regional Endpoint]
        S3[S3 Bucket<br/>Multi-AZ Replication]
        BEDROCK[Bedrock<br/>Regional Service]
    end
    
    USER[Users] --> APIGW
    
    APIGW --> AZ1_LAMBDA
    APIGW --> AZ2_LAMBDA
    APIGW --> AZ3_LAMBDA
    
    AZ1_LAMBDA --> AZ1_DDB
    AZ2_LAMBDA --> AZ2_DDB
    AZ3_LAMBDA --> AZ3_DDB
    
    AZ1_LAMBDA --> S3
    AZ2_LAMBDA --> S3
    AZ3_LAMBDA --> S3
    
    AZ1_LAMBDA --> BEDROCK
    AZ2_LAMBDA --> BEDROCK
    AZ3_LAMBDA --> BEDROCK
    
    style USER fill:#90EE90
    style APIGW fill:#87CEEB
    style AZ1_LAMBDA fill:#FFD700
    style AZ2_LAMBDA fill:#FFD700
    style AZ3_LAMBDA fill:#FFD700
```

## 7. Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            HTTPS[HTTPS Only<br/>TLS 1.2+]
            APIGW[API Gateway<br/>Throttling & WAF]
        end
        
        subgraph "Identity & Access"
            IAM[IAM Roles<br/>Least Privilege]
            POLICY[Resource Policies<br/>S3, DynamoDB, KMS]
        end
        
        subgraph "Data Security"
            KMS[KMS Encryption<br/>At Rest]
            TLS[TLS Encryption<br/>In Transit]
            GUARD[Bedrock Guardrails<br/>Content Filtering]
        end
        
        subgraph "Application Security"
            INPUT[Input Validation]
            OUTPUT[Output Sanitization]
            PII[PII Anonymization]
        end
        
        subgraph "Monitoring Security"
            CW[CloudWatch Logs<br/>Encrypted]
            AUDIT[Audit Trail<br/>All API Calls]
            ALARM[Security Alarms<br/>Anomaly Detection]
        end
    end
    
    USER[User Request] --> HTTPS
    HTTPS --> APIGW
    APIGW --> IAM
    IAM --> INPUT
    INPUT --> GUARD
    GUARD --> KMS
    KMS --> OUTPUT
    OUTPUT --> PII
    PII --> CW
    CW --> AUDIT
    AUDIT --> ALARM
    
    style HTTPS fill:#DC143C
    style IAM fill:#DC143C
    style KMS fill:#DC143C
    style GUARD fill:#DC143C
    style ALARM fill:#20B2AA
```

## 8. Disaster Recovery Architecture

```mermaid
flowchart TD
    A[Production System] --> B{Failure Type?}
    
    B -->|Lambda failure| C[Auto-retry<br/>3 attempts]
    B -->|API Gateway failure| D[AWS auto-recovery<br/>Multi-AZ]
    B -->|DynamoDB failure| E[AWS auto-recovery<br/>Multi-AZ replication]
    B -->|S3 failure| F[AWS auto-recovery<br/>11 9s durability]
    B -->|Bedrock failure| G[Retry with backoff<br/>Fallback to cache]
    B -->|MCP server failure| H[Fallback to cache<br/>Stale data]
    
    C --> I{Recovered?}
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I -->|Yes| J[Resume normal operation]
    I -->|No| K[Trigger alarm]
    
    K --> L[SNS notification]
    L --> M[Admin intervention]
    M --> N[Manual recovery]
    
    N --> O{Stack delete?}
    O -->|Yes| P[Redeploy from CloudFormation]
    O -->|No| Q[Fix specific resource]
    
    P --> R[Restore from backup]
    Q --> R
    R --> J
    
    style A fill:#90EE90
    style C fill:#FFA500
    style K fill:#FF6B6B
    style J fill:#90EE90
```

## 9. Cost Optimization Architecture

```mermaid
graph TB
    subgraph "Cost Controls"
        subgraph "Lambda Optimization"
            L1[Reserved Concurrency: 100<br/>Prevents runaway costs]
            L2[Memory: 512MB<br/>Balanced performance/cost]
            L3[Timeout: 30s<br/>Prevents long-running costs]
        end
        
        subgraph "API Gateway Optimization"
            A1[Throttling: 1000/s<br/>Prevents abuse]
            A2[Caching: Disabled<br/>Save on cache costs]
        end
        
        subgraph "DynamoDB Optimization"
            D1[On-Demand Billing<br/>Pay per request]
            D2[TTL: 30 days<br/>Auto-delete old data]
        end
        
        subgraph "S3 Optimization"
            S1[Lifecycle Policy<br/>Delete after 30 days]
            S2[Intelligent Tiering<br/>Auto-move to cheaper storage]
        end
        
        subgraph "Bedrock Optimization"
            B1[Inference Profile<br/>Cross-region routing]
            B2[Prompt Caching<br/>Reduce token costs]
        end
        
        subgraph "MCP Optimization"
            M1[TTL Cache: 5 min<br/>Reduce API calls]
            M2[Batch Requests<br/>Combine multiple calls]
        end
    end
    
    COST[Total Cost: ~$73/month] --> L1
    COST --> A1
    COST --> D1
    COST --> S1
    COST --> B1
    COST --> M1
    
    style COST fill:#90EE90
    style L1 fill:#87CEEB
    style A1 fill:#87CEEB
    style D1 fill:#FFA500
    style S1 fill:#FFA500
    style B1 fill:#FF6B6B
    style M1 fill:#9370DB
```

## 10. Deployment Checklist

```mermaid
flowchart TD
    A[Start Deployment] --> B{Prerequisites?}
    
    B -->|AWS CLI installed| C{AWS credentials configured?}
    B -->|No| Z[Install AWS CLI]
    
    C -->|Yes| D{Environment variables set?}
    C -->|No| Y[Configure credentials]
    
    D -->|Yes| E[Deploy CloudFormation]
    D -->|No| X[Set .env variables]
    
    E --> F{Stack created?}
    F -->|Yes| G[Deploy Lambda code]
    F -->|No| W[Check CloudFormation errors]
    
    G --> H{Code deployed?}
    H -->|Yes| I[Start MCP servers]
    H -->|No| V[Check Lambda errors]
    
    I --> J{Servers running?}
    J -->|Yes| K[Test API endpoint]
    J -->|No| U[Check server logs]
    
    K --> L{API working?}
    L -->|Yes| M[Verify monitoring]
    L -->|No| T[Check API Gateway logs]
    
    M --> N{Alarms configured?}
    N -->|Yes| O[Run integration tests]
    N -->|No| S[Configure alarms]
    
    O --> P{Tests passing?}
    P -->|Yes| Q[Deployment Complete ✅]
    P -->|No| R[Debug and fix]
    
    R --> K
    S --> O
    T --> K
    U --> I
    V --> G
    W --> E
    X --> D
    Y --> C
    Z --> B
    
    style A fill:#FFD700
    style Q fill:#90EE90
    style W fill:#FF6B6B
    style V fill:#FF6B6B
    style U fill:#FF6B6B
    style T fill:#FF6B6B
    style R fill:#FF6B6B
```

---

**Version**: 1.0.0  
**Last Updated**: February 28, 2026
