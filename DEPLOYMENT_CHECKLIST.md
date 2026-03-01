# URE MVP - Production Deployment Checklist

**Date**: February 28, 2026  
**Target Environment**: AWS Production (us-east-1)

---

## Pre-Deployment Checklist

### 1. AWS Account Setup
- [ ] AWS Account ID verified: 188238313375
- [ ] AWS CLI configured with credentials
- [ ] IAM user has necessary permissions:
  - CloudFormation full access
  - Lambda full access
  - API Gateway full access
  - DynamoDB full access
  - S3 full access
  - Bedrock full access
  - KMS full access
  - CloudWatch full access
  - IAM role creation

### 2. Environment Variables
- [ ] `.env` file configured with all required variables
- [ ] BEDROCK_KB_ID set: 7XROZ6PZIF
- [ ] BEDROCK_GUARDRAIL_ID set: q6wfsifs9d72
- [ ] BEDROCK_MODEL_ID set: us.amazon.nova-pro-v1:0
- [ ] OPENWEATHER_API_KEY set: 4f744a31ea3afc09cb4391ad37be26c7
- [ ] AWS_REGION set: us-east-1

### 3. Code Readiness
- [ ] All tests passing (31/31 local tests)
- [ ] No syntax errors in code
- [ ] All dependencies listed in requirements.txt
- [ ] Lambda handler tested locally
- [ ] MCP Client tested
- [ ] Agents tested

### 4. Infrastructure Files
- [ ] CloudFormation template validated
- [ ] Deployment scripts tested
- [ ] All configuration files present

---

## Deployment Steps

### Step 1: Create Bedrock Guardrails (if not exists)

```bash
# Check if guardrail exists
aws bedrock get-guardrail \
  --guardrail-identifier q6wfsifs9d72 \
  --region us-east-1

# If not exists, create it
py scripts/create_bedrock_guardrails.py create
```

**Verification**:
- [ ] Guardrail ID obtained
- [ ] Guardrail tested with sample queries
- [ ] Guardrail ID added to .env

---

### Step 2: Deploy CloudFormation Stack

```bash
# Option 1: Using automated script (RECOMMENDED)
py scripts/deploy_production.py \
  --stack-name ure-mvp-stack \
  --region us-east-1 \
  --alarm-email your-email@example.com

# Option 2: Using deploy_cloudformation.py
py scripts/deploy_cloudformation.py deploy \
  --stack-name ure-mvp-stack \
  --kb-id 7XROZ6PZIF \
  --guardrail-id q6wfsifs9d72 \
  --wait
```

**Verification**:
- [ ] Stack status: CREATE_COMPLETE or UPDATE_COMPLETE
- [ ] All resources created successfully
- [ ] No errors in CloudWatch logs
- [ ] Stack outputs available

**Expected Resources**:
- [ ] KMS encryption key
- [ ] S3 bucket
- [ ] DynamoDB tables (3)
- [ ] IAM role
- [ ] Lambda function
- [ ] API Gateway
- [ ] CloudWatch log groups
- [ ] CloudWatch alarms (7)
- [ ] CloudWatch dashboard
- [ ] SNS topic (if email provided)

---

### Step 3: Get Stack Outputs

```bash
# Get all stack outputs
py scripts/deploy_cloudformation.py outputs --stack-name ure-mvp-stack

# Or using AWS CLI
aws cloudformation describe-stacks \
  --stack-name ure-mvp-stack \
  --query 'Stacks[0].Outputs' \
  --output table
```

**Save These Values**:
- [ ] API Gateway URL: ___________________________
- [ ] Lambda Function ARN: ___________________________
- [ ] S3 Bucket Name: ___________________________
- [ ] DynamoDB Table Names: ___________________________
- [ ] KMS Key ID: ___________________________

---

### Step 4: Deploy Lambda Function Code

```bash
# Deploy Lambda code
py scripts/deploy_lambda.py

# Or use production script
py scripts/deploy_production.py --skip-test
```

**Verification**:
- [ ] Lambda code uploaded successfully
- [ ] Lambda function updated
- [ ] Environment variables configured
- [ ] No errors in deployment

