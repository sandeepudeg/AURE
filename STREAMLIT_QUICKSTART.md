# Streamlit UI with AWS Backend - Quick Start Guide

## 🚀 Quick Start (Recommended)

Run the Streamlit UI connected to your deployed AWS backend:

```powershell
.\run_streamlit_with_aws.ps1
```

That's it! The UI will open in your browser automatically.

---

## 📋 What You Get

### Full-Featured Web Interface
- 🌾 **Multi-Agent AI System**
  - Supervisor Agent (routes queries)
  - Agri-Expert Agent (crop diseases, pests)
  - Policy Navigator Agent (government schemes)
  - Resource Optimizer Agent (irrigation, weather)

- 🌍 **Multilingual Support**
  - English
  - Hindi (हिंदी)
  - Marathi (मराठी)

- 📸 **Image Upload**
  - Upload crop images for disease detection
  - AI-powered image analysis

- 📍 **Auto Location Detection**
  - Detects your location from IP
  - Provides location-specific advice

- 👤 **User Profile**
  - Save your farming details
  - Personalized recommendations

- 💬 **Conversation History**
  - View past conversations
  - Continue previous discussions

- 👍👎 **Feedback System**
  - Rate responses
  - Help improve the system

---

## 🎯 How to Use

### 1. Start the Application

```powershell
.\run_streamlit_with_aws.ps1
```

### 2. The UI Opens Automatically

Your browser will open to `http://localhost:8501`

### 3. Fill Your Profile (Optional)

In the sidebar:
- Enter your name, village, district
- Add phone number
- Select crops you grow
- Specify land size

### 4. Ask Questions

Type your farming questions in the chat:
- "What crops are suitable for my region?"
- "Tell me about PM-KISAN scheme"
- "How should I manage irrigation?"
- "What's the weather forecast?"

### 5. Upload Images (Optional)

- Click "📸 Upload Crop Image"
- Select an image of your crop
- Ask about diseases or issues

### 6. Use Quick Actions

Click quick action buttons for common queries:
- 🌾 Crop Recommendations
- 🦠 Disease Diagnosis
- 💰 Government Schemes
- 💧 Irrigation Tips

### 7. Provide Feedback

After each response:
- Click 👍 if helpful
- Click 👎 if not helpful
- Add comments (optional)

---

## 🔧 Configuration

### AWS Backend Mode (Default)
```powershell
.\run_streamlit_with_aws.ps1
```

**Connects to:**
- API Endpoint: `https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query`
- Uses deployed Lambda function
- No local setup required

### Local Development Mode
```powershell
.\run_streamlit_local.ps1
```

**Requires:**
- All Python dependencies installed
- `.env` file configured
- AWS credentials for Bedrock

---

## 📱 Features Walkthrough

### Sidebar

**Settings Section:**
- 🌐 Mode indicator (AWS/Local)
- 🌍 Language selector
- 📍 Location display

**User Profile:**
- Name, Village, District
- Phone number
- Crops grown
- Land size

**Help Guide:**
- How to use GramSetu
- Language support info
- Image upload guide
- Privacy & safety

### Main Chat Area

**Welcome Message:**
- Quick action buttons
- Getting started tips

**Chat Interface:**
- User messages (right side)
- AI responses (left side)
- Agent badges showing which specialist responded

**Image Upload:**
- Drag & drop or click to upload
- Supports JPG, PNG
- Preview before sending

**Feedback Buttons:**
- Appear after each AI response
- Thumbs up/down
- Optional comment field

---

## 💡 Example Queries

### Crop Recommendations
```
"What crops should I grow in Pune district during monsoon season?"
```

### Disease Diagnosis
```
"My tomato plants have yellow leaves and brown spots. What's wrong?"
```
(Upload image for better diagnosis)

### Government Schemes
```
"How can I apply for PM-KISAN? What are the eligibility criteria?"
```

### Irrigation Management
```
"When should I irrigate my wheat crop? How much water is needed?"
```

### Weather-Based Advice
```
"What farming activities should I do based on current weather?"
```

### Market Prices
```
"What are the current mandi prices for onions in Nashik?"
```

### Hindi Query
```
"मुझे टमाटर की खेती के बारे में बताओ"
```

### Marathi Query
```
"मला शेतीबद्दल माहिती हवी आहे"
```

---

## 🛠️ Troubleshooting

### UI Won't Start

**Check virtual environment:**
```powershell
# Activate manually
.\rural\Scripts\Activate.ps1

# Then run
streamlit run src/ui/app.py
```

### Connection Error

**Verify API endpoint:**
```powershell
# Test API directly
$body = @{
    query = "test"
    user_id = "test"
    language = "en"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -Method POST -Body $body -ContentType "application/json"
```

### Slow Responses

- First query may take 10-15 seconds (Lambda cold start)
- Subsequent queries are faster (2-5 seconds)
- Complex queries may take longer

### Image Upload Not Working

- Check file size (max 5MB)
- Use JPG or PNG format
- Ensure good image quality

---

## 🔄 Switching Modes

### To AWS Mode:
```powershell
$env:USE_API_MODE = "true"
$env:API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
streamlit run src/ui/app.py
```

### To Local Mode:
```powershell
$env:USE_API_MODE = "false"
streamlit run src/ui/app.py
```

---

## 📊 Monitoring

### View Logs

**Streamlit logs:**
- Shown in terminal where you ran the script

**AWS Lambda logs:**
```powershell
aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1
```

### Check Status

```powershell
.\scripts\check_deployment_status.ps1
```

---

## 🎨 Customization

### Change Port

```powershell
streamlit run src/ui/app.py --server.port 8502
```

### Change Theme

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1B5E20"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 🆘 Support

### Common Issues

1. **"Module not found" error**
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

2. **"Connection refused" error**
   - Check API endpoint is correct
   - Verify Lambda function is running

3. **"Guardrails blocking" error**
   - Adjust Bedrock Guardrails in AWS Console
   - Or temporarily disable for testing

### Get Help

- Check logs in terminal
- Review `docs/TROUBLESHOOTING_GUIDE.md`
- Run status check: `.\scripts\check_deployment_status.ps1`

---

## 🎉 You're Ready!

Start the application:
```powershell
.\run_streamlit_with_aws.ps1
```

Happy farming! 🌾
