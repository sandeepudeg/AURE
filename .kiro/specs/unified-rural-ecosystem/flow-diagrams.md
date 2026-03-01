# URE Process Flow Diagrams

## 1. High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         FARMER USER                             │
│  (Web, WhatsApp, Telegram, Voice)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   INPUT PROCESSING             │
        │ ┌──────────────────────────┐   │
        │ │ • Parse text/image/voice │   │
        │ │ • Validate input         │   │
        │ │ • Extract user context   │   │
        │ └──────────────────────────┘   │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   SUPERVISOR AGENT             │
        │ ┌──────────────────────────┐   │
        │ │ • Classify query type    │   │
        │ │ • Route to agent(s)      │   │
        │ │ • Orchestrate flow       │   │
        │ └──────────────────────────┘   │
        └────────────┬───────────────────┘
                     │
        ┌────────────┴────────────┬──────────────┐
        │                         │              │
        ▼                         ▼              ▼
   ┌─────────────┐         ┌──────────────┐  ┌──────────────┐
   │ Agri-Expert │         │Policy-Nav    │  │Resource-Opt  │
   │   Agent     │         │   Agent      │  │   Agent      │
   └─────────────┘         └──────────────┘  └──────────────┘
        │                         │              │
        ▼                         ▼              ▼
   ┌─────────────┐         ┌──────────────┐  ┌──────────────┐
   │ • Analyze   │         │ • Search KB  │  │ • Calculate  │
   │   image     │         │ • Check      │  │   ET         │
   │ • Identify  │         │   eligibility│  │ • Analyze    │
   │   disease   │         │ • Get scheme │  │   soil       │
   │ • Fetch     │         │   details    │  │ • Fetch      │
   │   prices    │         │              │  │   weather    │
   └─────────────┘         └──────────────┘  └──────────────┘
        │                         │              │
        └────────────┬────────────┴──────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   RESPONSE SYNTHESIS           │
        │ ┌──────────────────────────┐   │
        │ │ • Combine agent outputs  │   │
        │ │ • Apply guardrails       │   │
        │ │ • Translate response     │   │
        │ └──────────────────────────┘   │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   PERSISTENCE & LOGGING        │
        │ ┌──────────────────────────┐   │
        │ │ • Store in DynamoDB      │   │
        │ │ • Log to CloudWatch      │   │
        │ │ • Update user context    │   │
        │ └──────────────────────────┘   │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   RESPONSE DELIVERY            │
        │ ┌──────────────────────────┐   │
        │ │ • Format response        │   │
        │ │ • Send to user channel   │   │
        │ │ • Display in UI          │   │
        │ └──────────────────────────┘   │
        └────────────┬───────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FARMER RECEIVES RESPONSE                     │
│  (Web, WhatsApp, Telegram, Voice)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Disease Identification Flow

```
FARMER UPLOADS CROP IMAGE
        │
        ▼
┌──────────────────────────┐
│ 1. UPLOAD TO S3          │
│ • Store image in S3      │
│ • Generate unique URL    │
│ • Encrypt with KMS       │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 2. GENERATE EMBEDDING    │
│ • Use Titan Multimodal   │
│ • Create vector          │
│ • Store in OpenSearch    │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 3. SEARCH PLANTVILLAGE   │
│ • Query OpenSearch       │
│ • Find similar images    │
│ • Retrieve top 3 matches │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 4. ANALYZE WITH CLAUDE   │
│ • Send image + matches   │
│ • Claude 3.5 Sonnet      │
│ • Identify disease       │
│ • Confidence score       │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 5. FETCH TREATMENT       │
│ • Query Bedrock KB       │
│ • Get treatment options  │
│ • Organic + Chemical     │
│ • Cost estimate          │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 6. FETCH MARKET PRICES   │
│ • Query Agmarknet API    │
│ • Get current prices     │
│ • Historical trends      │
│ • Best markets           │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 7. APPLY GUARDRAILS      │
│ • Check for harmful      │
│   advice                 │
│ • Validate response      │
│ • Block if unsafe        │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 8. TRANSLATE RESPONSE    │
│ • Detect language        │
│ • Translate to Hindi/    │
│   Marathi/etc            │
│ • Format for channel     │
└──────────────────────────┘
        │
        ▼
RETURN TO FARMER:
• Disease: Yellow Rust (85% confidence)
• Treatment: Neem oil + soap water
• Cost: ₹500-1000
• Market price: ₹2500/quintal
• Best market: Nashik Mandi
```

---

## 3. PM-Kisan Eligibility Flow