---

### Step 5: Upload Data to S3

```bash
# Upload PlantVillage images, government schemes, datasets
py scripts/ingest_data.py
```

**Verification**:
- [ ] PlantVillage images uploaded (70,295 images)
- [ ] Government scheme PDFs uploaded (4 files)
- [ ] Agmarknet CSV uploaded (87K records)
- [ ] S3 bucket structure correct

---

### Step 6: Test API Gateway Endpoint

```bash
# Test with curl
curl -X POST <API_GATEWAY_URL> \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_farmer_001",
    "query": "What are the symptoms of tomato late blight?",
    "language": "en"
  }'

# Or use Python script
py scripts/test_api_endpoint.py --url <API_GATEWAY_URL>
```

**Verification**:
- [ ] API returns 200 status code
- [ ] Response contains expected fields
- [ ] Response time < 5 seconds
- [ ] No errors in CloudWatch logs

---

### Step 7: Start MCP Servers

```bash
# Start Agmarknet server (port 8001)
py src/mcp/servers/agmarknet_server.py &

# Start Weather server (port 8002)
py src/mcp/servers/weather_server.py &

# Or use combined script
py scripts/run_mcp_servers.py
```

**Verification**:
- [ ] Agmarknet server running on port 8001
- [ ] Weather server running on port 8002
- [ ] Health check endpoints responding
- [ ] MCP tools accessible from Lambda

---

### Step 8: Deploy Streamlit UI

```bash
# Update .env with API Gateway URL
# API_GATEWAY_URL=<your-api-gateway-url>

# Run Streamlit locally for testing
py -m streamlit run src/ui/app.py

# Or deploy to Streamlit Cloud
# 1. Push code to GitHub
# 2. Connect Streamlit Cloud to repository
# 3. Configure environment variables
# 4. Deploy
```

**Verification**:
- [ ] Streamlit app accessible
- [ ] UI loads without errors
- [ ] Can submit queries
- [ ] Receives responses from API
- [ ] Image upload works
- [ ] Language toggle works

---

### Step 9: Configure CloudWatch Alarms

```bash
# Alarms are automatically created by CloudFormation
# Verify they are active

aws cloudwatch describe-alarms \
  --alarm-name-prefix ure-mvp \
  --region us-east-1
```

**Verification**:
- [ ] Lambda error alarm active
- [ ] Lambda duration alarm active
- [ ] Lambda throttle alarm active
- [ ] API Gateway 5xx alarm active
- [ ] API Gateway 4xx alarm active
- [ ] API Gateway latency alarm active
- [ ] DynamoDB throttle alarm active
- [ ] SNS topic subscribed (if email provided)

---

### Step 10: Verify CloudWatch Dashboard

```bash
# Open CloudWatch dashboard in AWS Console
# Dashboard name: ure-mvp-dashboard
```

**Verification**:
- [ ] Dashboard displays all widgets
- [ ] Lambda invocations visible
- [ ] Lambda errors visible
- [ ] Lambda duration visible
- [ ] API Gateway requests visible
- [ ] API Gateway errors visible
- [ ] API Gateway latency visible
- [ ] DynamoDB capacity visible
- [ ] Recent Lambda errors log visible

---

## Post-Deployment Verification

### 1. Functional Testing

```bash
# Run end-to-end tests
py -m pytest tests/test_end_to_end.py -v

# Test all agent types
py scripts/test_all_agents.py
```

**Test Cases**:
- [ ] Disease identification query
- [ ] Market price query
- [ ] PM-Kisan eligibility query
- [ ] Irrigation recommendation query
- [ ] Image upload and analysis
- [ ] Multi-language support (Hindi, Marathi)
- [ ] Conversation history
- [ ] Guardrails blocking harmful content

### 2. Performance Testing

```bash
# Run performance tests
py -m pytest tests/test_performance.py -v -m "not slow"
```

**Metrics to Verify**:
- [ ] Response time < 5 seconds (95th percentile)
- [ ] Throughput ≥ 10 requests/second
- [ ] 50 concurrent users supported
- [ ] Success rate ≥ 95%

