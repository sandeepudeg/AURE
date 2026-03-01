#!/usr/bin/env python3
"""Check ingestion job error details"""

import boto3

client = boto3.client('bedrock-agent', region_name='us-east-1')
response = client.get_ingestion_job(
    knowledgeBaseId='7XROZ6PZIF',
    dataSourceId='D0598AKIM4',
    ingestionJobId='VUDAMUZUJR'
)

job = response['ingestionJob']
print(f"Status: {job['status']}")

if 'failureReasons' in job and job['failureReasons']:
    print(f"\nFailure Reasons:")
    for reason in job['failureReasons']:
        print(f"  - {reason}")

print(f"\nStatistics:")
if 'statistics' in job:
    stats = job['statistics']
    print(f"  Documents scanned: {stats.get('numberOfDocumentsScanned', 0)}")
    print(f"  Documents indexed: {stats.get('numberOfNewDocumentsIndexed', 0)}")
    print(f"  Documents modified: {stats.get('numberOfModifiedDocumentsIndexed', 0)}")
    print(f"  Documents deleted: {stats.get('numberOfDocumentsDeleted', 0)}")
    print(f"  Documents failed: {stats.get('numberOfDocumentsFailed', 0)}")

