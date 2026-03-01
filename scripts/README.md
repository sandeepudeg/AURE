# URE MVP Data Scripts

This directory contains scripts for downloading and ingesting data into AWS services for the URE MVP.

## Scripts Overview

1. **download_datasets.py** - Download all required datasets
2. **ingest_data.py** - Ingest datasets into AWS services

## Quick Start

### Step 1: Download Datasets

```bash
# Download all datasets (requires Kaggle credentials for PlantVillage)
python scripts/download_datasets.py

# Download only sample data (no Kaggle required)
python scripts/download_datasets.py --datasets agmarknet pmkisan village

# Verify datasets
python scripts/download_datasets.py --verify-only
```

### Step 2: Ingest to AWS

```bash
# Quick test with sample data
python scripts/ingest_data.py --sample-data --steps dynamodb

# Full ingestion
python scripts/ingest_data.py --steps all
```

---

## 1. Dataset Download Script

### Overview

The `download_datasets.py` script downloads all required datasets for the URE MVP:

- **PlantVillage** (87,000+ images, ~2GB) - via Kaggle API
- **Agmarknet** market prices - sample CSV generated
- **PM-Kisan** scheme documents - sample text generated
- **Village amenities** - sample CSV generated

### Kaggle API Setup

For PlantVillage dataset download, you need Kaggle API credentials.

**Quick Setup:**