```
FARMER ASKS: "Am I eligible for PM-Kisan?"
        │
        ▼
┌──────────────────────────┐
│ 1. SEARCH KNOWLEDGE BASE │
│ • Query Bedrock KB       │
│ • Retrieve PM-Kisan docs │
│ • Extract eligibility    │
│   criteria               │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 2. RETRIEVE CRITERIA     │
│ • Must be farmer         │
│ • Must own land          │
│ • Income < ₹2 lakh/year  │
│ • Age requirements       │
│ • State-specific rules   │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 3. CHECK FARMER PROFILE  │
│ • Query DynamoDB         │
│ • Get farmer details     │
│ • Land ownership         │
│ • Income level           │
│ • Location/state         │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 4. ASSESS ELIGIBILITY    │
│ • Compare criteria       │
│ • Check all conditions   │
│ • Identify gaps          │
│ • Calculate subsidy      │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 5. GET APPLICATION INFO  │
│ • Retrieve from KB       │
│ • Step-by-step process   │
│ • Required documents     │
│ • Application deadline   │
│ • Contact info           │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 6. APPLY GUARDRAILS      │
│ • Validate response      │
│ • Check for errors       │
│ • Verify accuracy        │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 7. TRANSLATE RESPONSE    │
│ • Convert to user lang   │
│ • Format for channel     │
└──────────────────────────┘
        │
        ▼
RETURN TO FARMER:
• Eligible: YES
• Subsidy: ₹6000/year
• Application: Online at pmkisan.gov.in
• Documents: Aadhar, Land deed, Bank account
• Deadline: 31 Dec 2026
```

---

## 4. Irrigation Recommendation Flow

```
FARMER ASKS: "Should I irrigate today?"
        │
        ▼
┌──────────────────────────┐
│ 1. RETRIEVE SENSOR DATA  │
│ • Query S3 for logs      │
│ • Get latest readings    │
│ • Soil moisture          │
│ • Temperature            │
│ • Humidity               │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 2. FETCH WEATHER DATA    │
│ • Query IMD API          │
│ • Get forecast           │
│ • Temperature            │
│ • Rainfall probability   │
│ • Wind speed             │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 3. CALCULATE ET          │
│ • Hargreaves-Samani      │
│ • Reference ET (ET0)     │
│ • Crop coefficient       │
│ • Actual ET (ETc)        │
│ • Daily water need       │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 4. ANALYZE SOIL MOISTURE │
│ • Current level: 0.4     │
│ • Threshold: 0.3         │
│ • Wilting point: 0.15    │
│ • Field capacity: 0.8    │
│ • Available water        │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 5. DECISION LOGIC        │
│ IF moisture < 0.3 AND    │
│    rain predicted        │
│    → WAIT FOR RAIN       │
│ ELSE IF moisture < 0.3   │
│    → IRRIGATE NOW        │
│ ELSE IF moisture > 0.7   │
│    → DON'T IRRIGATE      │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 6. OPTIMIZE SCHEDULE     │
│ • Best time to irrigate  │
│ • Duration needed        │
│ • Pump schedule          │
│ • Cost estimate          │
│ • Water savings          │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 7. APPLY GUARDRAILS      │
│ • Validate recommendation│
│ • Check for errors       │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 8. TRANSLATE RESPONSE    │
│ • Convert to user lang   │
│ • Format for channel     │
└──────────────────────────┘
        │
        ▼
RETURN TO FARMER:
• Recommendation: WAIT FOR RAIN
• Probability: 60% in 12 hours
• If no rain: Irrigate tomorrow
• Duration: 2 hours
• Cost: ₹200
• Water saved: 5000 liters
```

---

## 5. Multi-Agent Orchestration Flow

