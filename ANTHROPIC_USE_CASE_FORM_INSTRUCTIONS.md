# Anthropic Use Case Form - Required Action

## ⚠️ Action Required

Your Mumbai deployment is complete, but you need to fill out the Anthropic use case form before Claude models will work.

---

## Error Message

```
ResourceNotFoundException: Model use case details have not been submitted for this account. 
Fill out the Anthropic use case details form before using the model. 
If you have already filled out the form, try again in 15 minutes.
```

---

## How to Submit the Form

### ⚠️ Note: Model Access Page Retired

AWS has retired the model access page. Models are now automatically enabled on first use, but Anthropic models require use case details submission.

### Step 1: Open Bedrock Playground

**Option A: Direct Playground Link (Recommended)**
1. Go to: https://console.aws.amazon.com/bedrock/home?region=ap-south-1#/playground
2. Make sure you're in the **ap-south-1 (Mumbai)** region

**Option B: Via Model Catalog**
1. Go to: https://console.aws.amazon.com/bedrock/home?region=ap-south-1#/models
2. Search for "Claude 3.5 Sonnet v2"
3. Click "Try in Playground"

### Step 2: Trigger the Use Case Form

1. In the playground, select **"Claude 3.5 Sonnet v2"** from the model dropdown
2. Try to send any message (e.g., "Hello")
3. The use case form will appear automatically

### Step 3: Fill Out Use Case Form

You'll be prompted to fill out a form with:

**Required Information:**
- **Company Name:** Your company or organization name
- **Use Case Description:** Describe how you'll use Claude
  - Example: "Agricultural advisory chatbot for Indian farmers providing crop recommendations, disease diagnosis, and market price information"
- **Industry:** Select "Agriculture" or "Technology"
- **Expected Monthly Usage:** Estimate your usage
  - Example: "10,000-50,000 API calls per month"

**Tips for Form:**
- Be specific about your use case
- Mention it's for agricultural education/advisory
- Indicate it's for production use
- Be honest about expected usage

### Step 4: Submit and Wait

1. Click **"Submit"** or **"Request access"**
2. Wait **15-30 minutes** for approval
3. You'll receive an email confirmation when approved
4. Model access will be automatically granted

---

## Alternative: Use Nova Lite (No Form Required)

While waiting for Anthropic approval, you can use Amazon Nova Lite which doesn't require a use case form:

```powershell
aws lambda update-function-configuration `
    --function-name ure-mvp-handler-mumbai `
    --region ap-south-1 `
    --environment "Variables={DYNAMODB_TABLE_NAME=ure-conversations-mumbai,DYNAMODB_USER_TABLE=ure-user-profiles-mumbai,DYNAMODB_VILLAGE_TABLE=ure-village-amenities-mumbai,S3_BUCKET_NAME=ure-mvp-data-mumbai-188238313375,BEDROCK_KB_ID=7XROZ6PZIF,BEDROCK_MODEL_ID=amazon.nova-lite-v1:0,BEDROCK_REGION=ap-south-1,LOG_LEVEL=INFO}"
```

**Nova Lite Characteristics:**
- ✅ No use case form required
- ✅ Works immediately
- ✅ Faster responses
- ✅ Lower cost
- ⚠️ Less capable than Claude for complex queries

---

## After Form Approval

Once your form is approved (15-30 minutes):

### Test the API

```powershell
$body = @{
    user_id = "test_farmer"
    query = "What crops grow well in Maharashtra?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### Expected Response

```json
{
  "user_id": "test_farmer",
  "query": "What crops grow well in Maharashtra?",
  "response": "Let me help you with crop recommendations for Maharashtra...",
  "agent_used": "supervisor",
  "timestamp": "2026-02-28T12:30:00.000000"
}
```

---

## Verification Steps

### 1. Check Model Access Status

```powershell
aws bedrock get-foundation-model `
    --model-identifier apac.anthropic.claude-3-5-sonnet-20241022-v2:0 `
    --region ap-south-1 `
    --query 'modelDetails.{ModelId:modelId,Status:modelLifecycle.status}'
```

Expected output:
```json
{
    "ModelId": "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "Status": "ACTIVE"
}
```

### 2. Test Lambda Function

```powershell
aws lambda invoke `
    --function-name ure-mvp-handler-mumbai `
    --region ap-south-1 `
    --payload '{"user_id":"test","query":"Hello"}' `
    response.json

Get-Content response.json | ConvertFrom-Json
```

### 3. Check CloudWatch Logs

```powershell
aws logs tail /aws/lambda/ure-mvp-handler-mumbai --region ap-south-1 --follow
```

Look for successful responses without errors.

---

## Troubleshooting

### Form Not Appearing

If you don't see the use case form:
1. Make sure you're in ap-south-1 region
2. Try a different browser or clear cache
3. Contact AWS Support if issue persists

### Form Rejected

If your form is rejected:
1. Resubmit with more detailed use case description
2. Emphasize educational/agricultural advisory purpose
3. Provide more specific usage estimates

### Still Getting Errors After 15 Minutes

1. Wait up to 30 minutes for propagation
2. Check email for approval confirmation
3. Verify model access in console shows "Available"
4. Try invoking Lambda again

---

## Current Deployment Status

**Infrastructure:** ✅ 100% Complete
- Mumbai Lambda: Deployed
- Singapore Streamlit: Running
- API Gateway: Configured
- DynamoDB: Ready
- S3: Ready

**Model Access:** ⚠️ Pending Form Approval
- Form submission required
- Expected wait: 15-30 minutes
- Alternative: Use Nova Lite immediately

**Overall Status:** 95% Complete (waiting for Anthropic approval)

---

## Quick Start with Nova Lite

Don't want to wait? Switch to Nova Lite now:

```powershell
# Update Lambda to use Nova Lite
aws lambda update-function-configuration `
    --function-name ure-mvp-handler-mumbai `
    --region ap-south-1 `
    --environment "Variables={DYNAMODB_TABLE_NAME=ure-conversations-mumbai,DYNAMODB_USER_TABLE=ure-user-profiles-mumbai,DYNAMODB_VILLAGE_TABLE=ure-village-amenities-mumbai,S3_BUCKET_NAME=ure-mvp-data-mumbai-188238313375,BEDROCK_KB_ID=7XROZ6PZIF,BEDROCK_MODEL_ID=amazon.nova-lite-v1:0,BEDROCK_REGION=ap-south-1,LOG_LEVEL=INFO}"

# Wait 10 seconds
Start-Sleep -Seconds 10

# Test immediately
$body = @{user_id="test"; query="Hello"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query" -Method Post -Body $body -ContentType "application/json"
```

This will work immediately while you wait for Claude approval!

---

## Summary

1. ✅ Infrastructure deployed successfully
2. ⚠️ Fill out Anthropic use case form (15-30 min wait)
3. ✅ Alternative: Use Nova Lite immediately
4. ✅ Streamlit UI is live and ready
5. ⚠️ API will work once form is approved

**Next Step:** Go to AWS Console and submit the Anthropic use case form!

**Console Link:** https://console.aws.amazon.com/bedrock/home?region=ap-south-1#/modelaccess
