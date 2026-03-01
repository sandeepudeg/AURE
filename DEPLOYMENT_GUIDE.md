# URE MVP Deployment Guide

## Overview
This guide covers deploying the URE (Unified Rural Ecosystem) MVP to AWS.

## Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.11 installed
- All dependencies installed (`pip install -r requirements.txt`)

## Architecture
```
User → API Gateway → Lambda → Bedrock/DynamoDB/S3
                            ↓
                    Supervisor Agent
                    ↓     ↓     ↓
            Agri-Expert  Policy  Resource
                         Navigator Optimizer
```

## Deployment Steps

### 1. Verify Local Setup
```bash
# Test Lambda handler locally
py scripts/test_lambda_local.py

# Test end-to-end system
py tests/test_end_to_end.py
```

### 2. Deploy Lambda Function
```bash
# Automated deployment (recommended)
py scripts/deploy_lambda.py
```

This script will:
- Create IAM role with necessary permissions
- Package Lambda deployment zip
- Deploy/update Lambda function
- Create API Gateway REST API
- Configure Lambda integration

### 3. Manual Deployment (Alternative)

#### Step 3.1: Create IAM Role
```bash
aws iam create-role \
  --role-name ure-lambda-execution-role \
  --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy \
  --role-name ure-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name ure-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name ure-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name ure-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

#### Step 3.2: Create Deployment Package
```bash
# Create package directory
mkdir lambda_package
cd lambda_package

# Copy source code
cp -r ../src/* .

# Install dependencies
pip install -r ../requirements-lambda.txt -t .

# Create zip
zip -r ../lambda_deployment.zip .
cd ..
```

#### Step 3.3: Deploy Lambda
```bash
aws lambda create-function \
  --function-name ure-mvp-handler \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/ure-lambda-execution-role \
  --handler aws.lambda_handler.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{
    DYNAMODB_TABLE_NAME=ure-conversations,
    DYNAMODB_USER_TABLE=ure-user-profiles,
    S3_BUCKET_NAME=ure-mvp-data-us-east-1-ACCOUNT_ID,
    BEDROCK_KB_ID=YOUR_KB_ID,
    BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0,
    BEDROCK_REGION=us-east-1
  }"
```

#### Step 3.4: Create API Gateway
```bash
# Create REST API
aws apigateway create-rest-api \
  --name ure-mvp-api \
  --description "API for URE MVP"

# Get API ID and Root Resource ID
API_ID=<from previous command>
ROOT_ID=<from get-resources command>

# Create /query resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part query

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Set Lambda integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:ACCOUNT_ID:function:ure-mvp-handler/invocations

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

### 4. Test Deployment
```bash
# Test API endpoint
curl -X POST https://API_ID.execute-api.us-east-1.amazonaws.com/prod/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_farmer",
    "query": "What are the symptoms of tomato blight?",
    "language": "en"
  }'
```

### 5. Deploy Streamlit UI

#### Option A: Local Deployment
```bash
# Run Streamlit locally
py -m streamlit run src/ui/app.py --server.port=8501
```

#### Option B: EC2 Deployment
```bash
# SSH to EC2 instance
ssh -i your-key.pem ec2-user@your-instance

# Install dependencies
sudo yum install python3.11 git -y
git clone your-repo
cd your-repo
pip3.11 install -r requirements.txt

# Run Streamlit with systemd
sudo systemctl start ure-streamlit
```

#### Option C: ECS/Fargate Deployment
See `docker/Dockerfile` for containerized deployment.

### 6. Deploy MCP Servers

#### Option A: EC2 Deployment
```bash
# Start MCP servers on EC2
nohup py src/mcp/servers/agmarknet_server.py > agmarknet.log 2>&1 &
nohup py src/mcp/servers/weather_server.py > weather.log 2>&1 &
```

#### Option B: ECS/Fargate Deployment
Deploy as separate containers with load balancer.

## Environment Variables

### Lambda Function
- `DYNAMODB_TABLE_NAME`: ure-conversations
- `DYNAMODB_USER_TABLE`: ure-user-profiles
- `DYNAMODB_VILLAGE_TABLE`: ure-village-amenities
- `S3_BUCKET_NAME`: ure-mvp-data-us-east-1-{account_id}
- `BEDROCK_KB_ID`: Your Knowledge Base ID
- `BEDROCK_MODEL_ID`: us.amazon.nova-pro-v1:0
- `BEDROCK_REGION`: us-east-1
- `LOG_LEVEL`: INFO

### Streamlit UI
- All Lambda variables plus:
- `API_GATEWAY_URL`: Your API Gateway endpoint
- `STREAMLIT_SERVER_PORT`: 8501

### MCP Servers
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key

## Monitoring

### CloudWatch Logs
```bash
# View Lambda logs
aws logs tail /aws/lambda/ure-mvp-handler --follow

# View specific log stream
aws logs get-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --log-stream-name 2024/01/01/[$LATEST]abc123
```

### CloudWatch Metrics
- Lambda invocations
- Lambda errors
- Lambda duration
- API Gateway 4xx/5xx errors
- DynamoDB read/write capacity

## Cost Optimization

### Lambda
- Use provisioned concurrency for consistent performance
- Optimize memory allocation (current: 512MB)
- Set appropriate timeout (current: 300s)

### Bedrock
- Use inference profiles for cost savings
- Cache responses when possible
- Monitor token usage

### DynamoDB
- Use on-demand billing for variable workload
- Enable point-in-time recovery for production

### S3
- Use S3 Intelligent-Tiering for images
- Enable lifecycle policies for old data

## Security

### IAM Roles
- Follow principle of least privilege
- Use separate roles for dev/prod
- Enable MFA for sensitive operations

### API Gateway
- Add API key authentication
- Enable throttling (rate limiting)
- Use WAF for DDoS protection

### Data Encryption
- Enable encryption at rest for DynamoDB
- Use S3 bucket encryption
- Enable HTTPS only for API Gateway

## Troubleshooting

### Lambda Timeout
- Increase timeout in Lambda configuration
- Optimize agent response time
- Use async processing for long operations

### Memory Issues
- Increase Lambda memory allocation
- Optimize dependency size
- Use Lambda Layers for large libraries

### API Gateway 502 Errors
- Check Lambda execution role permissions
- Verify Lambda function is not timing out
- Check CloudWatch logs for errors

## Rollback

### Lambda Function
```bash
# List versions
aws lambda list-versions-by-function --function-name ure-mvp-handler

# Rollback to previous version
aws lambda update-alias \
  --function-name ure-mvp-handler \
  --name prod \
  --function-version PREVIOUS_VERSION
```

### API Gateway
```bash
# List deployments
aws apigateway get-deployments --rest-api-id $API_ID

# Rollback to previous deployment
aws apigateway update-stage \
  --rest-api-id $API_ID \
  --stage-name prod \
  --patch-operations op=replace,path=/deploymentId,value=PREVIOUS_DEPLOYMENT_ID
```

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review this deployment guide
3. Contact the development team
