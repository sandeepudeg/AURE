#!/usr/bin/env python3
"""
Feedback Management Script for URE MVP

This script manages feedback collection and reporting:
1. View feedback
2. Generate reports
3. Export feedback data
4. Analyze trends

Usage:
    python scripts/manage_feedback.py --report weekly
    python scripts/manage_feedback.py --report monthly
    python scripts/manage_feedback.py --export feedback.csv --days 30
    python scripts/manage_feedback.py --list --days 7
    python scripts/manage_feedback.py --user user-123
"""

import argparse
import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.feedback import FeedbackCollector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_weekly_report(report: dict):
    """Print weekly report in formatted output"""
    print("\n" + "=" * 80)
    print("WEEKLY FEEDBACK REPORT")
    print("=" * 80)
    print(f"\nPeriod: {report['period']}")
    print(f"Total Feedback: {report['total_feedback']}")
    
    print(f"\n--- Ratings ---")
    print(f"Thumbs Up: {report['ratings']['thumbs_up']}")
    print(f"Thumbs Down: {report['ratings']['thumbs_down']}")
    if report['ratings']['stars']:
        print(f"Average Star Rating: {report['average_rating']:.2f}/5")
    print(f"Satisfaction Rate: {report['satisfaction_rate']:.1f}%")
    
    print(f"\n--- Sentiment Analysis ---")
    print(f"Positive: {report['sentiment']['positive']}")
    print(f"Negative: {report['sentiment']['negative']}")
    print(f"Neutral: {report['sentiment']['neutral']}")
    
    print(f"\n--- By Agent ---")
    for agent, count in sorted(report['by_agent'].items(), key=lambda x: x[1], reverse=True):
        print(f"{agent}: {count}")
        
    if report['top_positive_comments']:
        print(f"\n--- Top Positive Comments ---")
        for i, comment in enumerate(report['top_positive_comments'], 1):
            print(f"{i}. {comment}")
            
    if report['top_negative_comments']:
        print(f"\n--- Top Negative Comments ---")
        for i, comment in enumerate(report['top_negative_comments'], 1):
            print(f"{i}. {comment}")
            
    print("\n" + "=" * 80 + "\n")


def print_monthly_report(report: dict):
    """Print monthly report in formatted output"""
    print("\n" + "=" * 80)
    print("MONTHLY FEEDBACK REPORT")
    print("=" * 80)
    print(f"\nPeriod: {report['period']}")
    print(f"Total Feedback: {report['total_feedback']}")
    
    print(f"\n--- Weekly Trend ---")
    print(f"{'Week':<15} {'Total':<10} {'Thumbs Up':<12} {'Thumbs Down':<12} {'Satisfaction':<15}")
    print("-" * 80)
    for week in report['weekly_trend']:
        print(f"{week['week']:<15} {week['total']:<10} {week['thumbs_up']:<12} {week['thumbs_down']:<12} {week['satisfaction_rate']:.1f}%")
        
    print(f"\n--- Agent Performance ---")
    print(f"{'Agent':<25} {'Total':<10} {'Thumbs Up':<12} {'Thumbs Down':<12} {'Satisfaction':<15}")
    print("-" * 80)
    for agent, stats in sorted(report['agent_performance'].items(), key=lambda x: x[1]['satisfaction_rate'], reverse=True):
        print(f"{agent:<25} {stats['total']:<10} {stats['thumbs_up']:<12} {stats['thumbs_down']:<12} {stats['satisfaction_rate']:.1f}%")
        
    print(f"\n--- User Engagement ---")
    print(f"Total Users: {report['user_engagement']['total_users']}")
    print(f"Feedback per User: {report['user_engagement']['feedback_per_user']:.2f}")
    
    print("\n" + "=" * 80 + "\n")


def print_feedback_list(feedback_items: list):
    """Print feedback list in formatted output"""
    print(f"\nTotal Feedback: {len(feedback_items)}\n")
    print(f"{'Feedback ID':<40} {'User ID':<40} {'Rating':<15} {'Sentiment':<12} {'Date':<20}")
    print("-" * 130)
    
    for item in feedback_items:
        feedback_id = item.get('feedback_id', 'N/A')
        user_id = item.get('user_id', 'N/A')
        rating = item.get('rating', 'N/A')
        sentiment = item.get('sentiment', 'N/A')
        created_at = item.get('created_at', 'N/A')
        
        # Truncate IDs if too long
        if len(feedback_id) > 38:
            feedback_id = feedback_id[:35] + "..."
        if len(user_id) > 38:
            user_id = user_id[:35] + "..."
            
        print(f"{feedback_id:<40} {user_id:<40} {rating:<15} {sentiment:<12} {created_at:<20}")
        
        # Print comment if exists
        comment = item.get('comment')
        if comment:
            print(f"  Comment: {comment}")
            print()


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Feedback Management Script')
    
    # Report generation
    parser.add_argument('--report', choices=['weekly', 'monthly'], help='Generate report')
    
    # List feedback
    parser.add_argument('--list', action='store_true', help='List all feedback')
    parser.add_argument('--days', type=int, default=7, help='Number of days to look back (default: 7)')
    
    # User-specific feedback
    parser.add_argument('--user', help='Get feedback for specific user ID')
    
    # Export feedback
    parser.add_argument('--export', help='Export feedback to CSV file')
    
    # Get specific feedback
    parser.add_argument('--get', help='Get specific feedback by ID')
    
    args = parser.parse_args()
    
    # Initialize feedback collector
    collector = FeedbackCollector()
    
    # Handle different operations
    if args.report == 'weekly':
        # Generate weekly report
        report = collector.generate_weekly_report()
        print_weekly_report(report)
        
    elif args.report == 'monthly':
        # Generate monthly report
        report = collector.generate_monthly_report()
        print_monthly_report(report)
        
    elif args.list:
        # List all feedback
        feedback_items = collector.get_all_feedback(days=args.days)
        print_feedback_list(feedback_items)
        
    elif args.user:
        # Get user-specific feedback
        feedback_items = collector.get_user_feedback(args.user)
        print(f"\nFeedback for user: {args.user}\n")
        print_feedback_list(feedback_items)
        
    elif args.export:
        # Export feedback to CSV
        print(f"Exporting feedback to {args.export}...")
        collector.export_feedback_to_csv(args.export, days=args.days)
        print(f"Export complete!")
        
    elif args.get:
        # Get specific feedback
        feedback = collector.get_feedback(args.get)
        if feedback:
            print(json.dumps(feedback, indent=2, default=str))
        else:
            print(f"Feedback not found: {args.get}")
            
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
