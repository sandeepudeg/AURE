# Deploy to Mumbai + Singapore for Optimal India Performance

## Overview

This deployment strategy provides the best performance for users in India:

- **Lambda + API Gateway** → Mumbai (ap-south-1) - 50-100ms latency
- **Streamlit UI** → Singapore (ap-southeast-1) - 2-3 second load time
- **DynamoDB + S3** → Mumbai (ap-south-1) - Fast data access

## Why This Configuration?

### Mumbai (ap-south-1)
- ✅ Lambda available
- ✅ API Gateway available
- ✅ DynamoDB available
- ✅ S3 available
- ❌ App Runner NOT available

### Singapore (ap-southeast-1)
- ✅ App Runner available
- ✅ Closest App Runner region to India (~3,500 km vs 12,000 km for US East)
- ✅ 80% faster than US East deployment

## Performance Comparison

| Metric | US East (Current) | Mumbai + Singapore | Improvement |
|--------|-------------------|-------------------|-------------|
| API Latency | 200-300ms | 50-100ms | 66% faster |
| UI Load Time | 10+ minutes | 2-3 seconds | 99% faster |
| Data Access | 200-300ms | 50-100ms | 66% faster |

## Deployment Steps

### Step 1: Deploy Lambda to Mumbai

This will create:
- Lambda function in ap-south-1
- API Gateway in ap-south-1
- DynamoDB tables in ap-south-1
- S3 bucket in ap-south-1

```powershell
py scripts/deploy_mumbai_lambda.py
```

**Expected Output:**
- Lambda Function ARN
- API Gateway endpoint (save this for Step 2)
- S3 bucket name
- DynamoDB table names

The API endpoint will be saved to `MUMBAI_ENDPOINT.txt`

### Step 2: Deploy Streamlit to Singapore

First, set the Mumbai API endpoint:

```powershell
# Read the endpoint from the file
$MUMBAI_API = Get-Content MUMBAI_ENDPOINT.txt
$env:MUMBAI_API_ENDPOINT = $MUMBAI_API

# Deploy to Singapore
py scripts/deploy_singapore_streamlit.py
```

**Expected Output:**
- ECR repository in Singapore
- Docker image pushed
- App Runner service URL

The service URL will be saved to `SINGAPORE_URL.txt`

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User in India                        │
└─────────────────────────────────────────────────────────┘
                          │
                          │ 50-100ms latency
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Streamlit UI (Singapore - ap-southeast-1)       │
│                  App Runner Service                      │
└─────────────────────────────────────────────────────────┘
                          │
                          │ API calls
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Lambda + API Gateway (Mumbai - ap-south-1)      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Lambda     │  │  DynamoDB    │  │   S3 Bucket  │ │
│  │   Function   │  │   Tables     │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Bedrock API calls
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Amazon Bedrock (us-east-1)                 │
│                  Nova Pro Model                          │
└─────────────────────────────────────────────────────────┘
```

## Cost Estimate

### Mumbai Resources (ap-south-1)
- Lambda: $6-12/month (20% more than US East)
- API Gateway: $3-5/month
- DynamoDB: $5-10/month (on-demand)
- S3: $2-5/month
- **Subtotal: $16-32/month**

### Singapore Resources (ap-southeast-1)
- App Runner: $18-30/month (20% more than US East)
- ECR: $1-2/month
- **Subtotal: $19-32/month**

### Total: $35-64/month
- ~20% more expensive than US East
- But 99% faster for Indian users!

## Testing the Deployment

### Test Mumbai API

```powershell
# Read the endpoint
$MUMBAI_API = Get-Content MUMBAI_ENDPOINT.txt

# Test the API
curl -X POST $MUMBAI_API `
  -H "Content-Type: application/json" `
  -d '{"user_id":"test","query":"What crops grow well in Maharashtra?"}'
```

### Test Singapore Streamlit

```powershell
# Read the URL
$SINGAPORE_URL = Get-Content SINGAPORE_URL.txt

# Open in browser
Start-Process $SINGAPORE_URL
```

## Monitoring

### Check Lambda Logs (Mumbai)
```powershell
aws logs tail /aws/lambda/ure-mvp-handler-mumbai --region ap-south-1 --follow
```

### Check App Runner Status (Singapore)
```powershell
aws apprunner describe-service `
  --service-arn <service-arn> `
  --region ap-southeast-1
```

## Rollback Plan

If you need to rollback to US East deployment:

1. Update Streamlit environment variable to use US East API
2. Keep both deployments running
3. Switch DNS or update links

## Next Steps

After deployment:

1. ✅ Test API from Mumbai
2. ✅ Test Streamlit from Singapore
3. ✅ Verify end-to-end flow
4. ✅ Monitor performance metrics
5. ✅ Update documentation with new endpoints

## Troubleshooting

### Lambda Deployment Issues
- Check IAM role permissions
- Verify layer is uploaded correctly
- Check CloudWatch logs

### App Runner Issues
- Verify ECR image exists
- Check IAM role for ECR access
- Verify health check endpoint

### API Connection Issues
- Verify API Gateway endpoint is correct
- Check CORS settings
- Verify Lambda permissions

## Support

For issues or questions:
1. Check CloudWatch logs
2. Verify all resources are in correct regions
3. Test each component independently
4. Check AWS service health dashboard
