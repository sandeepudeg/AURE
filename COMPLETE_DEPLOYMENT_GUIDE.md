# URE MVP - Complete Deployment Guide

## Overview

This guide covers the complete deployment of the Unified Rural Ecosystem (URE) MVP to AWS, including all infrastructure components with proper security (IAM, KMS encryption), safety features (Bedrock Guardrails), and multi-language support (Amazon Translate).

## Prerequisites

- AWS Account (ID: 188238313375)
- AWS CLI configured with appropriate credentials
- Python 3.11+ installed
- Virtual environment activated (`rural`)
- All dependencies installed

## Deployment Steps

### Step 1: Create Bedrock Guardrails

Guardrails filter harmful content and off-topic responses.

```bash
# Create guardrails
py scripts/create_bedrock_guardrails.py create

# This will output a Guardrail ID - save it to .env
# BEDROCK_GUARDRAIL_ID=<guardrail-id>
```

**What it does:**
- Blocks harmful pesticides (DDT, Endosulfan, etc.)
- Blocks off-topic content (politics, religion, finance)
- Filters violence, hate speech, misconduct
- Anonymizes PII (email, phone, address)

### Step 2: Deploy CloudFormation Stack

Deploy all infrastructure with a single command.

```bash
# Deploy stack
py scripts/deploy_cloudformation.py deploy \
  --stack-name ure-mvp-stack \
  --kb-id 7XROZ6PZIF \
  --guardrail-id <your-guardrail-id> \
  --wait

# Get stack outputs
py scripts/deploy_cloudformation.py outputs --stack-name ure-mvp-stack
```

**What it creates:**
- ✓ KMS encryption key for all data
- ✓ S3 bucket with encryption and lifecycle policies
- ✓ DynamoDB tables (conversations, user-profiles, village-amenities) with encryption
- ✓ IAM role with least privilege permissions
- ✓ Lambda function with proper configuration
- ✓ API Gateway REST API
- ✓ CloudWatch log groups with encryption

**Stack Outputs:**
- API Gateway URL
- Lambda Function ARN
- S3 Bucket Name
- DynamoDB Table Names
- KMS Key ID
- IAM Role ARN

### Step 3: Upload Data to S3

Upload PlantVillage images, government schemes, and datasets.

```bash
# Upload all data
py scripts/ingest_data.py

# This uploads:
# - 70,295 PlantVillage images
# - 4 government scheme PDFs
# - Agmarknet CSV (87K records)
```

### Step 4: Deploy Lambda Function Code

Package and deploy the Lambda function with all dependencies.

```bash
# Deploy Lambda code
py scripts/deploy_lambda.py

# This will:
# 1. Package Lambda code with dependencies
# 2. Upload to S3
# 3. Update Lambda function
# 4. Configure environment variables
```

### Step 5: Start MCP Servers

Start the MCP servers for external data access.

```bash
# Start both MCP servers
py scripts/run_mcp_servers.py

# Or start individually:
# Agmarknet server (port 8001)
py src/mcp/servers/agmarknet_server.py

# Weather server (port 8002)
py src/mcp/servers/weather_server.py
```

### Step 6: Test Deployment

Test the complete deployment end-to-end.

```bash
# Test Lambda locally
py scripts/test_lambda_local.py

# Test API Gateway endpoint
curl -X POST https://<api-gateway-url>/dev/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_farmer_001",
    "query": "What are the symptoms of tomato late blight?",
    "language": "en"
  }'
```

### Step 7: Deploy Streamlit UI

Deploy the Streamlit web interface.

```bash
# Update API Gateway URL in .env
# API_GATEWAY_URL=https://<api-gateway-url>/dev/query

# Run Streamlit locally
py scripts/run_ui.py

# Or deploy to Streamlit Cloud:
# 1. Push code to GitHub
# 2. Connect Streamlit Cloud to repository
# 3. Configure environment variables
# 4. Deploy
```

## Security Features

### 1. KMS Encryption

All data encrypted at rest using AWS KMS:
- S3 bucket objects
- DynamoDB tables
- Lambda environment variables
- CloudWatch logs

### 2. IAM Least Privilege

