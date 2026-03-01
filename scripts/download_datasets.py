# #!/usr/bin/env python3
# """
# URE MVP Dataset Download Script
# Targets: D:\Learning\Assembler_URE_Rural\data
# Uses kagglehub for CV data and generates synthetic data for other modules.
# """

# import os
# import logging
# import argparse
# import csv
# import shutil
# import kagglehub
# from pathlib import Path

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # --- WINDOWS PATH CONFIGURATION ---
# # Using raw strings (r"") to handle backslashes correctly
# BASE_DIR = r"D:\Learning\Assembler_URE_Rural\data"
# PLANTVILLAGE_DIR = os.path.join(BASE_DIR, "plantvillage")
# AGMARKNET_FILE = os.path.join(BASE_DIR, "agmarknet_prices.csv")
# SCHEMES_DIR = os.path.join(BASE_DIR, "schemes")
# VILLAGE_FILE = os.path.join(BASE_DIR, "village_amenities.csv")


# def download_plantvillage_kaggle(output_dir: str) -> bool:
#     """
#     Download PlantVillage dataset from Kaggle using kagglehub.
#     Automatically moves data to your specific D: drive project folder.
#     """
#     logger.info("=" * 60)
#     logger.info(f"DOWNLOADING TO: {output_dir}")
#     logger.info("=" * 60)
    
#     try:
#         # 1. Download/Verify via kagglehub (handles caching in ~/.cache/kagglehub)
#         logger.info("Fetching dataset via kagglehub...")
#         cache_path = kagglehub.dataset_download("vipoooool/new-plant-diseases-dataset")
        
#         dest_path = Path(output_dir)
#         dest_path.mkdir(parents=True, exist_ok=True)
        
#         # 2. Sync from cache to your D: drive project directory
#         # We copy because kagglehub might manage the cache folder separately
#         if not any(dest_path.iterdir()):
#             logger.info("Syncing files from cache to project directory...")
#             shutil.copytree(cache_path, dest_path, dirs_exist_ok=True)
#             logger.info("✓ Sync complete.")
#         else:
#             logger.info("✓ Dataset already exists in target directory. Skipping copy.")
            
#         return True
#     except Exception as e:
#         logger.error(f"Failed to download PlantVillage dataset: {e}")
#         return False


# def create_sample_agmarknet_data(output_file: str) -> bool:
#     """Create sample Agmarknet market prices CSV"""
#     logger.info(f"Creating Agmarknet data at: {output_file}")
#     try:
#         sample_data = [
#             {'date': '2026-02-27', 'crop': 'Wheat', 'district': 'Nashik', 'state': 'Maharashtra', 'price': 2500, 'market_name': 'Nashik APMC'},
#             {'date': '2026-02-27', 'crop': 'Onion', 'district': 'Nashik', 'state': 'Maharashtra', 'price': 3000, 'market_name': 'Nashik APMC'},
#             {'date': '2026-02-27', 'crop': 'Tomato', 'district': 'Nashik', 'state': 'Maharashtra', 'price': 2000, 'market_name': 'Nashik APMC'},
#         ]
#         Path(output_file).parent.mkdir(parents=True, exist_ok=True)
#         with open(output_file, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.DictWriter(f, fieldnames=['date', 'crop', 'district', 'state', 'price', 'market_name'])
#             writer.writeheader()
#             writer.writerows(sample_data)
#         return True
#     except Exception as e:
#         logger.error(f"Agmarknet creation failed: {e}")
#         return False


# def create_sample_pmkisan_docs(output_dir: str) -> bool:
#     """Create sample PM-Kisan scheme documents for RAG"""
#     logger.info(f"Creating Scheme docs at: {output_dir}")
#     try:
#         dest = Path(output_dir)
#         dest.mkdir(parents=True, exist_ok=True)
#         content = (
#             "PM-KISAN SCHEME - PRADHAN MANTRI KISAN SAMMAN NIDHI\n"
#             "ELIGIBILITY: Small and marginal farmers with land up to 2 hectares\n"
#             "BENEFITS: ₹6000 per year in three installments\n"
#             "URL: https://pmkisan.gov.in\n"
#         )
#         with open(dest / 'pm_kisan_scheme.txt', 'w', encoding='utf-8') as f:
#             f.write(content)
#         return True
#     except Exception as e:
#         logger.error(f"Scheme creation failed: {e}")
#         return False


# def create_sample_village_amenities(output_file: str) -> bool:
#     """Create sample village amenities CSV"""
#     logger.info(f"Creating Village amenities at: {output_file}")
#     try:
#         sample_villages = [
#             {'village_name': 'Nashik', 'district': 'Nashik', 'state': 'Maharashtra', 'irrigation_type': 'Canal', 'distance_to_town': 0, 'electricity': 'Yes', 'school': 'Yes', 'hospital': 'Yes'},
#         ]
#         Path(output_file).parent.mkdir(parents=True, exist_ok=True)
#         with open(output_file, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.DictWriter(f, fieldnames=['village_name', 'district', 'state', 'irrigation_type', 'distance_to_town', 'electricity', 'school', 'hospital'])
#             writer.writeheader()
#             writer.writerows(sample_villages)
#         return True
#     except Exception as e:
#         logger.error(f"Village amenities creation failed: {e}")
#         return False


