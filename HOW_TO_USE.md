# How to Interact with URE MVP Deployed Application

## Quick Start

Your URE MVP application is deployed and ready to use!

**API Endpoint:** `https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query`

---

## Method 1: Web Interface (Easiest) 🌐

1. Open `test_api.html` in your browser
2. Fill in the form:
   - **User ID**: Any identifier (e.g., "farmer_001")
   - **Query**: Your farming question
   - **Language**: English, Hindi, or Marathi
3. Click "Send Query"
4. View the response!

**Quick Open:**
```powershell
Start-Process test_api.html
```

---

## Method 2: PowerShell Commands 💻

### Basic Query
```powershell
$body = @{
    query = "What crops are good for Maharashtra?"
    user_id = "farmer_001"
    language = "en"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -Method POST -Body $body -ContentType "application/json"
```

### Run Test Examples
```powershell
.\scripts\test_api_examples.ps1
```

This will run 4 example queries:
1. General farming query
2. Government scheme query
3. Irrigation query
4. Hindi language query

---

## Method 3: Streamlit UI (Local with AWS Backend) 🎨

Run the full Streamlit interface locally, connected to AWS:

```powershell
.\scripts\run_local_ui.ps1
```

Features:
- User profile form
- Image upload for crop disease detection
- Feedback buttons
- Conversation history
- Quick action buttons
- Help guide

---

## Method 4: cURL (Cross-Platform) 🔧

```bash
curl -X POST https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "farmer_001",
    "query": "What crops are suitable for Maharashtra?",
    "language": "en"
  }'
```

---

## Example Queries

### 1. Crop Recommendations
```json
{
  "user_id": "farmer_001",
  "query": "What crops should I grow in Pune district?",
  "language": "en"
}
```

### 2. Government Schemes
```json
{
  "user_id": "farmer_002",
  "query": "Tell me about PM-KISAN scheme and how to apply",
  "language": "en"
}
```

### 3. Irrigation Management
```json
{
  "user_id": "farmer_003",
  "query": "How should I schedule irrigation for my wheat crop?",
  "language": "en"
}
```

### 4. Weather-Based Advice
```json
{
  "user_id": "farmer_004",
  "query": "What farming activities should I do based on current weather?",
  "language": "en"
}
```

### 5. Hindi Query
```json
{
  "user_id": "farmer_005",
  "query": "मुझे टमाटर की खेती के बारे में बताओ",
  "language": "hi"
}
```

### 6. Marathi Query
```json
{
  "user_id": "farmer_006",
  "query": "मला शेतीबद्दल माहिती हवी आहे",
  "language": "mr"
}
```

---

## Response Format

All responses follow this structure:

```json
{
  "user_id": "farmer_001",
  "query": "Your question",
  "response": "AI-generated response with farming advice",
  "agent_used": "supervisor",
  "metadata": {
    "translated": false,
    "target_language": "en"
  },
  "timestamp": "2026-02-28T07:56:32"
}
```

---

## Available Agents

The system automatically routes your query to the appropriate specialist:

1. **Supervisor Agent** - Routes queries and coordinates responses
2. **Agri-Expert Agent** - Crop diseases, pests, and cultivation advice
3. **Policy Navigator Agent** - Government schemes and subsidies
4. **Resource Optimizer Agent** - Irrigation, weather, and resource management

---

## Supported Languages

- **English** (`en`)
- **Hindi** (`hi`) - हिंदी
- **Marathi** (`mr`) - मराठी

The system automatically translates responses to your preferred language.

---

## Check Deployment Status

Run the status check script:

```powershell
.\scripts\check_deployment_status.ps1
```

This will verify:
- ✓ Lambda function status
- ✓ Lambda layer attachment
- ✓ API Gateway configuration
- ✓ DynamoDB tables
- ✓ IAM roles
- ✓ API endpoint connectivity

---

## Troubleshooting

### API Not Responding
1. Check deployment status: `.\scripts\check_deployment_status.ps1`
2. Verify Lambda function: `aws lambda get-function --function-name ure-mvp-handler --region us-east-1`
3. Check CloudWatch logs: `aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1`

### Guardrails Blocking Queries
If legitimate agricultural queries are being blocked:
1. Go to AWS Bedrock Console → Guardrails
2. Find guardrail ID: `q6wfsifs9d72`
3. Adjust content filters to be less restrictive

### Connection Timeout
- Increase Lambda timeout if needed (current: 300 seconds)
- Check network connectivity
- Verify API Gateway endpoint is correct

---

## Next Steps

1. **Test the API** - Run `.\scripts\test_api_examples.ps1`
2. **Try the Web UI** - Open `test_api.html`
3. **Run Streamlit** - Execute `.\scripts\run_local_ui.ps1`
4. **Monitor Usage** - Check CloudWatch metrics in AWS Console

---

## Support

For issues or questions:
- Check logs: `aws logs tail /aws/lambda/ure-mvp-handler --region us-east-1`
- Review documentation in `docs/` folder
- Run status check: `.\scripts\check_deployment_status.ps1`

---

**Happy Farming! 🌾**
