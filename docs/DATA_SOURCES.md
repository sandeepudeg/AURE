# URE MVP Data Sources & Extraction Guide

This document outlines all data sources for the Unified Rural Ecosystem (URE) MVP and how agents extract data based on user queries.

## Data Architecture Overview

```
User Query → Supervisor Agent → Specialist Agent → Data Source
                                                   ↓
                                    MCP Client / Bedrock KB / S3
```

---

## 1. Agri-Expert Agent Data Sources

### 1.1 Indian Mandi Prices (Agmarknet)

**Source**: https://www.agmarknet.gov.in/  
**Kaggle Dataset**: [Indian Agricultural Mandi Prices (2023-2025)](https://www.kaggle.com/datasets/arjunyadav99/indian-agricultural-mandi-prices-20232025)

**Data Contains**:
- Daily market prices for major crops: Onion, Tomato, Potato, Wheat, Rice
- Coverage: All districts across India
- Format: CSV with columns: date, crop, district, state, price, market_name

**Access Method**: MCP Client → Agmarknet MCP Server
- Tool: `get_mandi_prices`
- Parameters: `{crop, district, state}`
- Response: `{price, market, date}`

**Example Query Flow**:
```
User: "What is the wheat price in Nashik?"
  ↓
Supervisor → Agri-Expert
  ↓
MCP Client.call_tool('get_mandi_prices', 'Agri-Expert', {
  crop: 'wheat',
  district: 'Nashik',
  state: 'Maharashtra'
})
  ↓
Response: "₹2500/quintal at Nashik APMC (2026-01-13)"
```

### 1.2 PlantVillage Dataset

**Source**: PlantVillage (via Kaggle/GitHub)  
**Size**: 50,000+ images of healthy and diseased crop leaves

**Data Contains**:
- Image categories: 38 disease classes across 14 crop species
- Format: JPG images organized by crop and disease type
- Metadata: Disease name, crop type, severity level

**Storage**: 
- S3 Bucket: `knowledge-base-bharat/plantvillage/`
- OpenSearch: Vector embeddings for similarity search

**Access Method**: 
1. User uploads image → Stored in S3
2. Generate embedding using Titan Multimodal
3. Search OpenSearch for similar images
4. Claude 3.5 Sonnet analyzes image + top matches
5. Return disease identification + confidence

**Example Query Flow**:
```
User: [Uploads wheat leaf image]
  ↓
Supervisor → Agri-Expert
  ↓
1. Store image: S3.upload('uploads/farmer_12345_image.jpg')
2. Generate embedding: Bedrock.Titan.embed(image)
3. Search: OpenSearch.similarity_search(embedding, top_k=3)
4. Analyze: Claude.analyze(image, similar_images)
  ↓
Response: "Yellow Rust (85% confidence). Treatment: Neem oil spray."
```

---

## 2. Policy-Navigator Agent Data Sources

### 2.1 Data.gov.in (Government Schemes)

**Source**: https://data.gov.in/

**Key Datasets**:
- PM-Kisan Scheme Details (PDF)
- Paramparagat Krishi Vikas Yojana (PKVY) - CSV
- Agricultural Subsidy Allocation - Excel

**Data Contains**:
- Scheme eligibility criteria
- Subsidy amounts and payment schedules
- Application procedures and required documents
- Contact information for local offices

**Storage**: 
- S3 Bucket: `knowledge-base-bharat/schemes/`
- Bedrock Knowledge Base: RAG-enabled for semantic search

**Access Method**: Bedrock Knowledge Base RAG Query
- Query: Natural language question
- Response: Retrieved context + LLM-generated answer

**Example Query Flow**:
```
User: "Am I eligible for PM-Kisan if I have 1.5 hectares?"
  ↓
Supervisor → Policy-Navigator
  ↓
1. RAG Query: BedrockKB.search("PM-Kisan eligibility 1.5 hectares")
2. Retrieved Context: "Small/marginal farmers with <2 hectares eligible"
3. Check User Profile: DynamoDB.get_item(user_id)
4. Assess Eligibility: farm_size=1.5 < 2 → Eligible
  ↓
Response: "Yes, eligible for ₹6000/year in 3 installments."
```

### 2.2 Village Amenities (Census 2011)

**Source**: https://data.gov.in/keywords/village-amenities

**Data Contains**:
- Distance to nearest town (km)
- Availability of schools, hospitals, banks
- Irrigation types: Canal, Well, Drip, Rainfed
- Electricity availability

**Storage**: DynamoDB Table: `ure-village-amenities`
- Partition Key: `village_name`
- Attributes: `district, state, irrigation_type, distance_to_town, facilities`

**Access Method**: DynamoDB Query
- Query: `get_item(Key={'village_name': 'Nashik'})`

**Example Query Flow**:
```
User: "What irrigation facilities are available in my village?"
  ↓
Supervisor → Policy-Navigator
  ↓
DynamoDB.get_item(Key={'village_name': user.location.village})
  ↓
Response: "Canal irrigation available. Distance to town: 12 km."
```

---

## 3. Resource-Optimizer Agent Data Sources

### 3.1 Weather Data (IMD / MCP Weather Server)

**Source**: Indian Meteorological Department (IMD) via MCP Server

**Data Contains**:
- Current weather: Temperature, humidity, wind speed, rainfall
- Forecast (3-7 days): Rain probability, temperature range
- Historical patterns: Seasonal averages

**Access Method**: MCP Client → Weather MCP Server
- Tools: `get_current_weather`, `get_weather_forecast`
- Parameters: `{location, days, units}`

**Example Query Flow**:
```
User: "When should I irrigate my wheat field?"
  ↓
Supervisor → Resource-Optimizer
  ↓
1. Get Weather: MCP.call_tool('get_weather_forecast', {
     location: 'Nashik',
     days: 3
   })
2. Get Soil Moisture: S3.get_object('sensor_data/farmer_12345.json')
3. Calculate ET: hargreaves_samani(temp=35, humidity=40)
4. Decision Logic:
   - moisture=0.4 (low)
   - rain_probability=60% in 12 hours
   - Recommendation: Wait for rain
  ↓
Response: "Wait for rain (60% probability in 12 hours). Save ₹200 on electricity."
```

### 3.2 AgriFieldNet (Crop Type Data)

**Source**: https://source.coop/radiantearth/agrifieldnet-competition

**Data Contains**:
- Ground-truthed crop types for Northern India
- Coverage: Bihar, Odisha, Rajasthan, Uttar Pradesh
- Format: Geospatial data (GeoJSON/Shapefile)

**Storage**: S3 Bucket: `knowledge-base-bharat/agrifieldnet/`

**Access Method**: S3 Query + Geospatial Analysis
- Query by coordinates or district
- Return crop type distribution

**Example Query Flow**:
```
User: "What crops are grown in my area?"
  ↓
Supervisor → Resource-Optimizer
  ↓
S3.query_geospatial(location=user.coordinates)
  ↓
Response: "Wheat (60%), Cotton (30%), Vegetables (10%)"
```

---

## Data Extraction Patterns by Query Type

### Query Type 1: Market Prices
**User Query**: "What is the tomato price today?"
**Agent**: Agri-Expert
**Data Source**: Agmarknet MCP Server
**Extraction**: `MCP.call_tool('get_mandi_prices', {crop: 'tomato', district: user.district})`

### Query Type 2: Disease Identification
**User Query**: [Image upload]
**Agent**: Agri-Expert
**Data Sources**: S3 (PlantVillage) + OpenSearch + Claude
**Extraction**: 
1. S3.upload(image)
2. OpenSearch.similarity_search(embedding)
3. Claude.analyze(image, context)

### Query Type 3: Scheme Eligibility
**User Query**: "Can I get PM-Kisan subsidy?"
**Agent**: Policy-Navigator
**Data Sources**: Bedrock KB + DynamoDB
**Extraction**:
1. BedrockKB.rag_query("PM-Kisan eligibility")
2. DynamoDB.get_item(user_profile)
3. Eligibility logic

### Query Type 4: Irrigation Advice
**User Query**: "Should I water my crops today?"
**Agent**: Resource-Optimizer
**Data Sources**: Weather MCP Server + S3 (sensor data)
**Extraction**:
1. MCP.call_tool('get_weather_forecast')
2. S3.get_object('sensor_data')
3. Calculate ET + decision logic

---

## Data Storage Architecture

```
S3 Bucket: knowledge-base-bharat/
├── plantvillage/          # 50,000+ crop disease images
├── schemes/               # Government scheme PDFs
├── agrifieldnet/          # Crop type geospatial data
├── sensor_data/           # Soil moisture JSON logs
└── uploads/               # User-uploaded images

DynamoDB Tables:
├── ure-conversations      # Chat history
├── ure-village-amenities  # Village infrastructure data
└── ure-user-profiles      # Farmer profiles

Bedrock Knowledge Base:
├── PM-Kisan Scheme PDF
├── PKVY Guidelines
└── Agricultural Subsidy Rules

OpenSearch Serverless:
└── PlantVillage embeddings (vector search)

MCP Servers:
├── Agmarknet Server       # Market prices API
└── Weather Server         # IMD weather data
```

---

## Next Steps for Implementation

1. **Data Ingestion Scripts** (TASK-1.4):
   - Download PlantVillage dataset → Upload to S3
   - Download Agmarknet CSV → Configure MCP Server
   - Download PM-Kisan PDF → Upload to Bedrock KB

2. **MCP Server Setup** (TASK-2.9):
   - Deploy Agmarknet MCP Server (or mock)
   - Deploy Weather MCP Server (or mock)
   - Test all 4 MCP tools

3. **Bedrock KB Configuration** (TASK-1.3):
   - Create OpenSearch Serverless collection
   - Upload scheme PDFs to S3
   - Index documents in Bedrock KB

4. **DynamoDB Schema** (TASK-1.2):
   - Create `ure-village-amenities` table
   - Populate with Census 2011 data
   - Create indexes for fast queries

---

## Data Update Frequency

| Data Source | Update Frequency | Responsibility |
|-------------|------------------|----------------|
| Mandi Prices | Daily | Agmarknet API |
| Weather Data | Hourly | IMD via MCP |
| Scheme PDFs | Quarterly | Manual upload |
| PlantVillage | Static | One-time upload |
| Village Data | Annual | Census updates |
| Sensor Data | Real-time | IoT devices |

---

**Last Updated**: 2026-02-27  
**Maintained By**: URE Development Team
