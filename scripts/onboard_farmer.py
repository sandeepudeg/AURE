#!/usr/bin/env python3
"""
Farmer Onboarding Script for URE MVP

This script onboards farmers to the URE system by:
1. Creating user profiles in DynamoDB
2. Sending welcome messages
3. Tracking onboarding status
4. Generating onboarding reports

Usage:
    python scripts/onboard_farmer.py --name "Ramesh Kumar" --village "Nashik" --phone "+91-9876543210" --language "hi"
    python scripts/onboard_farmer.py --batch farmers.csv
    python scripts/onboard_farmer.py --list
    python scripts/onboard_farmer.py --report
"""

import argparse
import boto3
import csv
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_USER_PROFILES_TABLE = os.getenv('DYNAMODB_USER_PROFILES_TABLE', 'ure-user-profiles')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
user_profiles_table = dynamodb.Table(DYNAMODB_USER_PROFILES_TABLE)


class FarmerOnboarding:
    """Handles farmer onboarding operations"""
    
    def __init__(self):
        self.table = user_profiles_table
        
    def create_user_profile(
        self,
        name: str,
        village: str,
        phone: str,
        language: str = 'en',
        district: str = 'Nashik',
        state: str = 'Maharashtra',
        land_size_acres: Optional[float] = None,
        crops: Optional[List[str]] = None,
        email: Optional[str] = None
    ) -> Dict:
        """
        Create a new user profile in DynamoDB
        
        Args:
            name: Farmer's full name
            village: Village name
            phone: Phone number (format: +91-XXXXXXXXXX)
            language: Preferred language (en, hi, mr)
            district: District name
            state: State name
            land_size_acres: Land size in acres (optional)
            crops: List of crops grown (optional)
            email: Email address (optional)
            
        Returns:
            Dict containing user profile data
        """
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare user profile
        user_profile = {
            'user_id': user_id,
            'name': name,
            'village': village,
            'district': district,
            'state': state,
            'phone': phone,
            'language': language,
            'created_at': timestamp,
            'updated_at': timestamp,
            'onboarding_status': 'completed',
            'onboarding_date': timestamp,
            'active': True
        }
        
        # Add optional fields
        if land_size_acres:
            user_profile['land_size_acres'] = land_size_acres
        if crops:
            user_profile['crops'] = crops
        if email:
            user_profile['email'] = email
            
        # Store in DynamoDB
        try:
            self.table.put_item(Item=user_profile)
            logger.info(f"Created user profile for {name} (ID: {user_id})")
            return user_profile
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            raise
            
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID"""
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
            
    def list_all_users(self) -> List[Dict]:
        """List all user profiles"""
        try:
            response = self.table.scan()
            users = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                users.extend(response.get('Items', []))
                
            return users
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []
            
    def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """Update user profile"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Build update expression
            update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
            expr_attr_names = {f"#{k}": k for k in updates.keys()}
            expr_attr_values = {f":{k}": v for k, v in updates.items()}
            
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            logger.info(f"Updated user profile: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False
            
    def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile (soft delete - mark as inactive)"""
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET active = :active, updated_at = :updated_at",
                ExpressionAttributeValues={
                    ':active': False,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Deactivated user profile: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user profile: {e}")
            return False
            
    def batch_onboard_from_csv(self, csv_file: str) -> Dict:
        """
        Batch onboard farmers from CSV file
        
        CSV format:
        name,village,phone,language,district,state,land_size_acres,crops,email
        
        Returns:
            Dict with success/failure counts
        """
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Parse crops (comma-separated)
                        crops = row.get('crops', '').split(',') if row.get('crops') else None
                        crops = [c.strip() for c in crops] if crops else None
                        
                        # Parse land size
                        land_size = float(row.get('land_size_acres')) if row.get('land_size_acres') else None
                        
                        # Create user profile
                        self.create_user_profile(
                            name=row['name'],
                            village=row['village'],
                            phone=row['phone'],
                            language=row.get('language', 'en'),
                            district=row.get('district', 'Nashik'),
                            state=row.get('state', 'Maharashtra'),
                            land_size_acres=land_size,
                            crops=crops,
                            email=row.get('email')
                        )
                        results['success'] += 1
                        
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append({
                            'name': row.get('name', 'Unknown'),
                            'error': str(e)
                        })
                        logger.error(f"Failed to onboard {row.get('name')}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            raise
            
        return results
        
    def generate_onboarding_report(self) -> Dict:
        """Generate onboarding statistics report"""
        users = self.list_all_users()
        
        report = {
            'total_users': len(users),
            'active_users': sum(1 for u in users if u.get('active', True)),
            'inactive_users': sum(1 for u in users if not u.get('active', True)),
            'by_language': {},
            'by_district': {},
            'by_village': {},
            'recent_onboardings': []
        }
        
        # Count by language
        for user in users:
            lang = user.get('language', 'en')
            report['by_language'][lang] = report['by_language'].get(lang, 0) + 1
            
        # Count by district
        for user in users:
            district = user.get('district', 'Unknown')
            report['by_district'][district] = report['by_district'].get(district, 0) + 1
            
        # Count by village
        for user in users:
            village = user.get('village', 'Unknown')
            report['by_village'][village] = report['by_village'].get(village, 0) + 1
            
        # Get recent onboardings (last 7 days)
        from datetime import timedelta
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        for user in users:
            if user.get('onboarding_date', '') >= seven_days_ago:
                report['recent_onboardings'].append({
                    'name': user.get('name'),
                    'village': user.get('village'),
                    'date': user.get('onboarding_date')
                })
                
        return report
        
    def send_welcome_message(self, user_id: str) -> bool:
        """
        Send welcome message to farmer (placeholder)
        
        In production, this would:
        - Send WhatsApp message via Twilio/WhatsApp Business API
        - Send SMS via SNS
        - Send email via SES
        """
        user = self.get_user_profile(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            return False
            
        # Placeholder for welcome message
        welcome_messages = {
            'en': f"Welcome to Gram-Setu, {user['name']}! Get instant help with crop diseases, market prices, and government schemes. Visit: https://ure-mvp.streamlit.app",
            'hi': f"ग्राम-सेतू में आपका स्वागत है, {user['name']}! फसल रोग, बाजार भाव और सरकारी योजनाओं के लिए तुरंत मदद पाएं। यहां जाएं: https://ure-mvp.streamlit.app",
            'mr': f"ग्राम-सेतूमध्ये आपले स्वागत आहे, {user['name']}! पीक रोग, बाजार भाव आणि सरकारी योजनांसाठी तात्काळ मदत मिळवा। येथे जा: https://ure-mvp.streamlit.app"
        }
        
        message = welcome_messages.get(user.get('language', 'en'))
        
        logger.info(f"Welcome message for {user['name']}: {message}")
        
        # TODO: Implement actual message sending
        # - WhatsApp: Use Twilio API
        # - SMS: Use AWS SNS
        # - Email: Use AWS SES
        
        return True


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Farmer Onboarding Script')
    
    # Single farmer onboarding
    parser.add_argument('--name', help='Farmer name')
    parser.add_argument('--village', help='Village name')
    parser.add_argument('--phone', help='Phone number (+91-XXXXXXXXXX)')
    parser.add_argument('--language', default='en', choices=['en', 'hi', 'mr'], help='Language preference')
    parser.add_argument('--district', default='Nashik', help='District name')
    parser.add_argument('--state', default='Maharashtra', help='State name')
    parser.add_argument('--land-size', type=float, help='Land size in acres')
    parser.add_argument('--crops', help='Crops grown (comma-separated)')
    parser.add_argument('--email', help='Email address')
    
    # Batch onboarding
    parser.add_argument('--batch', help='CSV file for batch onboarding')
    
    # List and report
    parser.add_argument('--list', action='store_true', help='List all users')
    parser.add_argument('--report', action='store_true', help='Generate onboarding report')
    
    # User management
    parser.add_argument('--get', help='Get user profile by ID')
    parser.add_argument('--delete', help='Delete user profile by ID')
    
    args = parser.parse_args()
    
    # Initialize onboarding handler
    onboarding = FarmerOnboarding()
    
    # Handle different operations
    if args.list:
        # List all users
        users = onboarding.list_all_users()
        print(f"\nTotal users: {len(users)}\n")
        print(f"{'User ID':<40} {'Name':<25} {'Village':<20} {'Language':<10} {'Status':<10}")
        print("-" * 110)
        for user in users:
            status = 'Active' if user.get('active', True) else 'Inactive'
            print(f"{user['user_id']:<40} {user['name']:<25} {user['village']:<20} {user['language']:<10} {status:<10}")
            
    elif args.report:
        # Generate report
        report = onboarding.generate_onboarding_report()
        print("\n=== Onboarding Report ===\n")
        print(f"Total Users: {report['total_users']}")
        print(f"Active Users: {report['active_users']}")
        print(f"Inactive Users: {report['inactive_users']}")
        print(f"\nBy Language:")
        for lang, count in report['by_language'].items():
            print(f"  {lang}: {count}")
        print(f"\nBy District:")
        for district, count in report['by_district'].items():
            print(f"  {district}: {count}")
        print(f"\nBy Village:")
        for village, count in sorted(report['by_village'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {village}: {count}")
        print(f"\nRecent Onboardings (Last 7 days): {len(report['recent_onboardings'])}")
        
    elif args.get:
        # Get user profile
        user = onboarding.get_user_profile(args.get)
        if user:
            print(json.dumps(user, indent=2, default=str))
        else:
            print(f"User not found: {args.get}")
            
    elif args.delete:
        # Delete user profile
        if onboarding.delete_user_profile(args.delete):
            print(f"User deactivated: {args.delete}")
        else:
            print(f"Failed to deactivate user: {args.delete}")
            
    elif args.batch:
        # Batch onboarding
        print(f"Starting batch onboarding from {args.batch}...")
        results = onboarding.batch_onboard_from_csv(args.batch)
        print(f"\nBatch onboarding complete:")
        print(f"  Success: {results['success']}")
        print(f"  Failed: {results['failed']}")
        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error['name']}: {error['error']}")
                
    elif args.name and args.village and args.phone:
        # Single farmer onboarding
        crops = args.crops.split(',') if args.crops else None
        crops = [c.strip() for c in crops] if crops else None
        
        user_profile = onboarding.create_user_profile(
            name=args.name,
            village=args.village,
            phone=args.phone,
            language=args.language,
            district=args.district,
            state=args.state,
            land_size_acres=args.land_size,
            crops=crops,
            email=args.email
        )
        
        print(f"\nFarmer onboarded successfully!")
        print(f"User ID: {user_profile['user_id']}")
        print(f"Name: {user_profile['name']}")
        print(f"Village: {user_profile['village']}")
        print(f"Phone: {user_profile['phone']}")
        print(f"Language: {user_profile['language']}")
        
        # Send welcome message
        onboarding.send_welcome_message(user_profile['user_id'])
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
