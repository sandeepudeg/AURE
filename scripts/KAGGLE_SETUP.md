# Kaggle API Setup Guide

This guide explains how to set up Kaggle API credentials to download the PlantVillage dataset.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Kaggle account (free)

## Step-by-Step Setup

### Step 1: Create Kaggle Account

1. Visit [https://www.kaggle.com](https://www.kaggle.com)
2. Click "Register" to create a free account
3. Complete the registration process

### Step 2: Generate API Token

1. Log in to your Kaggle account
2. Click your profile icon in the top right corner
3. Select "Settings" from the dropdown menu
4. Scroll down to the "API" section
5. Click "Create New API Token"
6. This will download a file named `kaggle.json`

**Important**: Keep this file secure! It contains your API credentials.

### Step 3: Install Kaggle Package

```bash
pip install kaggle
```

### Step 4: Configure API Credentials

You have three options to configure your Kaggle API credentials:

#### Option A: Place kaggle.json File (Recommended)

**Windows:**
```
C:\Users\<your-username>\.kaggle\kaggle.json
```

**Linux/Mac:**
```
~/.kaggle/kaggle.json
```

**Steps:**
1. Create the `.kaggle` directory if it doesn't exist
2. Move the downloaded `kaggle.json` file to this location
3. On Linux/Mac, set file permissions:
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

#### Option B: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:KAGGLE_USERNAME='your_username'
$env:KAGGLE_KEY='your_api_key'
```

**Windows (Command Prompt):**
```cmd
set KAGGLE_USERNAME=your_username
set KAGGLE_KEY=your_api_key
```

**Linux/Mac:**
```bash
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

To make these permanent, add them to your shell profile:
- Linux/Mac: Add to `~/.bashrc` or `~/.zshrc`
- Windows: Set as system environment variables

#### Option C: Pass as CLI Arguments

```bash
python scripts/download_datasets.py \
  --kaggle-username YOUR_USERNAME \
  --kaggle-key YOUR_API_KEY
```

## Verify Setup

Test your Kaggle API setup:

```bash
kaggle datasets list
```

If configured correctly, this will display a list of datasets.

## Download PlantVillage Dataset

Once configured, download the dataset:

```bash
# Download all datasets including PlantVillage
python scripts/download_datasets.py

# Download only PlantVillage
python scripts/download_datasets.py --datasets plantvillage
```

## Troubleshooting

### Error: "Kaggle credentials not found"

**Solution**: Ensure `kaggle.json` is in the correct location or environment variables are set.

### Error: "401 Unauthorized"

**Solution**: Your API token may be invalid. Generate a new token from Kaggle settings.

### Error: "kaggle: command not found"

**Solution**: Install the Kaggle package:
```bash
pip install kaggle
```

### Error: "Permission denied" (Linux/Mac)

**Solution**: Set correct file permissions:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

## Manual Download Alternative

If you prefer not to use the API:

1. Visit: [https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset)
2. Click the "Download" button (requires Kaggle login)
3. Extract the downloaded ZIP file to `data/plantvillage/`

## Dataset Information

- **Name**: New Plant Diseases Dataset (Augmented)
- **Size**: ~2GB
- **Images**: 87,000+ augmented images
- **Format**: JPG images organized by crop and disease type
- **Kaggle URL**: https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset

## Security Notes

- Never commit `kaggle.json` to version control
- Keep your API credentials private
- Regenerate your token if you suspect it has been compromised
- The `.gitignore` file already excludes `kaggle.json`

## Additional Resources

- [Official Kaggle API Documentation](https://github.com/Kaggle/kaggle-api)
- [Kaggle API GitHub Repository](https://github.com/Kaggle/kaggle-api)
- [Kaggle Datasets](https://www.kaggle.com/datasets)

---

**Last Updated**: 2026-02-27  
**URE MVP Project**
