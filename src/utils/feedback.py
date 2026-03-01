"""
Feedback Collection Module for URE MVP

This module handles:
1. In-app feedback collection (thumbs up/down + comments)
2. Feedback storage in DynamoDB
3. Sentiment analysis
4. Weekly/monthly reports generation
"""

import boto3
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_FEEDBACK_TABLE = os.getenv('DYNAMODB_FEEDBACK_TABLE', 'ure-feedback')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)


class FeedbackCollector:
    """Handles feedback collection and analysis"""
    
    def __init__(self):
        """Initialize feedback collector"""
        try:
            self.table = dynamodb.Table(DYNAMODB_FEEDBACK_TABLE)
        except Exception as e:
            logger.warning(f"Feedback table not found, will create on first use: {e}")
            self.table = None
            
    def _ensure_table_exists(self):
        """Create feedback table if it doesn't exist"""
        if self.table is not None:
            return
            
        try:
            # Create table
            table = dynamodb.create_table(
                TableName=DYNAMODB_FEEDBACK_TABLE,
                KeySchema=[
                    {'AttributeName': 'feedback_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'feedback_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'created_at', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'user_id-created_at-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            self.table = table
            logger.info(f"Created feedback table: {DYNAMODB_FEEDBACK_TABLE}")
            
        except Exception as e:
            logger.error(f"Failed to create feedback table: {e}")
            raise
            
    def collect_feedback(
        self,
        user_id: str,
        query_id: str,
        rating: str,
        comment: Optional[str] = None,
        query_text: Optional[str] = None,
        response_text: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Collect feedback from user
        
        Args:
            user_id: User ID
            query_id: Query/conversation ID
            rating: Rating (thumbs_up, thumbs_down, 1-5 stars)
            comment: Optional comment from user
            query_text: Original query text
            response_text: Response text
            agent_name: Agent that handled the query
            metadata: Additional metadata
            
        Returns:
            Dict containing feedback data
        """
        self._ensure_table_exists()
        
        # Generate feedback ID
        feedback_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare feedback item
        feedback = {
            'feedback_id': feedback_id,
            'user_id': user_id,
            'query_id': query_id,
            'rating': rating,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Add optional fields
        if comment:
            feedback['comment'] = comment
            feedback['sentiment'] = self._analyze_sentiment(comment)
        if query_text:
            feedback['query_text'] = query_text
        if response_text:
            feedback['response_text'] = response_text
        if agent_name:
            feedback['agent_name'] = agent_name
        if metadata:
            feedback['metadata'] = metadata
            
        # Store in DynamoDB
        try:
            self.table.put_item(Item=feedback)
            logger.info(f"Collected feedback: {feedback_id} (rating: {rating})")
            return feedback
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            raise
            
    def get_feedback(self, feedback_id: str) -> Optional[Dict]:
        """Get feedback by ID"""
        try:
            response = self.table.get_item(Key={'feedback_id': feedback_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get feedback: {e}")
            return None
            
    def get_user_feedback(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get feedback for a specific user"""
        try:
            response = self.table.query(
                IndexName='user_id-created_at-index',
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False,  # Sort by created_at descending
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get user feedback: {e}")
            return []
            
    def get_all_feedback(self, days: int = 7) -> List[Dict]:
        """Get all feedback from last N days"""
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.table.scan(
                FilterExpression='created_at >= :cutoff',
                ExpressionAttributeValues={':cutoff': cutoff_date}
            )
            
            feedback_items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    FilterExpression='created_at >= :cutoff',
                    ExpressionAttributeValues={':cutoff': cutoff_date},
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                feedback_items.extend(response.get('Items', []))
                
            return feedback_items
        except Exception as e:
            logger.error(f"Failed to get all feedback: {e}")
            return []
            
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of feedback comment
        
        Simple keyword-based sentiment analysis.
        In production, use AWS Comprehend for better accuracy.
        
        Returns:
            'positive', 'negative', or 'neutral'
        """
        # Positive keywords
        positive_keywords = [
            'good', 'great', 'excellent', 'helpful', 'useful', 'accurate',
            'thank', 'thanks', 'appreciate', 'love', 'perfect', 'amazing',
            'wonderful', 'fantastic', 'best', 'awesome', 'nice'
        ]
        
        # Negative keywords
        negative_keywords = [
            'bad', 'poor', 'wrong', 'incorrect', 'useless', 'unhelpful',
            'terrible', 'awful', 'worst', 'hate', 'disappointed', 'frustrat',
            'confus', 'error', 'fail', 'broken', 'slow', 'not working'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
            
    def generate_weekly_report(self) -> Dict:
        """Generate weekly feedback report"""
        feedback_items = self.get_all_feedback(days=7)
        
        report = {
            'period': 'Last 7 days',
            'total_feedback': len(feedback_items),
            'ratings': {
                'thumbs_up': 0,
                'thumbs_down': 0,
                'stars': []
            },
            'sentiment': {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            },
            'by_agent': {},
            'common_issues': [],
            'top_positive_comments': [],
            'top_negative_comments': [],
            'average_rating': 0.0,
            'satisfaction_rate': 0.0
        }
        
        # Analyze ratings
        for item in feedback_items:
            rating = item.get('rating', '')
            
            if rating == 'thumbs_up':
                report['ratings']['thumbs_up'] += 1
            elif rating == 'thumbs_down':
                report['ratings']['thumbs_down'] += 1
            elif rating.isdigit():
                report['ratings']['stars'].append(int(rating))
                
            # Analyze sentiment
            sentiment = item.get('sentiment', 'neutral')
            report['sentiment'][sentiment] += 1
            
            # Count by agent
            agent = item.get('agent_name', 'Unknown')
            report['by_agent'][agent] = report['by_agent'].get(agent, 0) + 1
            
            # Collect comments
            comment = item.get('comment')
            if comment:
                if sentiment == 'positive':
                    report['top_positive_comments'].append(comment)
                elif sentiment == 'negative':
                    report['top_negative_comments'].append(comment)
                    
        # Calculate average rating
        if report['ratings']['stars']:
            report['average_rating'] = sum(report['ratings']['stars']) / len(report['ratings']['stars'])
            
        # Calculate satisfaction rate
        total_ratings = report['ratings']['thumbs_up'] + report['ratings']['thumbs_down']
        if total_ratings > 0:
            report['satisfaction_rate'] = (report['ratings']['thumbs_up'] / total_ratings) * 100
            
        # Limit comments
        report['top_positive_comments'] = report['top_positive_comments'][:5]
        report['top_negative_comments'] = report['top_negative_comments'][:5]
        
        return report
        
    def generate_monthly_report(self) -> Dict:
        """Generate monthly feedback report"""
        feedback_items = self.get_all_feedback(days=30)
        
        report = {
            'period': 'Last 30 days',
            'total_feedback': len(feedback_items),
            'weekly_trend': [],
            'ratings_distribution': {},
            'sentiment_trend': [],
            'agent_performance': {},
            'user_engagement': {
                'total_users': 0,
                'feedback_per_user': 0.0
            },
            'roi_metrics': {
                'queries_with_feedback': 0,
                'feedback_rate': 0.0
            }
        }
        
        # Calculate weekly trend (4 weeks)
        for week in range(4):
            week_start = datetime.utcnow() - timedelta(days=(week + 1) * 7)
            week_end = datetime.utcnow() - timedelta(days=week * 7)
            
            week_feedback = [
                f for f in feedback_items
                if week_start.isoformat() <= f.get('created_at', '') < week_end.isoformat()
            ]
            
            thumbs_up = sum(1 for f in week_feedback if f.get('rating') == 'thumbs_up')
            thumbs_down = sum(1 for f in week_feedback if f.get('rating') == 'thumbs_down')
            
            report['weekly_trend'].append({
                'week': f"Week {4 - week}",
                'total': len(week_feedback),
                'thumbs_up': thumbs_up,
                'thumbs_down': thumbs_down,
                'satisfaction_rate': (thumbs_up / (thumbs_up + thumbs_down) * 100) if (thumbs_up + thumbs_down) > 0 else 0
            })
            
        # Agent performance
        for item in feedback_items:
            agent = item.get('agent_name', 'Unknown')
            if agent not in report['agent_performance']:
                report['agent_performance'][agent] = {
                    'total': 0,
                    'thumbs_up': 0,
                    'thumbs_down': 0,
                    'satisfaction_rate': 0.0
                }
                
            report['agent_performance'][agent]['total'] += 1
            
            if item.get('rating') == 'thumbs_up':
                report['agent_performance'][agent]['thumbs_up'] += 1
            elif item.get('rating') == 'thumbs_down':
                report['agent_performance'][agent]['thumbs_down'] += 1
                
        # Calculate satisfaction rates
        for agent, stats in report['agent_performance'].items():
            total = stats['thumbs_up'] + stats['thumbs_down']
            if total > 0:
                stats['satisfaction_rate'] = (stats['thumbs_up'] / total) * 100
                
        # User engagement
        unique_users = set(f.get('user_id') for f in feedback_items)
        report['user_engagement']['total_users'] = len(unique_users)
        if len(unique_users) > 0:
            report['user_engagement']['feedback_per_user'] = len(feedback_items) / len(unique_users)
            
        return report
        
    def export_feedback_to_csv(self, output_file: str, days: int = 30):
        """Export feedback to CSV file"""
        import csv
        
        feedback_items = self.get_all_feedback(days=days)
        
        if not feedback_items:
            logger.warning("No feedback to export")
            return
            
        # Define CSV columns
        columns = [
            'feedback_id', 'user_id', 'query_id', 'rating', 'sentiment',
            'comment', 'agent_name', 'created_at'
        ]
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for item in feedback_items:
                    row = {col: item.get(col, '') for col in columns}
                    writer.writerow(row)
                    
            logger.info(f"Exported {len(feedback_items)} feedback items to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export feedback: {e}")
            raise


# Convenience functions for Lambda integration
def collect_feedback_from_lambda(event: Dict) -> Dict:
    """
    Collect feedback from Lambda event
    
    Expected event format:
    {
        "user_id": "user-123",
        "query_id": "query-456",
        "rating": "thumbs_up",
        "comment": "Very helpful!",
        "query_text": "What disease is this?",
        "response_text": "This is tomato late blight...",
        "agent_name": "Agri-Expert"
    }
    """
    collector = FeedbackCollector()
    
    return collector.collect_feedback(
        user_id=event['user_id'],
        query_id=event['query_id'],
        rating=event['rating'],
        comment=event.get('comment'),
        query_text=event.get('query_text'),
        response_text=event.get('response_text'),
        agent_name=event.get('agent_name'),
        metadata=event.get('metadata')
    )


def get_weekly_report() -> Dict:
    """Get weekly feedback report"""
    collector = FeedbackCollector()
    return collector.generate_weekly_report()


def get_monthly_report() -> Dict:
    """Get monthly feedback report"""
    collector = FeedbackCollector()
    return collector.generate_monthly_report()