```
COMPLEX QUERY: "My wheat has yellow spots. 
What's the market price? Should I irrigate? Am I eligible for subsidy?"
        │
        ▼
┌──────────────────────────┐
│ SUPERVISOR AGENT         │
│ • Classify query         │
│ • Identify 4 domains:    │
│   1. Disease (Agri)      │
│   2. Market (Agri)       │
│   3. Irrigation (Resource)
│   4. Subsidy (Policy)    │
└──────────────────────────┘
        │
        ├──────────────────────────────────────────────────┐
        │                                                  │
        ├─────────────────────────┐                        │
        │                         │                        │
        ▼                         ▼                        ▼
   ┌─────────────┐         ┌──────────────┐         ┌──────────────┐
   │ Agri-Expert │         │Policy-Nav    │         │Resource-Opt  │
   │   Agent     │         │   Agent      │         │   Agent      │
   └─────────────┘         └──────────────┘         └──────────────┘
        │                         │                        │
        ├─ Analyze image          ├─ Search KB             ├─ Fetch weather
        ├─ Identify disease       ├─ Check eligibility     ├─ Get soil data
        ├─ Fetch treatment        ├─ Get subsidy info      ├─ Calculate ET
        └─ Fetch prices           └─ Get application       ├─ Analyze moisture
                                     process               └─ Optimize schedule
        │                         │                        │
        └──────────────────────────┴────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────┐
                        │ RESPONSE SYNTHESIS       │
                        │ • Combine all outputs    │
                        │ • Resolve conflicts      │
                        │ • Create unified response│
                        │ • Apply guardrails       │
                        │ • Translate              │
                        └──────────────────────────┘
                                   │
                                   ▼
RETURN TO FARMER:
• Disease: Yellow Rust (85%)
• Treatment: Neem oil
• Market price: ₹2500/quintal
• Irrigation: WAIT FOR RAIN (60% probability)
• Subsidy: 20% available
• Application: Online at pmkisan.gov.in
```

---

## 6. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FARMER INPUT                            │
│  (Web, WhatsApp, Telegram, Voice)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   API GATEWAY                  │
        │ • Route requests               │
        │ • Validate input               │
        │ • Rate limiting                │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   LAMBDA FUNCTION              │
        │ • Parse request                │
        │ • Retrieve user context        │
        │ • Invoke Supervisor            │
        │ • Store response               │
        └────────────┬───────────────────┘
                     │
        ┌────────────┴────────────┬──────────────┐
        │                         │              │
        ▼                         ▼              ▼
   ┌─────────────┐         ┌──────────────┐  ┌──────────────┐
   │ Agri-Expert │         │Policy-Nav    │  │Resource-Opt  │
   │   Agent     │         │   Agent      │  │   Agent      │
   └─────────────┘         └──────────────┘  └──────────────┘
        │                         │              │
        ├─ S3 (images)            ├─ Bedrock KB  ├─ S3 (sensor)
        ├─ OpenSearch             ├─ DynamoDB    ├─ IMD API
        ├─ Agmarknet API          ├─ RDS         ├─ OpenWeather
        └─ Bedrock KB             └─ data.gov.in └─ Python math
        │                         │              │
        └────────────┬────────────┴──────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   BEDROCK GUARDRAILS           │
        │ • Safety validation            │
        │ • Content filtering            │
        │ • Accuracy checking            │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   AMAZON TRANSLATE             │
        │ • Language detection           │
        │ • Response translation         │
        │ • Format conversion            │
        └────────────┬───────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────────┐         ┌──────────────┐
   │ DynamoDB    │         │ CloudWatch   │
   │ • Store     │         │ • Logs       │
   │   response  │         │ • Metrics    │
   │ • History   │         │ • Monitoring │
   └─────────────┘         └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO FARMER                           │
│  (Web, WhatsApp, Telegram, Voice)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Request-Response Cycle (Timing)

```
T=0ms    Farmer submits query
         │
T=50ms   │ API Gateway receives request
         │
T=100ms  │ Lambda function starts
         │
T=150ms  │ Retrieve user context from DynamoDB
         │
T=200ms  │ Invoke Supervisor Agent
         │
T=300ms  │ Supervisor classifies query
         │
T=350ms  │ Route to specialist agent(s)
         │
T=400ms  │ Specialist agents execute in parallel
         │ ├─ Agri-Expert: Analyze image (500ms)
         │ ├─ Policy-Nav: Search KB (300ms)
         │ └─ Resource-Opt: Calculate ET (200ms)
         │
T=900ms  │ All agents complete
         │
T=950ms  │ Supervisor synthesizes response
         │
T=1000ms │ Apply Bedrock Guardrails
         │
T=1050ms │ Translate response
         │
T=1100ms │ Store in DynamoDB
         │
T=1150ms │ Return to API Gateway
         │
T=1200ms │ Response delivered to Streamlit
         │
T=1250ms │ Display response to farmer
         │
TOTAL: ~1.25 seconds (Target: < 5 seconds)
```

---

## 8. Error Handling Flow

