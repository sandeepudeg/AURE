# URE Pilot Metrics Guide

## Overview

The URE MVP includes comprehensive custom CloudWatch metrics for tracking pilot program performance. These metrics provide real-time insights into system usage, user engagement, agent performance, and overall pilot success.

## Metrics Categories

### 1. Query Metrics
Track all query-related activity:
- `TotalQueries` - Total number of queries
- `SuccessfulQueries` - Queries that completed successfully
- `FailedQueries` - Queries that failed
- `QueriesByAgent` - Queries handled by each agent (dimension: Agent)
- `QueriesByUser` - Queries per user (dimension: UserID)
- `QueriesByLanguage` - Queries by language (dimension: Language)
- `ImageQueries` - Queries with image uploads
- `ResponseTime` - Query response time in seconds
- `ResponseTimeByAgent` - Response time per agent (dimension: Agent)

### 2. User Engagement Metrics
Track farmer engagement and usage patterns:
- `ActiveUsers` - Number of active users
- `SessionDuration` - User session duration in seconds (dimension: UserID)
- `QueriesPerSession` - Queries per session (dimension: UserID)

### 3. Feedback Metrics
Track user satisfaction:
- `TotalFeedback` - Total feedback submissions
- `PositiveFeedback` - Positive feedback count
- `NegativeFeedback` - Negative feedback count
- `PositiveFeedbackByAgent` - Positive feedback per agent (dimension: Agent)
- `NegativeFeedbackByAgent` - Negative feedback per agent (dimension: Agent)
- `FeedbackByUser` - Feedback per user (dimension: UserID)

### 4. Agent Performance Metrics
Track AI agent performance:
- `AgentAccuracy` - Agent accuracy percentage (dimension: Agent)
- `AgentConfidence` - Agent confidence percentage (dimension: Agent)

### 5. Error Metrics
Track system errors and issues:
- `TotalErrors` - Total error count
- `ErrorsByType` - Errors by type (dimension: ErrorType)
- `ErrorsByAgent` - Errors by agent (dimension: Agent)
- `ErrorsByUser` - Errors by user (dimension: UserID)

### 6. MCP Tool Metrics
Track MCP tool usage:
- `MCPToolCalls` - Total MCP tool calls
- `MCPToolCallsByName` - Calls per tool (dimension: Tool)
- `MCPToolSuccess` - Successful tool calls (dimension: Tool)
- `MCPToolFailure` - Failed tool calls (dimension: Tool)
- `MCPToolResponseTime` - Tool response time (dimension: Tool)

### 7. Guardrails Metrics
Track Bedrock Guardrails actions:
- `GuardrailsActions` - Total guardrails actions
- `GuardrailsActionsByType` - Actions by type (dimension: Action)
- `GuardrailsActionsByReason` - Actions by reason (dimension: Reason)
- `GuardrailsActionsByUser` - Actions by user (dimension: UserID)

### 8. Translation Metrics
Track Amazon Translate usage:
- `TotalTranslations` - Total translations
- `TranslationsByLanguage` - Translations by language pair (dimensions: SourceLanguage, TargetLanguage)
- `CharactersTranslated` - Total characters translated

## Using the Metrics Dashboard

### View Pilot Summary

Display overall pilot metrics for the last 24 hours:

```bash
python scripts/pilot_metrics_dashboard.py --summary
```

View metrics for a custom time period:

```bash
python scripts/pilot_metrics_dashboard.py --summary --hours 48
```

### View Agent Breakdown

Display detailed agent performance:

```bash
python scripts/pilot_metrics_dashboard.py --agents --hours 24
```

### Export Metrics to JSON

Export all metrics to a JSON file:

```bash
python scripts/pilot_metrics_dashboard.py --export pilot_metrics.json --hours 24
```

### View All Reports

Display all available reports:

```bash
python scripts/pilot_metrics_dashboard.py --all --hours 24
```

## Sample Dashboard Output

```
============================================================
URE PILOT PROGRAM METRICS - Last 24 Hours
============================================================

📊 QUERY METRICS
------------------------------------------------------------
Total Queries:      1,234
Successful:         1,198
Failed:             36
Success Rate:       97.1%
Avg Response Time:  2.34s
Max Response Time:  8.92s

👥 USER ENGAGEMENT
------------------------------------------------------------
Active Users:       52
Image Queries:      234
Image Query Rate:   19.0%

🤖 AGENT PERFORMANCE
------------------------------------------------------------
supervisor          : 456 queries
agri-expert         : 389 queries
policy-navigator    : 234 queries
resource-optimizer  : 155 queries

💬 FEEDBACK METRICS
------------------------------------------------------------
Total Feedback:     89
Positive:           76
Negative:           13
Positive Rate:      85.4%

🌐 LANGUAGE USAGE
------------------------------------------------------------
English        : 567 queries
Hindi          : 445 queries
Marathi        : 222 queries

⚠️  ERROR METRICS
------------------------------------------------------------
Total Errors:       36
Guardrails Actions: 12

🔧 MCP TOOL USAGE
------------------------------------------------------------
Total MCP Calls:    234
Successful:         228
Success Rate:       97.4%
```