# def main():
#     parser = argparse.ArgumentParser(description='URE MVP Dataset Download Script')
#     parser.add_argument('--verify-only', action='store_true', help='Only verify datasets')
#     args = parser.parse_args()

#     if args.verify_only:
#         logger.info("=" * 60)
#         logger.info(f"VERIFYING PROJECT DATA AT: {BASE_DIR}")
#         logger.info("=" * 60)
#         paths = [PLANTVILLAGE_DIR, AGMARKNET_FILE, SCHEMES_DIR, VILLAGE_FILE]
#         for p in paths:
#             exists = Path(p).exists()
#             status = "✓" if exists else "✗"
#             logger.info(f"{status} {p}")
#         return

#     # Start the download and creation process
#     success_pv = download_plantvillage_kaggle(PLANTVILLAGE_DIR)
#     success_ag = create_sample_agmarknet_data(AGMARKNET_FILE)
#     success_pm = create_sample_pmkisan_docs(SCHEMES_DIR)
#     success_vl = create_sample_village_amenities(VILLAGE_FILE)

#     logger.info("\n" + "=" * 60)
#     logger.info("SUMMARY")
#     logger.info("=" * 60)
#     logger.info(f"PlantVillage: {'SUCCESS' if success_pv else 'FAILED'}")
#     logger.info(f"Agmarknet:    {'SUCCESS' if success_ag else 'FAILED'}")
#     logger.info(f"Schemes:      {'SUCCESS' if success_pm else 'FAILED'}")
#     logger.info(f"Village:      {'SUCCESS' if success_vl else 'FAILED'}")
#     logger.info("=" * 60)
#     logger.info(f"Total workspace: {BASE_DIR}")


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
# """
# URE Dataset Downloader with Safety Unzip
# Target Path: D:\Learning\Assembler_URE_Rural
# """

# import os
# import logging
# import shutil
# import zipfile
# import kagglehub
# from pathlib import Path

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# BASE_DATA_DIR = r"D:\Learning\Assembler_URE_Rural\data"

# DATASETS = {
#     "Agri-Expert (Diseases)": {
#         "handle": "vipoooool/new-plant-diseases-dataset",
#         "path": os.path.join(BASE_DATA_DIR, "plantvillage")
#     },
#     "Market-Expert (Prices)": {
#         "handle": "arjunyadav99/indian-agricultural-mandi-prices-20232025",
#         "path": os.path.join(BASE_DATA_DIR, "mandi_prices")
#     },
#     "Eco-Resource (Geospatial)": {
#         "handle": "radiantearth/agrifieldnet-competition-dataset-pi-dist",
#         "path": os.path.join(BASE_DATA_DIR, "agrifieldnet")
#     }
# }

# def unzip_if_needed(target_dir):
#     """Checks for zip files in a folder and extracts them if found."""
#     path = Path(target_dir)
#     for item in path.glob("*.zip"):
#         logger.info(f"--- Unzipping: {item.name} ---")
#         try:
#             with zipfile.ZipFile(item, 'r') as zip_ref:
#                 zip_ref.extractall(path)
#             # Optional: Remove zip after extraction to save space on D: drive
#             os.remove(item)
#             logger.info(f"   ✓ Extracted and removed zip.")
#         except Exception as e:
#             logger.error(f"   ✗ Unzip failed for {item.name}: {e}")

# def download_and_sync():
#     logger.info("=" * 60)
#     logger.info(f"STARTING DOWNLOAD & EXTRACT TO: {BASE_DATA_DIR}")
#     logger.info("=" * 60)

#     for agent_name, info in DATASETS.items():
#         try:
#             logger.info(f"\n[+] Processing {agent_name}...")
            
#             # kagglehub typically returns an already unzipped folder path
#             cache_path = kagglehub.dataset_download(info["handle"])
            
#             dest_path = Path(info["path"])
#             dest_path.mkdir(parents=True, exist_ok=True)
            
#             if not any(dest_path.iterdir()):
#                 logger.info(f"   Syncing data to: {info['path']}")
#                 shutil.copytree(cache_path, dest_path, dirs_exist_ok=True)
                
#                 # Safety step: unzip any archives that might have slipped through
#                 unzip_if_needed(info["path"])
                
#                 logger.info(f"   ✓ {agent_name} ready.")
#             else:
#                 logger.info(f"   ✓ {agent_name} already exists. Skipping.")
                
#         except Exception as e:
#             logger.error(f"   ✗ Failed to process {agent_name}: {e}")

