# URE Architecture Documentation

This directory contains comprehensive architecture documentation for the Unified Rural Ecosystem (URE) MVP.

## Documentation Files

### 1. System Architecture (`system_architecture.md`)
Complete system architecture diagram showing all AWS components, services, and their interactions.

**Contents**:
- High-level system architecture diagram
- Component descriptions (User Layer, Frontend, API, Compute, AI/ML, Storage, Security, Monitoring)
- Key features (Scalability, Security, Reliability, Performance)
- Data flow overview
- Cost optimization breakdown

**Use this when**: You need to understand the overall system design and how components interact.

---

### 2. Data Flow (`data_flow.md`)
Detailed sequence diagrams showing how data flows through the system.

**Contents**:
- Complete request-response flow
- Image upload flow
- Agent routing flow
- MCP tool call flow
- Guardrails flow
- Translation flow
- Error handling flow
- Monitoring flow
- Data persistence flow

**Use this when**: You need to understand how a specific request is processed or debug data flow issues.

---

### 3. Agent Interaction (`agent_interaction.md`)
Architecture and interaction patterns for the AI agents.

**Contents**:
- Agent architecture overview
- Supervisor agent routing logic
- Agri-Expert agent workflow
- Policy-Navigator agent workflow
- Resource-Optimizer agent workflow
- Multi-agent coordination
- Agent tool usage matrix
- Agent decision tree
- Agent communication protocol
- Agent performance metrics

**Use this when**: You need to understand how agents work together or add new agent capabilities.

---

### 4. MCP Integration (`mcp_integration.md`)
Model Context Protocol integration architecture and implementation details.

**Contents**:
- MCP integration overview
- MCP Client architecture
- Tool registry structure
- MCP tool call flow
- Permission system and matrix
- Retry logic with exponential backoff
- Caching strategy
- MCP server implementation
- Error handling
- Monitoring & logging
- MCP integration benefits
- Future enhancements

**Use this when**: You need to understand MCP integration, add new MCP tools, or debug MCP issues.

---

### 5. Deployment Architecture (`deployment_architecture.md`)
AWS deployment architecture and infrastructure details.

**Contents**:
- AWS deployment architecture
- CloudFormation stack resources
- Deployment pipeline
- Multi-environment strategy (dev/staging/prod)
- Scaling architecture
- High availability architecture
- Security architecture
- Disaster recovery architecture
- Cost optimization architecture
- Deployment checklist

**Use this when**: You need to deploy the system, understand infrastructure, or plan for scaling.

---

## Quick Reference

### For Developers
- **Understanding the system**: Start with `system_architecture.md`
- **Debugging issues**: Check `data_flow.md` for request flow
- **Adding features**: Review `agent_interaction.md` for agent patterns
- **Integrating external services**: See `mcp_integration.md`

### For DevOps
- **Deploying the system**: Follow `deployment_architecture.md`
- **Monitoring**: Check monitoring sections in `system_architecture.md` and `data_flow.md`
- **Scaling**: Review scaling sections in `deployment_architecture.md`
- **Security**: See security sections in all documents

### For Product Managers
- **System capabilities**: Review `system_architecture.md` component descriptions
- **User flows**: Check `data_flow.md` for end-to-end flows
- **Agent capabilities**: See `agent_interaction.md` for what each agent can do
- **Cost planning**: Review cost sections in `system_architecture.md` and `deployment_architecture.md`

---

## Diagram Formats

All diagrams are created using **Mermaid** syntax, which can be:
- Rendered in GitHub/GitLab markdown viewers
- Exported to PNG/SVG using Mermaid CLI
- Edited using Mermaid Live Editor (https://mermaid.live)

### Rendering Diagrams

**In GitHub/GitLab**: Diagrams render automatically in markdown preview.

**Using Mermaid CLI**:
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i system_architecture.md -o system_architecture.png

# Convert to SVG
mmdc -i system_architecture.md -o system_architecture.svg
```

**Using Mermaid Live Editor**:
1. Go to https://mermaid.live
2. Copy diagram code from markdown file
3. Edit and export as PNG/SVG

---

## Architecture Principles

### 1. Serverless-First
- Use AWS Lambda for compute (no server management)
- Use managed services (DynamoDB, S3, Bedrock)
- Auto-scaling by default

### 2. Security by Design
- Encryption at rest (KMS) and in transit (TLS)
- Least privilege IAM roles
- Content filtering with Bedrock Guardrails
- PII anonymization

### 3. Cost Optimization
- Pay-per-use pricing (Lambda, DynamoDB on-demand)
- Reserved concurrency to prevent runaway costs
- TTL and lifecycle policies for data cleanup
- Caching to reduce API calls

### 4. High Availability
- Multi-AZ deployment
- Auto-retry with exponential backoff
- Fallback to cached data
- CloudWatch alarms for proactive monitoring

### 5. Observability
- Comprehensive logging to CloudWatch
- Custom metrics for business KPIs
- Real-time dashboards
- Automated alerting

---

## Technology Stack

### Frontend
- **Streamlit**: Python-based web framework
- **Responsive design**: Works on mobile and desktop

### Backend
- **AWS Lambda**: Serverless compute
- **Python 3.11**: Runtime environment
- **Strands SDK**: Agent orchestration

### AI/ML
- **Amazon Bedrock**: Nova Pro model
- **Knowledge Base**: RAG for schemes
- **Guardrails**: Content filtering
- **Translate**: Multi-language support

### Storage
- **S3**: Object storage for images/documents
- **DynamoDB**: NoSQL database for conversations/profiles
- **KMS**: Encryption key management

### External Services
- **MCP Servers**: Agmarknet (prices), Weather (forecasts)
- **FastAPI**: MCP server framework

### Monitoring
- **CloudWatch**: Logs, metrics, alarms, dashboards
- **SNS**: Alarm notifications

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Feb 28, 2026 | Initial architecture documentation |

---

## Contributing

When updating architecture documentation:

1. **Keep diagrams up-to-date**: Update Mermaid diagrams when architecture changes
2. **Document decisions**: Add rationale for architectural choices
3. **Update all affected docs**: Changes may impact multiple documents
4. **Version control**: Update version history in this README
5. **Review with team**: Get feedback before finalizing changes

---

## Contact

For questions about the architecture:
- **Technical Lead**: [Your Name]
- **Email**: support@ure-mvp.com
- **Documentation**: https://github.com/your-org/ure-mvp/docs/architecture

---

**Last Updated**: February 28, 2026