## CloudWatch Dashboard

The pilot metrics are automatically visualized in the CloudWatch dashboard created by the CloudFormation template. Access it at:

**AWS Console → CloudWatch → Dashboards → URE-MVP-Dashboard**

The dashboard includes:
- Query volume and success rate
- Response time trends
- Agent usage distribution
- Feedback sentiment
- Error rates
- MCP tool performance

## Alarms

The following CloudWatch alarms are configured:
- High error rate (>5% of queries)
- Slow response time (>5s average)
- Low success rate (<95%)
- High guardrails block rate (>10%)

Alarms send notifications to the SNS topic configured in CloudFormation.

## Programmatic Access

### Python Integration

```python
from utils.pilot_metrics import get_pilot_metrics

# Get metrics instance
metrics = get_pilot_metrics()

# Track a query
metrics.track_query(
    user_id='farmer_001',
    agent_used='agri-expert',
    success=True,
    response_time=2.5,
    language='hi',
    has_image=True
)

# Track feedback
metrics.track_feedback(
    user_id='farmer_001',
    rating='positive',
    agent_used='agri-expert'
)

# Track error
metrics.track_error(
    error_type='guardrails_block',
    agent_used='supervisor',
    user_id='farmer_001'
)

# Get pilot summary
summary = metrics.get_pilot_summary(hours=24)
print(f"Total queries: {summary.get('TotalQueries', 0)}")
print(f"Success rate: {summary.get('SuccessRate', 0):.1f}%")
```

### Lambda Integration

The pilot metrics are automatically tracked in the Lambda handler for:
- Every query (success/failure, response time, agent used)
- Guardrails actions (input/output blocks)
- Translations (language pairs, character count)
- Errors (type, agent, user)

No additional code needed - metrics are tracked automatically!

## Best Practices

### During Pilot

1. **Daily Monitoring**: Check metrics dashboard daily
2. **Weekly Reports**: Generate weekly summary reports
3. **Alert Response**: Respond to CloudWatch alarms within 1 hour
4. **Feedback Analysis**: Review negative feedback daily
5. **Performance Tracking**: Monitor agent accuracy and response times

### Metric Analysis

1. **Success Rate**: Target >95%
2. **Response Time**: Target <5s average
3. **Positive Feedback**: Target >80%
4. **Active Users**: Track daily active users
5. **Error Rate**: Target <5%

### Troubleshooting

**High Error Rate**:
- Check CloudWatch Logs for error details
- Review ErrorsByType metric to identify patterns
- Check ErrorsByAgent to identify problematic agents

**Slow Response Time**:
- Check ResponseTimeByAgent to identify slow agents
- Review Lambda duration metrics
- Check MCP tool response times

**Low Feedback Rate**:
- Encourage farmers to provide feedback
- Check FeedbackByUser to identify engaged users
- Review UI/UX for feedback collection

**High Guardrails Block Rate**:
- Review GuardrailsActionsByReason
- Check if farmers are asking off-topic questions
- Consider adjusting guardrails configuration

## Cost Considerations

Custom CloudWatch metrics cost:
- First 10,000 metrics: $0.30 per metric per month
- Additional metrics: $0.10 per metric per month

Estimated cost for pilot (50 users, 1000 queries/day):
- ~30 custom metrics
- ~$9/month for custom metrics
- ~$3/month for CloudWatch Logs
- **Total: ~$12/month**

## Exporting Data

### Export to CSV

```python
import boto3
import csv
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

# Get metric data
response = cloudwatch.get_metric_statistics(
    Namespace='URE/Pilot',
    MetricName='TotalQueries',
    StartTime=datetime.utcnow() - timedelta(days=7),
    EndTime=datetime.utcnow(),
    Period=3600,
    Statistics=['Sum']
)

# Write to CSV
with open('queries.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Queries'])
    for dp in response['Datapoints']:
        writer.writerow([dp['Timestamp'], dp['Sum']])
```

### Export to S3

```bash
# Export metrics to JSON
python scripts/pilot_metrics_dashboard.py --export metrics.json --hours 168

# Upload to S3
aws s3 cp metrics.json s3://ure-mvp-data-us-east-1-188238313375/pilot-reports/
```

## Support

For issues or questions about pilot metrics:
1. Check CloudWatch Logs for detailed error messages
2. Review this guide for troubleshooting steps
3. Contact the development team with specific metric names and time ranges

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0
