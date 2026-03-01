#!/usr/bin/env python3
"""
Pilot Metrics Dashboard
View and analyze pilot program metrics from CloudWatch
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

def get_metric_statistics(
    cloudwatch,
    namespace: str,
    metric_name: str,
    hours: int = 24,
    dimensions: list = None
) -> Dict[str, Any]:
    """Get statistics for a metric"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        params = {
            'Namespace': namespace,
            'MetricName': metric_name,
            'StartTime': start_time,
            'EndTime': end_time,
            'Period': 3600,  # 1 hour
            'Statistics': ['Sum', 'Average', 'Maximum', 'Minimum']
        }
        
        if dimensions:
            params['Dimensions'] = dimensions
        
        response = cloudwatch.get_metric_statistics(**params)
        
        datapoints = response.get('Datapoints', [])
        
        if not datapoints:
            return {'total': 0, 'average': 0, 'max': 0, 'min': 0}
        
        total = sum(dp.get('Sum', 0) for dp in datapoints)
        averages = [dp.get('Average', 0) for dp in datapoints if 'Average' in dp]
        
        return {
            'total': total,
            'average': sum(averages) / len(averages) if averages else 0,
            'max': max((dp.get('Maximum', 0) for dp in datapoints), default=0),
            'min': min((dp.get('Minimum', 0) for dp in datapoints), default=0),
            'datapoints': len(datapoints)
        }
    
    except ClientError as e:
        print(f"Error getting metric {metric_name}: {e}")
        return {'total': 0, 'average': 0, 'max': 0, 'min': 0}


def display_pilot_summary(hours: int = 24):
    """Display pilot program summary"""
    cloudwatch = boto3.client('cloudwatch')
    namespace = 'URE/Pilot'
    
    print(f"\n{'='*60}")
    print(f"URE PILOT PROGRAM METRICS - Last {hours} Hours")
    print(f"{'='*60}\n")
    
    # Query Metrics
    print("📊 QUERY METRICS")
    print("-" * 60)
    
    total_queries = get_metric_statistics(cloudwatch, namespace, 'TotalQueries', hours)
    successful = get_metric_statistics(cloudwatch, namespace, 'SuccessfulQueries', hours)
    failed = get_metric_statistics(cloudwatch, namespace, 'FailedQueries', hours)
    
    print(f"Total Queries:      {int(total_queries['total']):,}")
    print(f"Successful:         {int(successful['total']):,}")
    print(f"Failed:             {int(failed['total']):,}")
    
    if total_queries['total'] > 0:
        success_rate = (successful['total'] / total_queries['total']) * 100
        print(f"Success Rate:       {success_rate:.1f}%")
    
    response_time = get_metric_statistics(cloudwatch, namespace, 'ResponseTime', hours)
    print(f"Avg Response Time:  {response_time['average']:.2f}s")
    print(f"Max Response Time:  {response_time['max']:.2f}s")
    
    # User Engagement
    print(f"\n👥 USER ENGAGEMENT")
    print("-" * 60)
    
    active_users = get_metric_statistics(cloudwatch, namespace, 'ActiveUsers', hours)
    image_queries = get_metric_statistics(cloudwatch, namespace, 'ImageQueries', hours)
    
    print(f"Active Users:       {int(active_users['total']):,}")
    print(f"Image Queries:      {int(image_queries['total']):,}")
    
    if total_queries['total'] > 0:
        image_rate = (image_queries['total'] / total_queries['total']) * 100
        print(f"Image Query Rate:   {image_rate:.1f}%")
    
    # Agent Performance
    print(f"\n🤖 AGENT PERFORMANCE")
    print("-" * 60)
    
    agents = ['supervisor', 'agri-expert', 'policy-navigator', 'resource-optimizer']
    for agent in agents:
        queries = get_metric_statistics(
            cloudwatch,
            namespace,
            'QueriesByAgent',
            hours,
            dimensions=[{'Name': 'Agent', 'Value': agent}]
        )
        if queries['total'] > 0:
            print(f"{agent:20s}: {int(queries['total']):,} queries")
    
    # Feedback Metrics
    print(f"\n💬 FEEDBACK METRICS")
    print("-" * 60)
    
    positive = get_metric_statistics(cloudwatch, namespace, 'PositiveFeedback', hours)
    negative = get_metric_statistics(cloudwatch, namespace, 'NegativeFeedback', hours)
    total_feedback = positive['total'] + negative['total']
    
    print(f"Total Feedback:     {int(total_feedback):,}")
    print(f"Positive:           {int(positive['total']):,}")
    print(f"Negative:           {int(negative['total']):,}")
    
    if total_feedback > 0:
        positive_rate = (positive['total'] / total_feedback) * 100
        print(f"Positive Rate:      {positive_rate:.1f}%")
    
    # Language Usage
    print(f"\n🌐 LANGUAGE USAGE")
    print("-" * 60)
    
    languages = ['en', 'hi', 'mr']
    for lang in languages:
        queries = get_metric_statistics(
            cloudwatch,
            namespace,
            'QueriesByLanguage',
            hours,
            dimensions=[{'Name': 'Language', 'Value': lang}]
        )
        if queries['total'] > 0:
            lang_name = {'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi'}[lang]
            print(f"{lang_name:15s}: {int(queries['total']):,} queries")
    
    # Error Metrics
    print(f"\n⚠️  ERROR METRICS")
    print("-" * 60)
    
    total_errors = get_metric_statistics(cloudwatch, namespace, 'TotalErrors', hours)
    guardrails_actions = get_metric_statistics(cloudwatch, namespace, 'GuardrailsActions', hours)
    
    print(f"Total Errors:       {int(total_errors['total']):,}")
    print(f"Guardrails Actions: {int(guardrails_actions['total']):,}")
    
    # MCP Tool Usage
    print(f"\n🔧 MCP TOOL USAGE")
    print("-" * 60)
    
    mcp_calls = get_metric_statistics(cloudwatch, namespace, 'MCPToolCalls', hours)
    mcp_success = get_metric_statistics(cloudwatch, namespace, 'MCPToolSuccess', hours)
    
    print(f"Total MCP Calls:    {int(mcp_calls['total']):,}")
    print(f"Successful:         {int(mcp_success['total']):,}")
    
    if mcp_calls['total'] > 0:
        mcp_success_rate = (mcp_success['total'] / mcp_calls['total']) * 100
        print(f"Success Rate:       {mcp_success_rate:.1f}%")
    
    print(f"\n{'='*60}\n")