1. Create account at [https://www.kaggle.com](https://www.kaggle.com)
2. Go to Account Settings → API → Create New API Token
3. Download `kaggle.json` file
4. Place in `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<username>\.kaggle\kaggle.json` (Windows)
5. Install: `pip install kaggle`

**Detailed Instructions**: See [KAGGLE_SETUP.md](KAGGLE_SETUP.md)

### Usage

```bash
# Download all datasets with Kaggle credentials
python scripts/download_datasets.py \
  --kaggle-username YOUR_USERNAME \
  --kaggle-key YOUR_API_KEY

# Download only sample data (no Kaggle needed)
python scripts/download_datasets.py --datasets agmarknet pmkisan village

# Download to custom directory
python scripts/download_datasets.py --data-dir /path/to/data

# Verify datasets are present
python scripts/download_datasets.py --verify-only
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--data-dir` | Base directory for datasets | `data` |
| `--datasets` | Datasets to download | `all` |
| `--kaggle-username` | Kaggle username | None (uses env var) |
| `--kaggle-key` | Kaggle API key | None (uses env var) |
| `--verify-only` | Only verify, don't download | False |

### Output Structure

```
data/
├── plantvillage/           # 87,000+ crop disease images
│   ├── train/
│   ├── valid/
│   └── test/
├── agmarknet_prices.csv    # Market prices (sample)
├── schemes/                # Government scheme docs
│   └── pm_kisan_scheme.txt
└── village_amenities.csv   # Village data (sample)
```

---

## 2. Data Ingestion Script

## Prerequisites

### AWS Credentials

Ensure AWS credentials are configured:

```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=ap-south-1

# Option 2: AWS CLI configuration
aws configure
```

### Python Environment

Activate the virtual environment:

```bash
# Windows
rural\Scripts\activate

# Linux/Mac
source rural/bin/activate
```

### Required Datasets

Download the following datasets before running ingestion:

1. **PlantVillage Dataset** (50,000+ images)
   - Source: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
   - Extract to: `data/plantvillage/`

2. **Agmarknet Prices CSV**
   - Source: https://www.kaggle.com/datasets/arjunyadav99/indian-agricultural-mandi-prices-20232025
   - Save as: `data/agmarknet_prices.csv`

3. **PM-Kisan Scheme PDF**
   - Source: https://pmkisan.gov.in/
   - Save to: `data/schemes/pm-kisan.pdf`

4. **Village Amenities CSV** (Optional - sample data provided)
   - Format: `village_name,district,state,irrigation_type,distance_to_town,electricity,school,hospital`
   - Save as: `data/village_amenities.csv`

## Usage

### Quick Start (Sample Data)

For testing without downloading datasets:

```bash
python scripts/ingest_data.py --sample-data --steps dynamodb
```

This creates DynamoDB tables with sample data for Nashik village.

### Full Ingestion

With all datasets downloaded:

```bash
python scripts/ingest_data.py \
  --plantvillage-dir data/plantvillage \
  --schemes-dir data/schemes \
  --agmarknet-csv data/agmarknet_prices.csv \
  --village-csv data/village_amenities.csv \
  --steps all
```

### Step-by-Step Ingestion

Run individual steps:

```bash
# Step 1: S3 only
python scripts/ingest_data.py \
  --plantvillage-dir data/plantvillage \
  --schemes-dir data/schemes \
  --agmarknet-csv data/agmarknet_prices.csv \
  --steps s3

# Step 2: DynamoDB only
python scripts/ingest_data.py \
  --village-csv data/village_amenities.csv \
  --steps dynamodb

# Step 3: Bedrock KB only (requires S3 data first)
python scripts/ingest_data.py \
  --steps bedrock
```

### Custom Configuration

```bash
python scripts/ingest_data.py \
  --region ap-south-1 \
  --bedrock-region us-east-1 \
  --s3-bucket my-custom-bucket \
  --plantvillage-dir /path/to/plantvillage \
  --steps all
```

## Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--region` | AWS region for S3/DynamoDB | `ap-south-1` |
| `--bedrock-region` | AWS region for Bedrock | `us-east-1` |
| `--s3-bucket` | S3 bucket name | `knowledge-base-bharat` |
| `--plantvillage-dir` | PlantVillage dataset path | None |
| `--schemes-dir` | Scheme PDFs directory | None |
| `--agmarknet-csv` | Agmarknet CSV file | None |
| `--village-csv` | Village amenities CSV | None |
| `--steps` | Steps to execute | `all` |
| `--sample-data` | Use sample data only | False |

## Output

### S3 Bucket Structure

After ingestion, S3 bucket will have:

```
knowledge-base-bharat/
├── plantvillage/
│   ├── Tomato___Bacterial_spot/
│   ├── Tomato___Early_blight/
│   └── ... (38 disease classes)
├── schemes/
│   ├── pm-kisan.pdf
│   └── pkvy-guidelines.pdf
└── datasets/
    └── agmarknet_prices.csv
```

### DynamoDB Tables

Three tables will be created:

1. **ure-conversations**
   - Partition Key: `user_id` (String)
   - Purpose: Store chat history

2. **ure-village-amenities**
   - Partition Key: `village_name` (String)
   - Sort Key: `district` (String)
   - GSI: `state-index`
   - Purpose: Village infrastructure data

3. **ure-user-profiles**
   - Partition Key: `user_id` (String)
   - Purpose: Farmer profiles

### Bedrock Knowledge Base

After setup, you'll receive:

```
Knowledge Base ID: XXXXXXXXXX
```

**Important**: Save this ID to your `.env` file:

```bash
BEDROCK_KB_ID=XXXXXXXXXX
```

## Verification

### Verify S3 Upload

```bash
aws s3 ls s3://knowledge-base-bharat/ --recursive
```

### Verify DynamoDB Tables

```bash
aws dynamodb list-tables
aws dynamodb scan --table-name ure-village-amenities --limit 5
```

### Verify Bedrock KB

```python
from src.utils.bedrock_kb_loader import BedrockKBLoader

loader = BedrockKBLoader()
result = loader.query_knowledge_base(
    kb_id='YOUR_KB_ID',
    query='PM-Kisan eligibility criteria'
)
print(result)
```

## Troubleshooting

### Issue: S3 Bucket Already Exists

```
Error: BucketAlreadyExists
```

**Solution**: Use a different bucket name with `--s3-bucket` flag.

### Issue: IAM Permissions

```
Error: AccessDenied
```

**Solution**: Ensure your AWS credentials have permissions for:
- S3: `s3:CreateBucket`, `s3:PutObject`, `s3:GetObject`
- DynamoDB: `dynamodb:CreateTable`, `dynamodb:PutItem`
- Bedrock: `bedrock:CreateKnowledgeBase`, `bedrock:CreateDataSource`

### Issue: Bedrock Not Available

```
Error: InvalidRegion
```

**Solution**: Bedrock is only available in specific regions. Use:
- `--bedrock-region us-east-1` (recommended)
- `--bedrock-region us-west-2`

### Issue: Large Dataset Upload Timeout

**Solution**: Upload in batches or increase timeout:

```python
from src.utils.s3_uploader import S3Uploader

uploader = S3Uploader('knowledge-base-bharat')
# Upload specific subdirectories
uploader.upload_directory('data/plantvillage/Tomato', 'plantvillage/Tomato')
```

## Cost Estimation

Approximate AWS costs for MVP data ingestion:

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| S3 Storage | 50GB (PlantVillage) | $1.15/month |
| DynamoDB | 3 tables, 1000 items | $0.25/month |
| Bedrock KB | 100 documents | $0.10/month |
| OpenSearch Serverless | 1 collection | $0.24/hour |
| **Total** | | **~$8-10/month** |

## Next Steps

After successful ingestion:

1. Update `.env` file with `BEDROCK_KB_ID`
2. Configure MCP servers (see `src/mcp/README.md`)
3. Test agents: `python test_agents.py`
4. Deploy Lambda function (see `src/aws/README.md`)
5. Launch Streamlit UI (see `src/ui/README.md`)

## Support

For issues or questions:
- Check logs in console output
- Review AWS CloudWatch logs
- Consult `docs/DATA_SOURCES.md` for data architecture

---

**Last Updated**: 2026-02-27  
**Maintained By**: URE Development Team
