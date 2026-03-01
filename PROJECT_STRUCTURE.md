# URE MVP Project Structure

```
Assembler_URE_Rural/
├── src/                          # Source code
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Base agent class
│   │   ├── supervisor.py        # Supervisor agent
│   │   ├── agri_expert.py       # Agri-Expert agent
│   │   ├── policy_navigator.py  # Policy-Navigator agent
│   │   └── resource_optimizer.py # Resource-Optimizer agent
│   ├── tools/                    # Agent tools
│   │   ├── __init__.py
│   │   ├── image_analysis.py    # Image analysis tools
│   │   ├── knowledge_base.py    # Bedrock KB tools
│   │   ├── weather.py           # Weather tools (MCP)
│   │   └── market.py            # Market price tools (MCP)
│   ├── mcp/                      # MCP Client
│   │   ├── __init__.py
│   │   ├── client.py            # MCP Client implementation
│   │   └── tool_registry.json   # MCP Tool Registry
│   ├── aws/                      # AWS integrations
│   │   ├── __init__.py
│   │   ├── lambda_handler.py    # Lambda function
│   │   ├── dynamodb.py          # DynamoDB operations
│   │   ├── s3.py                # S3 operations
│   │   └── bedrock.py           # Bedrock operations
│   ├── ui/                       # Streamlit UI
│   │   ├── __init__.py
│   │   ├── app.py               # Main Streamlit app
│   │   ├── components.py        # UI components
│   │   └── translations.py      # Language translations
│   ├── config/                   # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py          # App settings
│   │   └── constants.py         # Constants
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── logging.py           # Logging utilities
│       ├── validators.py        # Input validators
│       └── formatters.py        # Output formatters
├── tests/                        # Tests
│   ├── unit/                    # Unit tests
│   │   ├── test_agents.py
│   │   ├── test_mcp_client.py
│   │   └── test_tools.py
│   ├── integration/             # Integration tests
│   │   ├── test_end_to_end.py
│   │   └── test_api.py
│   └── property_based/          # Property-based tests
│       └── test_properties.py
├── docs/                         # Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   └── user_guide.md
├── infrastructure/               # Infrastructure as Code
│   ├── cloudformation.yaml      # CloudFormation template
│   └── terraform/               # Terraform configs (optional)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── requirements-lambda.txt       # Lambda dependencies
├── setup.py                      # Package setup
└── README.md                     # Project README
```

## Current Status

✅ Directory structure created
⏳ Starting implementation with TASK-2.1: MCP Client

## Next Steps

1. Create MCP Client (TASK-2.1)
2. Create base agent class
3. Implement Supervisor agent
4. Implement specialist agents
5. Create Lambda handler
6. Build Streamlit UI