```
REQUEST RECEIVED
        │
        ▼
┌──────────────────────────┐
│ VALIDATE INPUT           │
│ • Check format           │
│ • Check size             │
│ • Check required fields  │
└──────────────────────────┘
        │
        ├─ VALID ──────────────────────────────┐
        │                                      │
        └─ INVALID                             │
                │                              │
                ▼                              │
        ┌──────────────────────────┐           │
        │ RETURN ERROR             │           │
        │ "Invalid input format"   │           │
        └──────────────────────────┘           │
                                               │
                                               ▼
                                    ┌──────────────────────────┐
                                    │ PROCESS REQUEST          │
                                    └──────────────────────────┘
                                               │
                                               ▼
                                    ┌──────────────────────────┐
                                    │ INVOKE AGENTS            │
                                    └──────────────────────────┘
                                               │
        ┌──────────────────────────────────────┼──────────────────────────────────────┐
        │                                      │                                      │
        ▼                                      ▼                                      ▼
┌──────────────────────────┐        ┌──────────────────────────┐        ┌──────────────────────────┐
│ AGENT TIMEOUT            │        │ API FAILURE              │        │ GUARDRAIL BLOCK          │
│ (> 10 seconds)           │        │ (External API down)      │        │ (Harmful content)        │
└──────────────────────────┘        └──────────────────────────┘        └──────────────────────────┘
        │                                   │                                   │
        ▼                                   ▼                                   ▼
┌──────────────────────────┐        ┌──────────────────────────┐        ┌──────────────────────────┐
│ FALLBACK RESPONSE        │        │ FALLBACK RESPONSE        │        │ SAFE RESPONSE            │
│ "Unable to analyze.      │        │ "Service unavailable.    │        │ "I cannot provide that   │
│ Please describe."        │        │ Please try again."       │        │ advice."                 │
└──────────────────────────┘        └──────────────────────────┘        └──────────────────────────┘
        │                                   │                                   │
        └───────────────────────────────────┴───────────────────────────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────────┐
                                    │ LOG ERROR                │
                                    │ • CloudWatch             │
                                    │ • Error details          │
                                    │ • Timestamp              │
                                    │ • User ID                │
                                    └──────────────────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────────┐
                                    │ RETURN RESPONSE          │
                                    │ (Error or Fallback)      │
                                    └──────────────────────────┘
```

---

## 9. Conversation History Flow

```
FIRST MESSAGE
        │
        ▼
┌──────────────────────────┐
│ 1. PROCESS QUERY         │
│ • Invoke agents          │
│ • Get response           │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 2. STORE IN DYNAMODB     │
│ • User message           │
│ • Assistant response     │
│ • Timestamp              │
│ • Agent used             │
│ • Confidence             │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 3. RETURN TO USER        │
│ • Display response       │
│ • Show history           │
└──────────────────────────┘
        │
        ▼
SECOND MESSAGE (FOLLOW-UP)
        │
        ▼
┌──────────────────────────┐
│ 1. RETRIEVE HISTORY      │
│ • Query DynamoDB         │
│ • Get last 10 messages   │
│ • Include context        │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 2. PROCESS WITH CONTEXT  │
│ • Include conversation   │
│   history in prompt      │
│ • Invoke agents          │
│ • Get contextual response│
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 3. APPEND TO HISTORY     │
│ • Add new message        │
│ • Add new response       │
│ • Update timestamp       │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ 4. RETURN TO USER        │
│ • Display response       │
│ • Show full history      │
└──────────────────────────┘
```

---

## 10. Multi-Channel Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    FARMER INPUT CHANNELS                        │
└─────────────────────────────────────────────────────────────────┘
        │
        ├─ WEB APP (Streamlit)
        │  └─ HTTP POST to API Gateway
        │
        ├─ WHATSAPP (Twilio)
        │  └─ Webhook to Lambda
        │
        ├─ TELEGRAM (Bot API)
        │  └─ Webhook to Lambda
        │
        └─ VOICE (Transcribe)
           └─ Audio → Transcribe → Lambda
        │
        ▼
┌──────────────────────────┐
│ CHANNEL ADAPTER          │
│ • Normalize input        │
│ • Extract user ID        │
│ • Detect language        │
│ • Convert to standard    │
│   format                 │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ UNIFIED BACKEND          │
│ • Lambda handler         │
│ • Supervisor agent       │
│ • Specialist agents      │
│ • Data sources           │
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│ RESPONSE FORMATTER       │
│ • Format for channel     │
│ • Translate to language  │
│ • Convert to media type  │
│   (text/image/voice)     │
└──────────────────────────┘
        │
        ├─ WEB APP
        │  └─ JSON response
        │
        ├─ WHATSAPP
        │  └─ WhatsApp message
        │
        ├─ TELEGRAM
        │  └─ Telegram message
        │
        └─ VOICE
           └─ Audio (Polly)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FARMER RECEIVES RESPONSE                     │
└─────────────────────────────────────────────────────────────────┘
```
