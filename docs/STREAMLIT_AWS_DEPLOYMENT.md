# Deploying Streamlit UI on AWS

## Overview

You have several options to deploy the Streamlit UI on AWS so users can access it via a web URL:

1. **AWS App Runner** (Easiest, Recommended)
2. **AWS ECS Fargate** (Container-based)
3. **AWS EC2** (Traditional server)
4. **AWS Amplify** (Static hosting with backend)

---

## Option 1: AWS App Runner (Recommended) ⭐

**Best for:** Quick deployment, automatic scaling, minimal configuration

### Prerequisites
- Docker installed locally
- AWS CLI configured

### Step 1: Create Dockerfile

Already created at `Dockerfile` in project root.

### Step 2: Build and Push to ECR

```powershell
# Run the deployment script
.\scripts\deploy_streamlit_apprunner.ps1
```

### Step 3: Access Your App

After deployment completes, you'll get a URL like:
```
https://xxxxx.us-east-1.awsapprunner.com
```

**Cost:** ~$25-50/month (pay for what you use)

---

## Option 2: AWS ECS Fargate

**Best for:** More control, integration with VPC

### Deploy with CloudFormation

```powershell
aws cloudformation create-stack \
  --stack-name ure-streamlit-ecs \
  --template-body file://cloudformation/streamlit-ecs.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

**Cost:** ~$30-60/month

---

## Option 3: AWS EC2

**Best for:** Full control, custom configurations

### Launch EC2 Instance

```powershell
# Run the EC2 deployment script
.\scripts\deploy_streamlit_ec2.ps1
```

**Cost:** ~$10-30/month (t3.small or t3.medium)

---

## Option 4: Static Hosting (Alternative)

Convert Streamlit to a static site and host on:
- AWS S3 + CloudFront
- AWS Amplify

**Note:** Requires significant refactoring of the Streamlit app.

---

## Comparison

| Option | Ease | Cost/Month | Scaling | Setup Time |
|--------|------|------------|---------|------------|
| App Runner | ⭐⭐⭐⭐⭐ | $25-50 | Auto | 10 min |
| ECS Fargate | ⭐⭐⭐ | $30-60 | Auto | 30 min |
| EC2 | ⭐⭐ | $10-30 | Manual | 20 min |
| Amplify | ⭐ | $5-15 | Auto | 2+ hours |

---

## Recommended: AWS App Runner

This is the easiest and most cost-effective option for deploying Streamlit on AWS.

### Quick Deploy

```powershell
.\scripts\deploy_streamlit_apprunner.ps1
```

This script will:
1. Create a Dockerfile for Streamlit
2. Build the Docker image
3. Push to Amazon ECR
4. Create App Runner service
5. Configure environment variables
6. Provide you with the public URL

---

## Security Considerations

### 1. Add Authentication

Use AWS Cognito or implement basic auth:

```python
# Add to app.py
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials,
    'ure_mvp',
    'auth_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show app
    pass
elif authentication_status == False:
    st.error('Username/Password is incorrect')
```

### 2. Use HTTPS

All AWS deployment options provide HTTPS by default.

### 3. Restrict Access

Use AWS WAF to restrict access by:
- IP address
- Geographic location
- Rate limiting

---

## Next Steps

Choose your deployment method and run the corresponding script!
