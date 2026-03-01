#!/usr/bin/env python3
"""
DynamoDB Loader Utility for URE MVP
----------------------------------
This script populates the 'Active Memory' of the URE agents.
It handles:
1. Village Amenities (Infrastructure grounding)
2. User Profiles (Personalization grounding)
3. Conversations (Chat history persistence)
"""

import boto3
import logging
import csv
import json
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from tqdm import tqdm

# Configure logging
logger = logging.getLogger(__name__)

class DynamoDBLoader:
    """Load data into DynamoDB tables for URE MVP with visual progress tracking."""
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize DynamoDB Loader using the Boto3 Resource API for easier item handling.
        """
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.client = boto3.client('dynamodb', region_name=region)
        
        logger.info(f"DynamoDB Loader initialized for region: {region}")
    
    def create_conversations_table(self, table_name: str = 'ure-conversations'):
        """Creates table for storing multi-turn chat history for the Supervisor agent."""
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'} # Partition Key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'URE-MVP'},
                    {'Key': 'Purpose', 'Value': 'ChatHistory'}
                ]
            )
            logger.info(f"Creating table: {table_name}...")
            table.wait_until_exists()
            logger.info(f"✓ Table {table_name} created successfully")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table {table_name} already exists")
                return True
            logger.error(f"Failed to create table: {e}")
            return False

    def create_village_amenities_table(self, table_name: str = 'ure-village-amenities'):
        """Creates table for regional grounding (Infrastructure data)."""
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'village_name', 'KeyType': 'HASH'}, # Partition Key
                    {'AttributeName': 'district', 'KeyType': 'RANGE'}    # Sort Key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'village_name', 'AttributeType': 'S'},
                    {'AttributeName': 'district', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'URE-MVP'},
                    {'Key': 'Purpose', 'Value': 'VillageGrounding'}
                ]
            )
            table.wait_until_exists()
            logger.info(f"✓ Table {table_name} created successfully")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table {table_name} already exists")
                return True
            return False

    def create_user_profiles_table(self, table_name: str = 'ure-user-profiles'):
        """Creates table to help agents identify farmer-specific details (land size, crops)."""
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'URE-MVP'},
                    {'Key': 'Purpose', 'Value': 'UserContext'}
                ]
            )
            table.wait_until_exists()
            logger.info(f"✓ Table {table_name} created successfully")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table {table_name} already exists")
                return True
            return False

    def load_village_amenities_from_csv(
        self,
        csv_path: str,
        table_name: str = 'ure-village-amenities'
    ) -> dict:
        """
        Parses the village CSV and uploads it to DynamoDB with a progress bar.
        
        Args:
            csv_path: Local path on D: drive
        """
        stats = {'success': 0, 'failed': 0}
        table = self.dynamodb.Table(table_name)
        
        try:
            # Count rows for the progress bar
            with open(csv_path, 'r', encoding='utf-8') as f:
                total_rows = sum(1 for _ in f) - 1

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Use tqdm to show ingestion progress in the terminal
                for row in tqdm(reader, total=total_rows, desc="Ingesting Villages"):
                    try:
                        # Map CSV types to DynamoDB compatible types (booleans/ints)
                        item = {
                            'village_name': row['village_name'],
                            'district': row['district'],
                            'state': row['state'],
                            'irrigation_type': row.get('irrigation_type', 'Unknown'),
                            'distance_to_town': int(row.get('distance_to_town', 0)),
                            'electricity': row.get('electricity', 'No') == 'Yes',
                            'school': row.get('school', 'No') == 'Yes',
                            'hospital': row.get('hospital', 'No') == 'Yes'
                        }
                        table.put_item(Item=item)
                        stats['success'] += 1
                    except Exception as e:
                        logger.error(f"Row failed: {row.get('village_name')} - {e}")
                        stats['failed'] += 1
            
            return stats
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return stats

    def load_sample_village_data(self, table_name: str = 'ure-village-amenities'):
        """Injects sample village data for testing regional grounding."""
        table = self.dynamodb.Table(table_name)
        
        sample_villages = [
            {
                'village_name': 'Nashik',
                'district': 'Nashik',
                'state': 'Maharashtra',
                'irrigation_type': 'Canal',
                'distance_to_town': 0,
                'electricity': True,
                'school': True,
                'hospital': True
            },
            {
                'village_name': 'Pimpalgaon',
                'district': 'Nashik',
                'state': 'Maharashtra',
                'irrigation_type': 'Well',
                'distance_to_town': 12,
                'electricity': True,
                'school': True,
                'hospital': False
            },
            {
                'village_name': 'Satana',
                'district': 'Nashik',
                'state': 'Maharashtra',
                'irrigation_type': 'Drip',
                'distance_to_town': 25,
                'electricity': True,
                'school': True,
                'hospital': True
            }
        ]
        
        for village in sample_villages:
            table.put_item(Item=village)
            logger.info(f"✓ Loaded sample village: {village['village_name']}")
        
        logger.info(f"✓ Loaded {len(sample_villages)} sample villages")

    def load_sample_user_profile(self, table_name: str = 'ure-user-profiles'):
        """Injects a sample farmer profile to test personalized agent routing."""
        table = self.dynamodb.Table(table_name)
        
        sample_user = {
            'user_id': 'farmer_12345',
            'name': 'Rajesh Kumar',
            'farm_details': {
                'total_acres': 5,
                'crops': ['wheat', 'cotton'],
                'irrigation_type': 'canal'
            },
            'language_preference': 'marathi',
            'created_at': '2026-02-27T10:30:00Z'
        }
        
        table.put_item(Item=sample_user)
        logger.info(f"✓ Sample user '{sample_user['name']}' injected into profiles.")

if __name__ == "__main__":
    # Standing up the infrastructure
    logging.basicConfig(level=logging.INFO)
    loader = DynamoDBLoader()
    
    print("\nCreating DynamoDB tables in us-east-1...")
    loader.create_conversations_table()
    loader.create_village_amenities_table()
    loader.create_user_profiles_table()
    
    print("\nLoading sample data...")
    loader.load_sample_village_data()
    loader.load_sample_user_profile()
    
    print("\nDynamoDB Infrastructure Ready in us-east-1.")