Lambda execution role has minimal permissions:
- DynamoDB: GetItem, PutItem, Query, UpdateItem (specific tables only)
- S3: GetObject, PutObject (specific bucket only)
- Bedrock: InvokeModel, Retrieve, ApplyGuardrail (specific resources only)
- Translate: TranslateText, DetectDominantLanguage
- KMS: Decrypt, DescribeKey (specific key only)

### 3. Bedrock Guardrails

Content safety filtering:
- Input validation (blocks harmful queries)
- Output validation (blocks harmful responses)
- Topic filtering (politics, religion, finance)
- Word filtering (banned pesticides)
- PII anonymization

### 4. Data Privacy

- No PII in logs
- TTL on conversation data (auto-delete after 30 days)
- Encrypted data in transit (HTTPS)
- Encrypted data at rest (KMS)

## Multi-Language Support

Amazon Translate integration:
- Supports English, Hindi, Marathi
- Automatic language detection
- Fast translation (< 500ms)
- Fallback to English on error

**Usage:**
```json
{
  "user_id": "farmer123",
  "query": "टमाटर की बीमारी क्या है?",
  "language": "hi"
}
```

## Monitoring & Logging

### CloudWatch Logs

All logs encrypted and retained for 30 days:
- Lambda execution logs: `/aws/lambda/ure-mvp-handler`
- API Gateway logs: `/aws/apigateway/ure-mvp-api`

### CloudWatch Metrics

Track key metrics:
- Lambda invocations, errors, duration
- API Gateway requests, latency, errors
- DynamoDB read/write capacity
- S3 storage, requests

### CloudWatch Alarms

Set up alarms for:
- Lambda error rate > 5%
- API Gateway 5xx errors > 10
- Lambda duration > 30 seconds
- DynamoDB throttling

## Cost Estimation

Monthly costs (50-100 concurrent users):

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 100K invocations, 1GB, 30s avg | $5 |
| API Gateway | 100K requests | $0.35 |
| DynamoDB | On-demand, 1M reads, 500K writes | $1.50 |
| S3 | 100GB storage, 10K requests | $2.50 |
| Bedrock | 1M input tokens, 500K output | $30 |
| Translate | 1M characters | $15 |
| KMS | 10K requests | $1 |
| CloudWatch | Logs, metrics | $5 |
| **Total** | | **~$60/month** |

## Troubleshooting

### Lambda Timeout

If Lambda times out (> 300s):
1. Check CloudWatch logs for errors
2. Increase Lambda memory (more memory = faster CPU)
3. Optimize agent prompts
4. Enable response streaming

### Guardrails Blocking Legitimate Content

If guardrails block valid agricultural advice:
1. Check CloudWatch logs for block reason
2. Review guardrail configuration
3. Adjust topic/word policies
4. Test with sample queries

### Translation Errors

If translation fails:
1. Check IAM permissions for Translate
2. Verify language code (en, hi, mr)
3. Check CloudWatch logs for errors
4. Fallback to English on error

### MCP Server Connection Failed

If MCP tools fail:
1. Verify MCP servers are running
2. Check server URLs in environment variables
3. Test server health endpoints
4. Review MCP Client logs

## Rollback Procedure

If deployment fails:

```bash
# Rollback CloudFormation stack
aws cloudformation rollback-stack --stack-name ure-mvp-stack

# Or delete and redeploy
py scripts/deploy_cloudformation.py delete --stack-name ure-mvp-stack --wait
```

## Production Checklist

Before going to production:

- [ ] Bedrock Guardrails created and tested
- [ ] CloudFormation stack deployed successfully
- [ ] All data uploaded to S3
- [ ] Lambda function deployed and tested
- [ ] MCP servers running and accessible
- [ ] API Gateway endpoint tested
- [ ] Streamlit UI deployed
- [ ] CloudWatch alarms configured
- [ ] IAM permissions reviewed
- [ ] KMS encryption verified
- [ ] Guardrails tested with 100+ samples
- [ ] Translation tested for all languages
- [ ] Load testing completed (50-100 concurrent users)
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Backup and disaster recovery plan in place

## Support

For issues or questions:
- Check CloudWatch logs first
- Review this deployment guide
- Contact: [your-email@example.com]

---

**Last Updated**: 2026-02-28
**Version**: 1.0.0
