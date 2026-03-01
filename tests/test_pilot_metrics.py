#!/usr/bin/env python3
"""
Tests for Pilot Metrics Module
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.pilot_metrics import PilotMetrics


@pytest.fixture
def mock_cloudwatch():
    """Mock CloudWatch client"""
    with patch('boto3.client') as mock_client:
        mock_cw = Mock()
        mock_client.return_value = mock_cw
        yield mock_cw


def test_pilot_metrics_initialization(mock_cloudwatch):
    """Test PilotMetrics initialization"""
    metrics = PilotMetrics(namespace="URE/Test")
    
    assert metrics.namespace == "URE/Test"
    assert metrics.cloudwatch is not None


def test_track_query(mock_cloudwatch):
    """Test query tracking"""
    metrics = PilotMetrics()
    
    metrics.track_query(
        user_id='test_user_001',
        agent_used='agri-expert',
        success=True,
        response_time=2.5,
        language='hi',
        has_image=True
    )
    
    # Should have called put_metric_data multiple times
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 7  # Multiple metrics tracked


def test_track_farmer_engagement(mock_cloudwatch):
    """Test farmer engagement tracking"""
    metrics = PilotMetrics()
    
    metrics.track_farmer_engagement(
        user_id='test_user_001',
        session_duration=300.0,
        queries_in_session=5
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 3


def test_track_feedback(mock_cloudwatch):
    """Test feedback tracking"""
    metrics = PilotMetrics()
    
    # Positive feedback
    metrics.track_feedback(
        user_id='test_user_001',
        rating='positive',
        agent_used='agri-expert'
    )
    
    assert mock_cloudwatch.put_metric_data.called
    
    # Negative feedback
    metrics.track_feedback(
        user_id='test_user_002',
        rating='negative',
        agent_used='policy-navigator'
    )
    
    assert mock_cloudwatch.put_metric_data.call_count >= 6


def test_track_agent_performance(mock_cloudwatch):
    """Test agent performance tracking"""
    metrics = PilotMetrics()
    
    metrics.track_agent_performance(
        agent_name='agri-expert',
        accuracy=85.5,
        confidence=92.3
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 2


def test_track_error(mock_cloudwatch):
    """Test error tracking"""
    metrics = PilotMetrics()
    
    metrics.track_error(
        error_type='guardrails_block',
        agent_used='supervisor',
        user_id='test_user_001'
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 4


def test_track_mcp_tool_usage(mock_cloudwatch):
    """Test MCP tool usage tracking"""
    metrics = PilotMetrics()
    
    metrics.track_mcp_tool_usage(
        tool_name='get_market_prices',
        success=True,
        response_time=1.2
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 4


def test_track_guardrails_action(mock_cloudwatch):
    """Test guardrails action tracking"""
    metrics = PilotMetrics()
    
    metrics.track_guardrails_action(
        action='input_blocked',
        reason='harmful_content',
        user_id='test_user_001'
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 4


def test_track_translation(mock_cloudwatch):
    """Test translation tracking"""
    metrics = PilotMetrics()
    
    metrics.track_translation(
        source_language='en',
        target_language='hi',
        character_count=150
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_count = mock_cloudwatch.put_metric_data.call_count
    assert call_count >= 3


def test_get_pilot_summary(mock_cloudwatch):
    """Test pilot summary retrieval"""
    # Mock get_metric_statistics response
    mock_cloudwatch.get_metric_statistics.return_value = {
        'Datapoints': [
            {'Sum': 100, 'Timestamp': datetime.utcnow()},
            {'Sum': 150, 'Timestamp': datetime.utcnow()}
        ]
    }
    
    metrics = PilotMetrics()
    summary = metrics.get_pilot_summary(hours=24)
    
    assert isinstance(summary, dict)
    assert mock_cloudwatch.get_metric_statistics.called


def test_put_metric_with_dimensions(mock_cloudwatch):
    """Test putting metric with dimensions"""
    metrics = PilotMetrics()
    
    metrics._put_metric(
        metric_name='TestMetric',
        value=10.0,
        unit='Count',
        dimensions=[
            {'Name': 'Agent', 'Value': 'test-agent'},
            {'Name': 'UserID', 'Value': 'test-user'}
        ]
    )
    
    assert mock_cloudwatch.put_metric_data.called
    call_args = mock_cloudwatch.put_metric_data.call_args
    
    # Verify namespace
    assert call_args[1]['Namespace'] == 'URE/Pilot'
    
    # Verify metric data
    metric_data = call_args[1]['MetricData'][0]
    assert metric_data['MetricName'] == 'TestMetric'
    assert metric_data['Value'] == 10.0
    assert metric_data['Unit'] == 'Count'
    assert len(metric_data['Dimensions']) == 2


def test_error_handling_in_put_metric(mock_cloudwatch):
    """Test error handling in _put_metric"""
    from botocore.exceptions import ClientError
    
    # Mock ClientError
    mock_cloudwatch.put_metric_data.side_effect = ClientError(
        {'Error': {'Code': 'InvalidParameterValue', 'Message': 'Test error'}},
        'PutMetricData'
    )
    
    metrics = PilotMetrics()
    
    # Should not raise exception
    metrics._put_metric('TestMetric', 1.0)
    
    assert mock_cloudwatch.put_metric_data.called


def test_singleton_pattern():
    """Test get_pilot_metrics singleton"""
    from utils.pilot_metrics import get_pilot_metrics
    
    metrics1 = get_pilot_metrics()
    metrics2 = get_pilot_metrics()
    
    # Should return same instance
    assert metrics1 is metrics2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