### 3. Security Verification

```bash
# Run security tests
py -m pytest tests/test_security.py -v
```

**Security Checks**:
- [ ] All data encrypted at rest (KMS)
- [ ] All data encrypted in transit (HTTPS)
- [ ] No PII in CloudWatch logs
- [ ] IAM roles have least privilege
- [ ] Guardrails blocking harmful content
- [ ] API Gateway using HTTPS only

### 4. Monitoring Verification

**Check CloudWatch Metrics**:
- [ ] Lambda invocations increasing
- [ ] No Lambda errors
- [ ] Lambda duration acceptable
- [ ] API Gateway requests increasing
- [ ] No API Gateway 5xx errors
- [ ] DynamoDB capacity sufficient

---

## Rollback Plan

If deployment fails or issues are found:

### Option 1: Rollback CloudFormation Stack

```bash
# Rollback to previous version
aws cloudformation rollback-stack --stack-name ure-mvp-stack

# Or delete and redeploy
py scripts/deploy_cloudformation.py delete --stack-name ure-mvp-stack --wait
```

### Option 2: Rollback Lambda Function

```bash
# List Lambda versions
aws lambda list-versions-by-function --function-name ure-mvp-handler

# Rollback to previous version
aws lambda update-alias \
  --function-name ure-mvp-handler \
  --name PROD \
  --function-version <previous-version>
```

---

## Troubleshooting

### Issue: CloudFormation Stack Fails

**Check**:
- CloudFormation events in AWS Console
- IAM permissions
- Parameter values
- Template syntax

**Solution**:
- Fix the issue
- Delete the stack
- Redeploy

### Issue: Lambda Function Timeout

**Check**:
- CloudWatch logs for errors
- Lambda memory allocation
- Agent response time

**Solution**:
- Increase Lambda timeout (current: 300s)
- Increase Lambda memory (current: 1024MB)
- Optimize agent prompts

### Issue: API Gateway 502 Errors

**Check**:
- Lambda execution role permissions
- Lambda function not timing out
- CloudWatch logs for errors

**Solution**:
- Verify IAM permissions
- Check Lambda logs
- Test Lambda function directly

### Issue: MCP Tools Not Working

**Check**:
- MCP servers running
- Server URLs in environment variables
- Network connectivity

**Solution**:
- Start MCP servers
- Verify server URLs
- Check firewall rules

---

## Success Criteria

### Deployment Success
- [ ] All CloudFormation resources created
- [ ] Lambda function deployed and working
- [ ] API Gateway endpoint accessible
- [ ] MCP servers running
- [ ] Streamlit UI deployed
- [ ] CloudWatch alarms configured
- [ ] CloudWatch dashboard visible

### Functional Success
- [ ] All test cases passing
- [ ] All agent types working
- [ ] Image upload working
- [ ] Multi-language support working
- [ ] Guardrails working
- [ ] Conversation history working

### Performance Success
- [ ] Response time < 5 seconds
- [ ] Throughput ≥ 10 req/s
- [ ] 50+ concurrent users supported
- [ ] Success rate ≥ 95%

### Security Success
- [ ] All data encrypted
- [ ] No PII in logs
- [ ] IAM least privilege
- [ ] Guardrails active
- [ ] HTTPS only

---

## Next Steps After Deployment

1. **Monitor for 24 hours**
   - Check CloudWatch dashboard
   - Review CloudWatch logs
   - Monitor alarms

2. **Start Farmer Onboarding**
   - Create onboarding process
   - Prepare training materials
   - Identify 50+ farmers

3. **Set Up Feedback Collection**
   - Create feedback form
   - Set up weekly surveys
   - Analyze feedback

4. **Begin 2-Week Pilot**
   - Monitor daily usage
   - Collect farmer feedback
   - Iterate based on feedback

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Stack Name**: ure-mvp-stack  
**Region**: us-east-1  
**Status**: ⏳ Pending / ✅ Complete / ❌ Failed

---

**Last Updated**: February 28, 2026
