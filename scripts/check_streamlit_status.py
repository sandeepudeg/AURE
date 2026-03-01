#!/usr/bin/env python3
"""
Check Streamlit App Runner deployment status
"""

import boto3
import time
import sys

SERVICE_ARN = "arn:aws:apprunner:us-east-1:188238313375:service/ure-streamlit-service/1f2722d2ea8c4b60ad6068cc1ea6d36f"
REGION = "us-east-1"

apprunner = boto3.client('apprunner', region_name=REGION)

print("Checking App Runner service status...\n")

try:
    service = apprunner.describe_service(ServiceArn=SERVICE_ARN)
    
    status = service['Service']['Status']
    service_url = service['Service']['ServiceUrl']
    
    print(f"Service Status: {status}")
    print(f"Service URL: https://{service_url}")
    
    if status == "RUNNING":
        print("\n✓ Service is RUNNING")
        print(f"\nAccess your app at: https://{service_url}")
        
        # Check recent operations
        print("\nRecent Operations:")
        operations = apprunner.list_operations(ServiceArn=SERVICE_ARN, MaxResults=5)
        
        for op in operations['OperationSummaryList']:
            op_type = op['Type']
            op_status = op['Status']
            started = op['StartedAt']
            print(f"  - {op_type}: {op_status} (Started: {started})")
    
    elif status == "OPERATION_IN_PROGRESS":
        print("\n⏳ Deployment in progress...")
        print("This typically takes 2-4 minutes.")
        print("\nWaiting for deployment to complete...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(10)
            attempt += 1
            
            service = apprunner.describe_service(ServiceArn=SERVICE_ARN)
            status = service['Service']['Status']
            
            print(f"  Attempt {attempt}/{max_attempts} - Status: {status}")
            
            if status == "RUNNING":
                print(f"\n✓ Deployment complete!")
                print(f"Access your app at: https://{service_url}")
                break
            elif status in ['CREATE_FAILED', 'UPDATE_FAILED']:
                print(f"\n✗ Deployment failed: {status}")
                sys.exit(1)
        
        if attempt >= max_attempts:
            print("\n⚠ Deployment is taking longer than expected.")
            print("Check AWS Console for details.")
    
    else:
        print(f"\n⚠ Unexpected status: {status}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
