# AWS Setup Summary - URE MVP

## ✅ Successfully Completed

### 1. S3 Data Storage
- **Bucket**: `ure-mvp-data-188238313375`
- **Region**: `ap-south-1` (Mumbai)
- **Versioning**: Enabled
- **Contents**:
  - PlantVillage dataset: 87,900 images (2GB+)
  - Government scheme PDFs: 4 files
    - PM-Kisan Registration Form
    - PMFBY Scheme Guidelines
    - PKVY Organic Farming Guidelines
    - PMKSY Irrigation Manual
    - eNAM Stakeholder Guideline
  - Agmarknet market prices CSV

### 2. DynamoDB Tables
All tables created in `ap-south-1` region with PAY_PER_REQUEST billing:

#### `ure-conversations`
- **Purpose**: Store multi-turn chat history
- **Key**: user_id (HASH)
- **Status**: Created, empty

#### `ure-village-amenities`
- **Purpose**: Regional infrastructure data
- **Keys**: village_name (HASH), district (RANGE)
- **Status**: Created with 3 sample villages
  - Nashik (district center)
  - Pimpalgaon (12km from town)
  - Satana (25km from town)

#### `ure-user-profiles`
- **Purpose**: Farmer profile data
- **Key**: user_id (HASH)
- **Status**: Created with 1 sample user
  - farmer_12345 (Rajesh Kumar)
  - 5 acres, wheat & cotton crops

### 3. OpenSearch Serverless
- **Collection**: `ure-knowledge-base`
- **ARN**: `arn:aws:aoss:us-east-1:188238313375:collection/q4hpsg5m4hm0fryx7dv6`
- **Region**: `us-east-1`
- **Type**: VECTORSEARCH
- **Security Policies**: Configured
  - Encryption policy: `ure-knowledge-base-encryption`
  - Network policy: `ure-knowledge-base-network`
  - Data access policy: `ure-knowledge-base-data`

### 4. IAM Roles
- **BedrockKnowledgeBaseRole**: Created with policies for:
  - S3 access to `ure-mvp-data-188238313375`
  - Bedrock model invocation
  - OpenSearch Serverless access

## ⚠️ Pending Manual Setup

### Bedrock Knowledge Base
The Knowledge Base creation requires manual setup through AWS Console due to complex IAM permissions and OpenSearch integration.

**Why Manual Setup is Needed:**
1. OpenSearch Serverless data access policies require precise timing
2. IAM role propagation can take several minutes
3. Bedrock service needs explicit permissions to access OpenSearch
4. Vector index must be created with specific field mappings

**Follow the guide**: `BEDROCK_KB_MANUAL_SETUP.md`

**Estimated Time**: 10-15 minutes

## 📊 Resource Summary

| Resource Type | Name | Region | Status |
|--------------|------|--------|--------|
| S3 Bucket | ure-mvp-data-188238313375 | ap-south-1 | ✅ Active |
| DynamoDB Table | ure-conversations | ap-south-1 | ✅ Active |
| DynamoDB Table | ure-village-amenities | ap-south-1 | ✅ Active (3 items) |
| DynamoDB Table | ure-user-profiles | ap-south-1 | ✅ Active (1 item) |
| OpenSearch Collection | ure-knowledge-base | us-east-1 | ✅ Active |
| IAM Role | BedrockKnowledgeBaseRole | Global | ✅ Created |
| Bedrock KB | ure-pm-kisan-kb | us-east-1 | ⚠️ Pending |

## 💰 Cost Estimate (Monthly)

### Current Setup
- **S3**: ~$0.50 (2GB storage + minimal requests)
- **DynamoDB**: ~$0.00 (free tier covers 25GB + 25 WCU/RCU)
- **OpenSearch Serverless**: ~$0.00 (collection exists but no data indexed yet)
- **Total**: ~$0.50/month

### After Bedrock KB Setup
- **Bedrock KB**: ~$0.00 (free tier: 10,000 queries/month)
- **OpenSearch Serverless**: ~$700/month (OCU-based pricing)
  - Note: This is the most expensive component
  - Consider using Amazon Kendra or RDS Postgres with pgvector for cost optimization
- **Total**: ~$700/month

## 🚀 Next Steps

1. **Complete Bedrock KB Setup** (Optional for testing)
   - Follow `BEDROCK_KB_MANUAL_SETUP.md`
   - Update `.env` with Knowledge Base ID

2. **Test Agents Without KB**
   ```bash
   py test_agents.py
   ```
   - Agri-Expert: Will work (uses direct API calls)
   - Resource-Optimizer: Will work (uses weather API)
   - Policy-Navigator: Limited functionality (needs KB for scheme info)

3. **Set Up MCP Servers** (For live data)
   - Agmarknet MCP server
   - Weather MCP server

4. **Run Streamlit UI**
   ```bash
   streamlit run src/ui/app.py
   ```

## 🔧 Configuration Files

### `.env`
All AWS resource names and configurations are stored in `.env`:
- S3 bucket name
- DynamoDB table names
- OpenSearch collection ARN
- Bedrock model IDs
- MCP server URLs

### AWS Credentials
Loaded from `~/.aws/credentials`:
- Account ID: 188238313375
- Region: ap-south-1 (primary), us-east-1 (Bedrock)

## 📝 Notes

1. **Region Strategy**:
   - Data storage (S3, DynamoDB): `ap-south-1` (Mumbai) for low latency
   - Bedrock services: `us-east-1` (Virginia) for model availability

2. **Cost Optimization**:
   - OpenSearch Serverless is expensive for small workloads
   - Consider alternatives:
     - Amazon Kendra (managed search)
     - RDS Postgres with pgvector extension
     - Amazon MemoryDB for Redis with vector search

3. **Security**:
   - All resources use IAM roles and policies
   - S3 bucket has versioning enabled
   - OpenSearch collection has encryption at rest

4. **Scalability**:
   - DynamoDB: Auto-scaling with PAY_PER_REQUEST
   - S3: Unlimited storage
   - OpenSearch: Can scale OCUs as needed

## 🐛 Troubleshooting

### Issue: Bedrock KB Creation Fails
**Solution**: Follow manual setup guide. The automated script has IAM timing issues.

### Issue: OpenSearch Collection Not Found
**Solution**: Ensure you're in `us-east-1` region. Collection takes 2-3 minutes to become active.

### Issue: S3 Access Denied
**Solution**: Check IAM role has correct bucket permissions. Verify bucket name in `.env`.

### Issue: DynamoDB Table Not Found
**Solution**: Verify region is `ap-south-1`. Check table names in `.env`.

## 📚 Reference Documentation

- [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
