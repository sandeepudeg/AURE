#!/usr/bin/env python3
"""
Pilot Metrics Module
Custom CloudWatch metrics for pilot program monitoring
"""

import boto3
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class PilotMetrics:
    """Custom CloudWatch metrics for pilot program tracking"""
    
    def __init__(self, namespace: str = "URE/Pilot"):
        """
        Initialize Pilot Metrics
        
        Args:
            namespace: CloudWatch namespace for custom metrics
        """
        self.cloudwatch = boto3.client('cloudwatch')
        self.namespace = namespace
        logger.info(f"Initialized PilotMetrics with namespace: {namespace}")
    
    def _put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'Count',
        dimensions: Optional[List[Dict[str, str]]] = None
    ):
        """
        Put a single metric to CloudWatch
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Metric unit (Count, Seconds, Percent, etc.)
            dimensions: List of dimension dicts with Name and Value keys
        """
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
            
            if dimensions:
                metric_data['Dimensions'] = dimensions
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            
            logger.debug(f"Put metric: {metric_name}={value} {unit}")
        
        except ClientError as e:
            logger.error(f"Failed to put metric {metric_name}: {e}")
    
    def track_query(
        self,
        user_id: str,
        agent_used: str,
        success: bool,
        response_time: float,
        language: str = 'en',
        has_image: bool = False
    ):
        """
        Track a query event with multiple metrics
        
        Args:
            user_id: Farmer user ID
            agent_used: Agent that handled the query
            success: Whether query was successful
            response_time: Response time in seconds
            language: Query language
            has_image: Whether query included an image
        """
        # Total queries
        self._put_metric('TotalQueries', 1.0)
        
        # Queries by agent
        self._put_metric(
            'QueriesByAgent',
            1.0,
            dimensions=[{'Name': 'Agent', 'Value': agent_used}]
        )
        
        # Queries by user
        self._put_metric(
            'QueriesByUser',
            1.0,
            dimensions=[{'Name': 'UserID', 'Value': user_id}]
        )
        
        # Success/failure
        if success:
            self._put_metric('SuccessfulQueries', 1.0)
        else:
            self._put_metric('FailedQueries', 1.0)
        
        # Response time
        self._put_metric('ResponseTime', response_time, unit='Seconds')
        self._put_metric(
            'ResponseTimeByAgent',
            response_time,
            unit='Seconds',
            dimensions=[{'Name': 'Agent', 'Value': agent_used}]
        )
        
        # Language usage
        self._put_metric(
            'QueriesByLanguage',
            1.0,
            dimensions=[{'Name': 'Language', 'Value': language}]
        )
        
        # Image queries
        if has_image:
            self._put_metric('ImageQueries', 1.0)
    
    def track_farmer_engagement(
        self,
        user_id: str,
        session_duration: float,
        queries_in_session: int
    ):
        """
        Track farmer engagement metrics
        
        Args:
            user_id: Farmer user ID
            session_duration: Session duration in seconds
            queries_in_session: Number of queries in this session
        """
        # Session duration
        self._put_metric(
            'SessionDuration',
            session_duration,
            unit='Seconds',
            dimensions=[{'Name': 'UserID', 'Value': user_id}]
        )
        
        # Queries per session
        self._put_metric(
            'QueriesPerSession',
            float(queries_in_session),
            dimensions=[{'Name': 'UserID', 'Value': user_id}]
        )
        
        # Active users
        self._put_metric('ActiveUsers', 1.0)
    
    def track_feedback(
        self,
        user_id: str,
        rating: str,
        agent_used: str
    ):
        """
        Track feedback metrics
        
        Args:
            user_id: Farmer user ID
            rating: Feedback rating (positive/negative)
            agent_used: Agent that generated the response
        """
        # Total feedback
        self._put_metric('TotalFeedback', 1.0)
        
        # Feedback by rating
        if rating == 'positive':
            self._put_metric('PositiveFeedback', 1.0)
            self._put_metric(
                'PositiveFeedbackByAgent',
                1.0,
                dimensions=[{'Name': 'Agent', 'Value': agent_used}]
            )
        else:
            self._put_metric('NegativeFeedback', 1.0)
            self._put_metric(
                'NegativeFeedbackByAgent',
                1.0,
                dimensions=[{'Name': 'Agent', 'Value': agent_used}]
            )
        
        # Feedback by user
        self._put_metric(
            'FeedbackByUser',
            1.0,
            dimensions=[{'Name': 'UserID', 'Value': user_id}]
        )
    
    def track_agent_performance(
        self,
        agent_name: str,
        accuracy: float,
        confidence: float
    ):
        """
        Track agent performance metrics
        
        Args:
            agent_name: Name of the agent
            accuracy: Accuracy score (0-100)
            confidence: Confidence score (0-100)
        """
        # Agent accuracy
        self._put_metric(
            'AgentAccuracy',
            accuracy,
            unit='Percent',
            dimensions=[{'Name': 'Agent', 'Value': agent_name}]
        )
        
        # Agent confidence
        self._put_metric(
            'AgentConfidence',
            confidence,
            unit='Percent',
            dimensions=[{'Name': 'Agent', 'Value': agent_name}]
        )
    
    def track_error(
        self,
        error_type: str,
        agent_used: str,
        user_id: Optional[str] = None
    ):
        """
        Track error metrics
        
        Args:
            error_type: Type of error (guardrails_block, agent_error, etc.)
            agent_used: Agent that encountered the error
            user_id: Optional user ID
        """
        # Total errors
        self._put_metric('TotalErrors', 1.0)
        
        # Errors by type
        self._put_metric(
            'ErrorsByType',
            1.0,
            dimensions=[{'Name': 'ErrorType', 'Value': error_type}]
        )
        
        # Errors by agent
        self._put_metric(
            'ErrorsByAgent',
            1.0,
            dimensions=[{'Name': 'Agent', 'Value': agent_used}]
        )
        
        if user_id:
            self._put_metric(
                'ErrorsByUser',
                1.0,
                dimensions=[{'Name': 'UserID', 'Value': user_id}]
            )
    
    def track_mcp_tool_usage(
        self,
        tool_name: str,
        success: bool,
        response_time: float
    ):
        """
        Track MCP tool usage metrics
        
        Args:
            tool_name: Name of the MCP tool
            success: Whether tool call was successful
            response_time: Tool response time in seconds
        """
        # Total tool calls
        self._put_metric('MCPToolCalls', 1.0)
        
        # Tool calls by name
        self._put_metric(
            'MCPToolCallsByName',
            1.0,
            dimensions=[{'Name': 'Tool', 'Value': tool_name}]
        )
        
        # Tool success/failure
        if success:
            self._put_metric(
                'MCPToolSuccess',
                1.0,
                dimensions=[{'Name': 'Tool', 'Value': tool_name}]
            )
        else:
            self._put_metric(
                'MCPToolFailure',
                1.0,
                dimensions=[{'Name': 'Tool', 'Value': tool_name}]
            )
        
        # Tool response time
        self._put_metric(
            'MCPToolResponseTime',
            response_time,
            unit='Seconds',
            dimensions=[{'Name': 'Tool', 'Value': tool_name}]
        )
    
    def track_guardrails_action(
        self,
        action: str,
        reason: str,
        user_id: Optional[str] = None
    ):
        """
        Track Bedrock Guardrails actions
        
        Args:
            action: Action taken (input_blocked, output_blocked, pii_anonymized)
            reason: Reason for the action
            user_id: Optional user ID
        """
        # Total guardrails actions
        self._put_metric('GuardrailsActions', 1.0)
        
        # Actions by type
        self._put_metric(
            'GuardrailsActionsByType',
            1.0,
            dimensions=[{'Name': 'Action', 'Value': action}]
        )
        
        # Actions by reason
        self._put_metric(
            'GuardrailsActionsByReason',
            1.0,
            dimensions=[{'Name': 'Reason', 'Value': reason}]
        )
        
        if user_id:
            self._put_metric(
                'GuardrailsActionsByUser',
                1.0,
                dimensions=[{'Name': 'UserID', 'Value': user_id}]
            )
    
    def track_translation(
        self,
        source_language: str,
        target_language: str,
        character_count: int
    ):
        """
        Track translation metrics
        
        Args:
            source_language: Source language code
            target_language: Target language code
            character_count: Number of characters translated
        """
        # Total translations
        self._put_metric('TotalTranslations', 1.0)
        
        # Translations by language pair
        self._put_metric(
            'TranslationsByLanguage',
            1.0,
            dimensions=[
                {'Name': 'SourceLanguage', 'Value': source_language},
                {'Name': 'TargetLanguage', 'Value': target_language}
            ]
        )
        
        # Characters translated
        self._put_metric(
            'CharactersTranslated',
            float(character_count),
            unit='Count'
        )
    
    def get_pilot_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get pilot program summary metrics
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dictionary with summary metrics
        """
        try:
            from datetime import timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Query CloudWatch for metrics
            metrics_to_query = [
                'TotalQueries',
                'SuccessfulQueries',
                'FailedQueries',
                'ActiveUsers',
                'PositiveFeedback',
                'NegativeFeedback',
                'TotalErrors'
            ]
            
            summary = {}
            
            for metric_name in metrics_to_query:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace=self.namespace,
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour
                    Statistics=['Sum']
                )
                
                datapoints = response.get('Datapoints', [])
                total = sum(dp['Sum'] for dp in datapoints)
                summary[metric_name] = total
            
            # Calculate derived metrics
            if summary.get('TotalQueries', 0) > 0:
                summary['SuccessRate'] = (
                    summary.get('SuccessfulQueries', 0) / summary['TotalQueries'] * 100
                )
            
            if summary.get('TotalFeedback', 0) > 0:
                total_feedback = summary.get('PositiveFeedback', 0) + summary.get('NegativeFeedback', 0)
                if total_feedback > 0:
                    summary['PositiveFeedbackRate'] = (
                        summary.get('PositiveFeedback', 0) / total_feedback * 100
                    )
            
            return summary
        
        except ClientError as e:
            logger.error(f"Failed to get pilot summary: {e}")
            return {}


# Singleton instance
_pilot_metrics = None

def get_pilot_metrics() -> PilotMetrics:
    """Get or create PilotMetrics singleton"""
    global _pilot_metrics
    if _pilot_metrics is None:
        _pilot_metrics = PilotMetrics()
    return _pilot_metrics
