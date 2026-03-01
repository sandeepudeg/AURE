# URE MVP - Comprehensive Troubleshooting Guide

**Version**: 1.0.0  
**Last Updated**: February 28, 2026

---

## Table of Contents

1. [User-Facing Issues](#user-facing-issues)
2. [API Issues](#api-issues)
3. [Lambda Function Issues](#lambda-function-issues)
4. [MCP Server Issues](#mcp-server-issues)
5. [Database Issues](#database-issues)
6. [Security & Guardrails Issues](#security--guardrails-issues)
7. [Performance Issues](#performance-issues)
8. [Deployment Issues](#deployment-issues)

---

## User-Facing Issues

### Issue 1: "Content Blocked by Safety Filters"

**Symptoms**:
- User receives message: "Your query contains harmful or off-topic content"
- Query is not processed

**Causes**:
1. Query contains banned pesticides (DDT, Endosulfan, Monocrotophos)
2. Query contains off-topic content (politics, religion, finance)
3. Query contains violence, hate speech, or misconduct
4. Query contains PII (email, phone, address)

**Solutions**:

```bash
# Check CloudWatch logs for guardrail blocks
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "GUARDRAIL_BLOCKED" \
  --start-time $(date -d '1 hour ago' +%s)000

# Review blocked content
# Look for: "Guardrail blocked input" or "Guardrail blocked output"
```

**User Actions**:
1. Rephrase the question
2. Focus on agricultural topics only
3. Avoid banned substances
4. Remove personal information

**Admin Actions**:
1. Review guardrail configuration
2. Adjust topic/word policies if too restrictive
3. Add legitimate terms to allow list

---

### Issue 2: "Image Upload Failed"

**Symptoms**:
- Image upload button doesn't work
- Error message: "Failed to upload image"
- Image doesn't appear after upload

**Causes**:
1. Image file too large (> 5MB)
2. Wrong file format (not JPG/PNG)
3. S3 bucket permissions issue
4. Network connectivity problem

**Solutions**:

```bash
# Check S3 bucket permissions
aws s3api get-bucket-policy \
  --bucket ure-mvp-data-us-east-1-188238313375

# Test S3 upload
aws s3 cp test-image.jpg \
  s3://ure-mvp-data-us-east-1-188238313375/uploads/test.jpg

# Check CloudWatch logs for S3 errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "S3" \
  --start-time $(date -d '1 hour ago' +%s)000
```

**User Actions**:
1. Compress image to < 5MB
2. Convert to JPG or PNG format
3. Check internet connection
4. Try a different image

**Admin Actions**:
1. Verify S3 bucket policy allows uploads
2. Check Lambda IAM role has S3 PutObject permission
3. Increase Lambda timeout if needed
4. Check S3 bucket storage limits

---

### Issue 3: "Query Timed Out"

**Symptoms**:
- User waits > 30 seconds
- Error message: "Request timed out"
- No response received

**Causes**:
1. Lambda function timeout (300s limit)
2. Bedrock API slow response
3. MCP server not responding
4. Complex query requiring multiple agent calls

**Solutions**:

```bash
# Check Lambda duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=ure-mvp-handler \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average,Maximum

# Check for timeout errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "Task timed out" \
  --start-time $(date -d '1 hour ago' +%s)000
```

**User Actions**:
1. Simplify the question
2. Ask one question at a time
3. Try again in a few minutes
4. Avoid uploading very large images

**Admin Actions**:
1. Increase Lambda timeout (current: 300s)
2. Increase Lambda memory (more memory = faster CPU)
3. Optimize agent prompts
4. Enable response streaming
5. Add caching for common queries

---

### Issue 4: "Translation Unavailable"

**Symptoms**:
- Response in English despite selecting Hindi/Marathi
- Error message: "Translation service unavailable"

**Causes**:
1. Amazon Translate service down
2. IAM permissions missing
3. Invalid language code
4. Translation API quota exceeded

**Solutions**:

```bash
# Check Translate service status
aws translate translate-text \
  --text "Test" \
  --source-language-code en \
  --target-language-code hi \
  --region us-east-1

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::188238313375:role/ure-mvp-lambda-role \
  --action-names translate:TranslateText \
  --resource-arns "*"

# Check CloudWatch logs for translation errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "Translation" \
  --start-time $(date -d '1 hour ago' +%s)000
```

**User Actions**:
1. Response will be in English (fallback)
2. Try again later
3. Change language preference and save

**Admin Actions**:
1. Verify IAM role has Translate permissions
2. Check Translate API quotas
3. Verify language codes (en, hi, mr)
4. Check CloudWatch logs for errors
5. Implement retry logic with exponential backoff

---

## API Issues

### Issue 5: "API Gateway 502 Bad Gateway"

**Symptoms**:
- HTTP 502 error
- Message: "Internal server error"
- API Gateway returns error immediately

**Causes**:
1. Lambda function not responding
2. Lambda execution role permissions missing
3. Lambda function crashed
4. API Gateway integration misconfigured

**Solutions**:

```bash
# Check Lambda function status
aws lambda get-function \
  --function-name ure-mvp-handler

# Test Lambda directly
aws lambda invoke \
  --function-name ure-mvp-handler \
  --payload '{"user_id":"test","query":"test","language":"en"}' \
  response.json

# Check API Gateway integration
aws apigateway get-integration \
  --rest-api-id <api-id> \
  --resource-id <resource-id> \
  --http-method POST

# Check CloudWatch logs
aws logs tail /aws/lambda/ure-mvp-handler --follow
```

**Solutions**:
1. Verify Lambda function is active
2. Check Lambda execution role permissions
3. Test Lambda function directly
4. Review CloudWatch logs for errors
5. Verify API Gateway integration settings

---

### Issue 6: "API Gateway 429 Too Many Requests"

**Symptoms**:
- HTTP 429 error
- Message: "Rate limit exceeded"
- Requests blocked temporarily

**Causes**:
1. API Gateway throttling limits reached
2. Too many requests from single IP
3. DDoS attack or abuse

**Solutions**:

```bash
# Check API Gateway throttling settings
aws apigateway get-stage \
  --rest-api-id <api-id> \
  --stage-name dev

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=ure-mvp-api \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 60 \
  --statistics Sum
```

**Solutions**:
1. Increase API Gateway throttling limits
2. Implement API key authentication
3. Add WAF rules to block abusive IPs
4. Use CloudFront for caching
5. Implement request queuing

---

## Lambda Function Issues

### Issue 7: "Lambda Out of Memory"

**Symptoms**:
- Error: "Runtime exited with error: signal: killed"
- Lambda function crashes
- Incomplete responses

**Causes**:
1. Memory limit too low (current: 1024MB)
2. Memory leak in code
3. Large image processing
4. Too many concurrent requests

**Solutions**:

```bash
# Check memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name MemoryUtilization \
  --dimensions Name=FunctionName,Value=ure-mvp-handler \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average,Maximum

# Increase Lambda memory
aws lambda update-function-configuration \
  --function-name ure-mvp-handler \
  --memory-size 2048
```

**Solutions**:
1. Increase Lambda memory (1024MB → 2048MB)
2. Optimize image processing
3. Use Lambda layers for dependencies
4. Implement streaming responses
5. Profile code for memory leaks

---

### Issue 8: "Lambda Cold Start Latency"

**Symptoms**:
- First request takes 5-10 seconds
- Subsequent requests faster
- Inconsistent response times

**Causes**:
1. Lambda cold start (initialization)
2. Large deployment package
3. Many dependencies to load

**Solutions**:

```bash
# Enable provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name ure-mvp-handler \
  --provisioned-concurrent-executions 5 \
  --qualifier $LATEST

# Check cold start metrics
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "REPORT" \
  --start-time $(date -d '1 hour ago' +%s)000 | \
  grep "Init Duration"
```

**Solutions**:
1. Enable provisioned concurrency (costs more)
2. Reduce deployment package size
3. Use Lambda layers for dependencies
4. Implement lazy loading
5. Keep Lambda warm with scheduled pings

---

## MCP Server Issues

### Issue 9: "MCP Tool Unavailable"

**Symptoms**:
- Error: "MCP server not responding"
- Market prices not available
- Weather data not available

**Causes**:
1. MCP server not running
2. Network connectivity issue
3. MCP server crashed
4. Wrong server URL in environment

**Solutions**:

```bash
# Check MCP server status
curl http://localhost:8001/health  # Agmarknet
curl http://localhost:8002/health  # Weather

# Check MCP server logs
tail -f agmarknet.log
tail -f weather.log

# Restart MCP servers
py src/mcp/servers/agmarknet_server.py &
py src/mcp/servers/weather_server.py &

# Test MCP tool call
curl -X POST http://localhost:8001/get_mandi_prices \
  -H "Content-Type: application/json" \
  -d '{"crop":"onion","district":"Nashik","state":"Maharashtra"}'
```

**Solutions**:
1. Start MCP servers
2. Verify server URLs in environment variables
3. Check network connectivity
4. Review MCP server logs
5. Implement health check monitoring
6. Use cached data as fallback

---

### Issue 10: "MCP Permission Denied"

**Symptoms**:
- Error: "Permission denied for tool"
- Agent cannot access MCP tool

**Causes**:
1. Agent role not in tool permissions
2. Tool registry misconfigured
3. Permission check logic error

**Solutions**:

```bash
# Check tool registry
cat src/mcp/tool_registry.json | jq '.get_mandi_prices.permissions'

# Test permission check
py -c "
from src.mcp.client import MCPClient
client = MCPClient('src/mcp/tool_registry.json', {})
print(client._check_permission('get_mandi_prices', 'Agri-Expert'))
"
```

**Solutions**:
1. Update tool registry permissions
2. Verify agent role name matches
3. Check MCP Client permission logic
4. Review CloudWatch logs for permission errors

---

## Database Issues

### Issue 11: "DynamoDB Throttling"

**Symptoms**:
- Error: "ProvisionedThroughputExceededException"
- Slow database operations
- Failed writes

**Causes**:
1. Too many concurrent requests
2. Hot partition key
3. On-demand capacity insufficient

**Solutions**:

```bash
# Check DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=ure-conversations \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum

# Check consumed capacity
aws dynamodb describe-table \
  --table-name ure-conversations | \
  jq '.Table.BillingModeSummary'
```

**Solutions**:
1. DynamoDB on-demand should auto-scale
2. Implement exponential backoff retry
3. Use batch operations
4. Optimize partition key design
5. Enable DynamoDB auto-scaling (if provisioned)

---

## Security & Guardrails Issues

### Issue 12: "Guardrails Blocking Legitimate Content"

**Symptoms**:
- Valid agricultural advice blocked
- False positive rate > 5%
- Users complaining about blocks

**Causes**:
1. Guardrail policies too restrictive
2. Legitimate terms in block list
3. Context not considered

**Solutions**:

```bash
# Test guardrail
aws bedrock apply-guardrail \
  --guardrail-identifier q6wfsifs9d72 \
  --guardrail-version DRAFT \
  --source INPUT \
  --content '[{"text":{"text":"Apply neem oil for aphids"}}]'

# Review guardrail configuration
aws bedrock get-guardrail \
  --guardrail-identifier q6wfsifs9d72

# Check blocked content logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "Guardrail blocked" \
  --start-time $(date -d '1 day ago' +%s)000
```

**Solutions**:
1. Review blocked content patterns
2. Adjust guardrail word policies
3. Add legitimate terms to allow list
4. Reduce sensitivity thresholds
5. Implement context-aware filtering

---

## Performance Issues

### Issue 13: "Slow Response Times"

**Symptoms**:
- Response time > 5 seconds
- Users complaining about slowness
- High latency in CloudWatch

**Causes**:
1. Bedrock API slow
2. Multiple agent calls
3. Large image processing
4. MCP server latency
5. Database queries slow

**Solutions**:

```bash
# Check response time distribution
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=ure-mvp-handler \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average,p95,p99

# Profile Lambda execution
# Add timing logs in code
import time
start = time.time()
# ... operation ...
print(f"Operation took {time.time() - start:.2f}s")
```

**Solutions**:
1. Optimize agent prompts (shorter = faster)
2. Implement caching for common queries
3. Use parallel agent calls where possible
4. Optimize image processing
5. Increase Lambda memory (faster CPU)
6. Enable response streaming

---

## Deployment Issues

### Issue 14: "CloudFormation Stack Failed"

**Symptoms**:
- Stack status: CREATE_FAILED or UPDATE_FAILED
- Resources not created
- Rollback initiated

**Causes**:
1. IAM permissions insufficient
2. Resource limits exceeded
3. Invalid parameter values
4. Resource name conflicts

**Solutions**:

```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name ure-mvp-stack \
  --max-items 20

# Check specific resource failure
aws cloudformation describe-stack-resources \
  --stack-name ure-mvp-stack \
  --logical-resource-id LambdaFunction

# Validate template
aws cloudformation validate-template \
  --template-body file://cloudformation/ure-infrastructure.yaml
```

**Solutions**:
1. Review stack events for error details
2. Fix parameter values
3. Check IAM permissions
4. Delete failed stack and retry
5. Use CloudFormation change sets for updates

---

## Quick Reference

### Common Commands

```bash
# Check Lambda logs (last 10 minutes)
aws logs tail /aws/lambda/ure-mvp-handler --since 10m --follow

# Test API endpoint
curl -X POST <api-url> \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","query":"test","language":"en"}'

# Check CloudWatch alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix ure-mvp \
  --state-value ALARM

# Restart MCP servers
pkill -f agmarknet_server
pkill -f weather_server
py src/mcp/servers/agmarknet_server.py &
py src/mcp/servers/weather_server.py &

# Check DynamoDB table status
aws dynamodb describe-table --table-name ure-conversations

# Check S3 bucket
aws s3 ls s3://ure-mvp-data-us-east-1-188238313375/
```

### Log Analysis

```bash
# Find errors in last hour
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# Find slow requests (> 10s)
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "[time, request_id, duration > 10000]" \
  --start-time $(date -d '1 hour ago' +%s)000

# Count requests by agent
aws logs filter-log-events \
  --log-group-name /aws/lambda/ure-mvp-handler \
  --filter-pattern "Agent:" \
  --start-time $(date -d '1 hour ago' +%s)000 | \
  grep -o "Agent: [A-Za-z-]*" | sort | uniq -c
```

---

## Escalation Path

### Level 1: User Support
- Check user guide
- Verify user input
- Test with different query
- Clear browser cache

### Level 2: Technical Support
- Check CloudWatch logs
- Review CloudWatch metrics
- Test API endpoint
- Verify MCP servers running

### Level 3: Engineering
- Review code
- Check AWS service status
- Analyze performance metrics
- Deploy hotfix if needed

---

## Contact Information

**Technical Support**:
- Email: support@ure-mvp.com
- Response time: 24 hours

**Emergency Hotline** (Production issues):
- Phone: +91-XXXX-XXXXXX
- Available: 24/7

**AWS Support**:
- AWS Support Console
- Support case priority: High

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0
