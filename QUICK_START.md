# URE MVP - Quick Start Guide

## Prerequisites

✅ Virtual environment `rural` created and activated
✅ All packages installed from `requirements.txt`
✅ AWS credentials configured in `~/.aws/credentials`
✅ Data uploaded to S3 and DynamoDB

## Testing the Agents

### Option 1: Test Individual Agents

```bash
py test_agents.py
```

This will test:
1. **Agri-Expert Agent** - Crop disease diagnosis
2. **Policy-Navigator Agent** - Government scheme information
3. **Resource-Optimizer Agent** - Irrigation and weather recommendations
4. **Supervisor Agent** - Query routing

### Option 2: Interactive Testing

```python
# Activate virtual environment
# Windows:
rural\Scripts\activate

# Import agents
from src.agents import supervisor_agent

# Test queries
response = supervisor_agent("My wheat has yellow spots")
print(response)

response = supervisor_agent("Am I eligible for PM-Kisan?")
print(response)

response = supervisor_agent("When should I water my crops?")
print(response)
```

## Expected Behavior

### Without Bedrock Knowledge Base

#### ✅ Will Work:
- **Agri-Expert**: Uses Claude 3.5 Sonnet for crop disease diagnosis
- **Resource-Optimizer**: Uses weather API and irrigation logic
- **Supervisor**: Routes queries to appropriate agents

#### ⚠️ Limited Functionality:
- **Policy-Navigator**: Cannot access PM-Kisan scheme documents
  - Will provide general information based on model knowledge
  - For full functionality, complete Bedrock KB setup

### With Bedrock Knowledge Base

All agents will have full functionality including:
- Policy-Navigator can retrieve specific scheme details from PDFs
- Accurate eligibility criteria
- Application procedures
- Benefit amounts

## Running the Streamlit UI

```bash
streamlit run src/ui/app.py
```

**Note**: The UI file needs to be created. This is the next step in development.

## Configuration

### Environment Variables (`.env`)

```bash
# AWS Configuration
AWS_REGION=ap-south-1
BEDROCK_REGION=us-east-1

# AWS Resources
S3_BUCKET_NAME=ure-mvp-data-188238313375
DYNAMODB_TABLE_NAME=ure-conversations
DYNAMODB_VILLAGE_TABLE=ure-village-amenities
DYNAMODB_USER_TABLE=ure-user-profiles

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_KB_ID=pending_manual_setup

# MCP Configuration
MCP_TOOL_REGISTRY_PATH=src/mcp/tool_registry.json
```

## Troubleshooting

### Issue: Import Error

```bash
ModuleNotFoundError: No module named 'src'
```

**Solution**: Run from project root directory:
```bash
cd D:\Learning\Assembler_URE_Rural
py test_agents.py
```

### Issue: AWS Credentials Not Found

```bash
NoCredentialsError: Unable to locate credentials
```

**Solution**: Configure AWS credentials:
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: ap-south-1
# Default output format: json
```

### Issue: Bedrock Model Access Denied

```bash
AccessDeniedException: Could not access model
```

**Solution**: Enable model access in Bedrock console:
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Enable "Claude 3.5 Sonnet"
4. Wait for approval (usually instant)

### Issue: Agent Returns Empty Response

**Possible Causes**:
1. Model not responding - check Bedrock service status
2. Invalid API call - check logs for error messages
3. Timeout - increase timeout in agent configuration

**Solution**: Check logs and verify model access

## Next Steps

### 1. Complete Bedrock KB Setup (Optional)
Follow `BEDROCK_KB_MANUAL_SETUP.md` to enable full Policy-Navigator functionality.

### 2. Set Up MCP Servers
For live market prices and weather data:
- Agmarknet MCP server
- Weather MCP server

### 3. Create Streamlit UI
Build the user interface for farmer interactions.

### 4. Deploy to Production
Options:
- AWS Lambda + API Gateway
- AWS Fargate (containerized)
- EC2 instance

## Sample Test Queries

### Agri-Expert
```
"My tomato plants have brown spots on leaves"
"What causes wheat rust disease?"
"How to treat cotton boll weevil?"
"Current market price for onions in Nashik"
```

### Policy-Navigator
```
"Am I eligible for PM-Kisan if I have 1.5 hectares?"
"What documents do I need for PM-Kisan registration?"
"What is the benefit amount for PM-Kisan?"
"How do I apply for crop insurance?"
```

### Resource-Optimizer
```
"When should I irrigate my wheat crop?"
"What's the weather forecast for next week?"
"Should I water my crops today? Soil moisture is 0.4"
"Best time to plant cotton in Maharashtra?"
```

### Supervisor (Auto-routing)
```
"My wheat has yellow spots" → Routes to Agri-Expert
"Am I eligible for PM-Kisan?" → Routes to Policy-Navigator
"When should I water crops?" → Routes to Resource-Optimizer
```

## Performance Expectations

### Response Times
- **Agri-Expert**: 2-5 seconds (Claude 3.5 Sonnet)
- **Policy-Navigator**: 3-7 seconds (with KB retrieval)
- **Resource-Optimizer**: 1-3 seconds (weather API)
- **Supervisor**: +1 second (routing overhead)

### Accuracy
- **Crop Disease Diagnosis**: High (based on Claude 3.5 Sonnet)
- **Scheme Information**: Medium without KB, High with KB
- **Weather Recommendations**: High (real-time data)

## Cost Per Query

### Without Bedrock KB
- Claude 3.5 Sonnet: ~$0.003 per query
- DynamoDB: ~$0.000001 per query
- **Total**: ~$0.003 per query

### With Bedrock KB
- Claude 3.5 Sonnet: ~$0.003 per query
- Bedrock KB retrieval: ~$0.0001 per query
- DynamoDB: ~$0.000001 per query
- **Total**: ~$0.0031 per query

**Monthly Cost Estimate** (1000 queries/month):
- Without KB: ~$3/month
- With KB: ~$3.10/month + $700 OpenSearch Serverless

## Support

For issues or questions:
1. Check `AWS_SETUP_SUMMARY.md` for resource status
2. Review `BEDROCK_KB_MANUAL_SETUP.md` for KB setup
3. Check AWS CloudWatch logs for detailed error messages
4. Verify `.env` configuration

## Development Roadmap

- [x] Agent implementation (Agri-Expert, Policy-Navigator, Resource-Optimizer, Supervisor)
- [x] AWS infrastructure setup (S3, DynamoDB, OpenSearch)
- [x] Data ingestion (PlantVillage, Government PDFs, Market prices)
- [ ] Bedrock Knowledge Base setup (manual)
- [ ] MCP server integration
- [ ] Streamlit UI development
- [ ] Testing and validation
- [ ] Production deployment
- [ ] Monitoring and logging
- [ ] Performance optimization