def display_agent_breakdown(hours: int = 24):
    """Display detailed agent breakdown"""
    cloudwatch = boto3.client('cloudwatch')
    namespace = 'URE/Pilot'
    
    print(f"\n{'='*60}")
    print(f"AGENT PERFORMANCE BREAKDOWN - Last {hours} Hours")
    print(f"{'='*60}\n")
    
    agents = ['supervisor', 'agri-expert', 'policy-navigator', 'resource-optimizer']
    
    for agent in agents:
        print(f"\n🤖 {agent.upper()}")
        print("-" * 60)
        
        # Queries
        queries = get_metric_statistics(
            cloudwatch,
            namespace,
            'QueriesByAgent',
            hours,
            dimensions=[{'Name': 'Agent', 'Value': agent}]
        )
        
        # Response time
        response_time = get_metric_statistics(
            cloudwatch,
            namespace,
            'ResponseTimeByAgent',
            hours,
            dimensions=[{'Name': 'Agent', 'Value': agent}]
        )
        
        # Feedback
        positive = get_metric_statistics(
            cloudwatch,
            namespace,
            'PositiveFeedbackByAgent',
            hours,
            dimensions=[{'Name': 'Agent', 'Value': agent}]
        )
        
        negative = get_metric_statistics(
            cloudwatch,
            namespace,
            'NegativeFeedbackByAgent',
            hours,
            dimensions=[{'Name': 'Agent', 'Value': agent}]
        )
        
        print(f"Queries:            {int(queries['total']):,}")
        print(f"Avg Response Time:  {response_time['average']:.2f}s")
        print(f"Positive Feedback:  {int(positive['total']):,}")
        print(f"Negative Feedback:  {int(negative['total']):,}")
        
        total_feedback = positive['total'] + negative['total']
        if total_feedback > 0:
            satisfaction = (positive['total'] / total_feedback) * 100
            print(f"Satisfaction Rate:  {satisfaction:.1f}%")


def export_metrics_json(hours: int = 24, output_file: str = 'pilot_metrics.json'):
    """Export metrics to JSON file"""
    cloudwatch = boto3.client('cloudwatch')
    namespace = 'URE/Pilot'
    
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'period_hours': hours,
        'queries': {},
        'users': {},
        'agents': {},
        'feedback': {},
        'errors': {},
        'mcp': {}
    }
    
    # Query metrics
    metrics['queries']['total'] = get_metric_statistics(cloudwatch, namespace, 'TotalQueries', hours)
    metrics['queries']['successful'] = get_metric_statistics(cloudwatch, namespace, 'SuccessfulQueries', hours)
    metrics['queries']['failed'] = get_metric_statistics(cloudwatch, namespace, 'FailedQueries', hours)
    metrics['queries']['response_time'] = get_metric_statistics(cloudwatch, namespace, 'ResponseTime', hours)
    
    # User metrics
    metrics['users']['active'] = get_metric_statistics(cloudwatch, namespace, 'ActiveUsers', hours)
    metrics['users']['image_queries'] = get_metric_statistics(cloudwatch, namespace, 'ImageQueries', hours)
    
    # Agent metrics
    agents = ['supervisor', 'agri-expert', 'policy-navigator', 'resource-optimizer']
    for agent in agents:
        metrics['agents'][agent] = get_metric_statistics(
            cloudwatch,
            namespace,
            'QueriesByAgent',
            hours,
            dimensions=[{'Name': 'Agent', 'Value': agent}]
        )
    
    # Feedback metrics
    metrics['feedback']['positive'] = get_metric_statistics(cloudwatch, namespace, 'PositiveFeedback', hours)
    metrics['feedback']['negative'] = get_metric_statistics(cloudwatch, namespace, 'NegativeFeedback', hours)
    
    # Error metrics
    metrics['errors']['total'] = get_metric_statistics(cloudwatch, namespace, 'TotalErrors', hours)
    metrics['errors']['guardrails'] = get_metric_statistics(cloudwatch, namespace, 'GuardrailsActions', hours)
    
    # MCP metrics
    metrics['mcp']['total_calls'] = get_metric_statistics(cloudwatch, namespace, 'MCPToolCalls', hours)
    metrics['mcp']['successful'] = get_metric_statistics(cloudwatch, namespace, 'MCPToolSuccess', hours)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Metrics exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='URE Pilot Metrics Dashboard')
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Number of hours to look back (default: 24)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Display pilot summary'
    )
    parser.add_argument(
        '--agents',
        action='store_true',
        help='Display agent breakdown'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Export metrics to JSON file'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Display all reports'
    )
    
    args = parser.parse_args()
    
    # Default to summary if no options specified
    if not (args.summary or args.agents or args.export or args.all):
        args.summary = True
    
    try:
        if args.all or args.summary:
            display_pilot_summary(args.hours)
        
        if args.all or args.agents:
            display_agent_breakdown(args.hours)
        
        if args.export:
            export_metrics_json(args.hours, args.export)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