# if __name__ == "__main__":
#     download_and_sync()
#!/usr/bin/env python3
"""
URE Dataset & Official Form Downloader
Target Path: D:\Learning\Assembler_URE_Rural
Includes: Kaggle Datasets (CV, Prices, Geospatial) and Official Govt Forms (PDFs)
"""

import os
import logging
import shutil
import zipfile
import requests
import kagglehub
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- WINDOWS PATH CONFIGURATION ---
BASE_DATA_DIR = r"D:\Learning\Assembler_URE_Rural\data"
SCHEME_DOCS_DIR = os.path.join(BASE_DATA_DIR, "government_schemes")

# Kaggle Dataset Configuration
DATASETS = {
    "Agri-Expert (Diseases)": {
        "handle": "vipoooool/new-plant-diseases-dataset",
        "path": os.path.join(BASE_DATA_DIR, "plantvillage")
    },
    "Market-Expert (Prices)": {
        "handle": "arjunyadav99/indian-agricultural-mandi-prices-20232025",
        "path": os.path.join(BASE_DATA_DIR, "mandi_prices")
    },
    "Eco-Resource (Geospatial)": {
        "handle": "radiantearth/agrifieldnet-competition-dataset-pi-dist",
        "path": os.path.join(BASE_DATA_DIR, "agrifieldnet")
    }
}

# Official Government Forms and Guidelines for RAG Grounding
OFFICIAL_FORMS = {
    "PM_Kisan_Registration_Form": "https://pmkisan.gov.in/Documents/NewFarmerRegistration.pdf",
    "PMFBY_Scheme_Guidelines": "https://pmfby.gov.in/pdf/Revised_Operational_Guidelines.pdf",
    "PKVY_Organic_Farming_Guidelines": "https://agriwelfare.gov.in/Documents/Revised_PKVY_Guidelines_022-2023_PUB_1FEB2022.pdf",
    "PMKSY_Irrigation_Manual": "https://darpg.gov.in/sites/default/files/Pradhan%20Mantri%20Krishi%20Sichai%20Yojana.pdf",
    "eNAM_Stakeholder_Guideline": "https://dmi.gov.in/Documents/guideline_final_merged.pdf"
}

def unzip_if_needed(target_dir):
    """Checks for zip files in a folder and extracts them if found."""
    path = Path(target_dir)
    for item in path.glob("*.zip"):
        logger.info(f"--- Unzipping: {item.name} ---")
        try:
            with zipfile.ZipFile(item, 'r') as zip_ref:
                zip_ref.extractall(path)
            os.remove(item)
            logger.info(f"   ✓ Extracted and removed zip.")
        except Exception as e:
            logger.error(f"   ✗ Unzip failed for {item.name}: {e}")

def download_and_sync_kaggle():
    """Handles Kaggle downloads and syncing to D: drive."""
    logger.info("=" * 60)
    logger.info("STARTING KAGGLE DATASET DOWNLOADS")
    logger.info("=" * 60)

    for agent_name, info in DATASETS.items():
        try:
            logger.info(f"\n[+] Processing {agent_name}...")
            cache_path = kagglehub.dataset_download(info["handle"])
            
            dest_path = Path(info["path"])
            dest_path.mkdir(parents=True, exist_ok=True)
            
            if not any(dest_path.iterdir()):
                logger.info(f"   Syncing data to: {info['path']}")
                shutil.copytree(cache_path, dest_path, dirs_exist_ok=True)
                unzip_if_needed(info["path"])
                logger.info(f"   ✓ {agent_name} ready.")
            else:
                logger.info(f"   ✓ {agent_name} already exists. Skipping.")
        except Exception as e:
            logger.error(f"   ✗ Failed to process {agent_name}: {e}")

def download_official_forms(target_dir):
    """Downloads official government PDF forms for RAG grounding."""
    dest = Path(target_dir)
    dest.mkdir(parents=True, exist_ok=True)
    
    logger.info("\n" + "=" * 60)
    logger.info("DOWNLOADING OFFICIAL SCHEME FORMS & GUIDELINES")
    logger.info("=" * 60)
    
    for name, url in OFFICIAL_FORMS.items():
        try:
            logger.info(f"[+] Downloading: {name}...")
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                file_path = dest / f"{name}.pdf"
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"   ✓ Saved: {file_path}")
            else:
                logger.warning(f"   ! Could not download {name} (Status: {response.status_code})")
        except Exception as e:
            logger.error(f"   ✗ Error downloading {name}: {e}")

if __name__ == "__main__":
    # Ensure prerequisites: pip install kagglehub requests
    
    # 1. Handle large Kaggle datasets
    download_and_sync_kaggle()
    
    # 2. Handle official Government PDFs
    download_official_forms(SCHEME_DOCS_DIR)

    logger.info("\n" + "=" * 60)
    logger.info("URE WORKSPACE SETUP COMPLETE")
    logger.info(f"Target Directory: {BASE_DATA_DIR}")
    logger.info("=" * 60)