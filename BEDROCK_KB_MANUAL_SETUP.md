# Bedrock Knowledge Base Manual Setup Guide

## Current Status

✅ **Completed:**
- S3 bucket created: `ure-mvp-data-188238313375`
- PlantVillage dataset uploaded (87,900 images)
- Government scheme PDFs uploaded (4 files)
- Agmarknet CSV uploaded
- DynamoDB tables created:
  - `ure-conversations`
  - `ure-village-amenities` (3 sample villages)
  - `ure-user-profiles` (1 sample user)
- OpenSearch Serverless collection created: `ure-knowledge-base`
  - ARN: `arn:aws:aoss:us-east-1:188238313375:collection/q4hpsg5m4hm0fryx7dv6`
- IAM role created: `BedrockKnowledgeBaseRole`

⚠️ **Pending:**
- Bedrock Knowledge Base creation (requires manual AWS Console setup)

## Manual Setup Steps

### Step 1: Open AWS Bedrock Console

1. Go to AWS Console: https://console.aws.amazon.com/bedrock/
2. Navigate to **Knowledge bases** in the left sidebar
3. Click **Create knowledge base**

### Step 2: Configure Knowledge Base

**Knowledge base details:**
- Name: `ure-pm-kisan-kb`
- Description: `PM-Kisan scheme information for URE MVP`
- IAM role: Select **Use an existing service role**
  - Choose: `BedrockKnowledgeBaseRole`

### Step 3: Configure Data Source

**Data source:**
- Data source name: `pm-kisan-docs`
- S3 URI: `s3://ure-mvp-data-188238313375/schemes/`

### Step 4: Configure Embeddings

**Embeddings model:**
- Select: `Titan Embeddings G1 - Text`

### Step 5: Configure Vector Store

**Vector database:**
- Select: **Amazon OpenSearch Serverless**
- Collection: Select `ure-knowledge-base`
- Vector index name: `ure-kb-index`
- Vector field: `embedding`
- Text field: `text`
- Metadata field: `metadata`

### Step 6: Review and Create

1. Review all settings
2. Click **Create knowledge base**
3. Wait for the knowledge base to be created
4. Note the **Knowledge Base ID** (format: `XXXXXXXXXX`)

### Step 7: Sync Data Source

1. After creation, go to the knowledge base details page
2. Click on the **Data sources** tab
3. Select `pm-kisan-docs`
4. Click **Sync** to start ingesting the PDFs
5. Wait for sync to complete (may take 5-10 minutes)

### Step 8: Update .env File

Once the Knowledge Base is created, update the `.env` file:

```bash
BEDROCK_KB_ID=<your-knowledge-base-id>
```

Replace `<your-knowledge-base-id>` with the actual ID from Step 6.

## Verification

Test the Knowledge Base using AWS Console:

1. Go to your Knowledge Base
2. Click **Test** tab
3. Try a query: "What is PM-Kisan scheme?"
4. Verify you get relevant responses from the PDFs

## Troubleshooting

### Issue: IAM Role Permissions Error

If you get permission errors, ensure the `BedrockKnowledgeBaseRole` has these policies:

1. **S3 Access:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ure-mvp-data-188238313375",
        "arn:aws:s3:::ure-mvp-data-188238313375/*"
      ]
    }
  ]
}
```

2. **OpenSearch Access:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aoss:APIAccessAll"
      ],
      "Resource": [
        "arn:aws:aoss:us-east-1:188238313375:collection/q4hpsg5m4hm0fryx7dv6"
      ]
    }
  ]
}
```

3. **Bedrock Model Access:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
      ]
    }
  ]
}
```

### Issue: OpenSearch Collection Not Found

If the collection is not visible:
1. Ensure you're in the correct region (us-east-1)
2. Check the collection status in OpenSearch Serverless console
3. Wait a few minutes for the collection to become active

## Next Steps After Setup

Once the Knowledge Base is configured:

1. Update `.env` with the Knowledge Base ID
2. Test the agents: `py test_agents.py`
3. Run the Streamlit UI: `streamlit run src/ui/app.py`

## Alternative: Skip Bedrock KB for Testing

If you want to test the agents without Bedrock KB:

1. The agents can work with direct API calls to Agmarknet and Weather services
2. The Policy-Navigator agent will have limited functionality without the KB
3. You can still test Agri-Expert and Resource-Optimizer agents fully
