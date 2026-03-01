# Unified Rural Ecosystem (URE) MVP

AI-powered agricultural assistance platform for Indian farmers, built for AWS AI for Bharat Hackathon.

## 🌾 Overview

URE provides farmers with:
- **Crop Disease Diagnosis** via image analysis
- **Market Price Information** from Agmarknet
- **Government Scheme Guidance** (PM-Kisan)
- **Irrigation Recommendations** based on weather and soil data

## 🏗️ Architecture

- **Frontend**: Streamlit web interface (Hindi/Marathi/English)
- **Backend**: AWS Lambda + API Gateway
- **AI Agents**: Strands Agents SDK with Claude 3.5 Sonnet
- **Knowledge Base**: Amazon Bedrock with PlantVillage dataset
- **External Services**: MCP (Model Context Protocol) for Agmarknet & Weather APIs
- **Storage**: DynamoDB (conversations) + S3 (images, datasets)

## 📁 Project Structure

```
Assembler_URE_Rural/
├── src/
│   ├── agents/          # AI agent implementations
│   ├── mcp/             # MCP Client for external services
│   ├── aws/             # AWS integrations (Lambda, DynamoDB, S3)
│   ├── ui/              # Streamlit interface
│   ├── tools/           # Agent tools
│   ├── config/          # Configuration
│   └── utils/           # Utilities
├── tests/               # Unit, integration, property-based tests
├── docs/                # Documentation
└── infrastructure/      # CloudFormation/Terraform
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sandeepudeg/Assembler_URE_Rural.git
   cd Assembler_URE_Rural
   ```

2. **Create virtual environment**
   ```bash
   python -m venv rural
   # Windows
   .\rural\Scripts\Activate.ps1
   # Linux/Mac
   source rural/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and configuration
   ```

5. **Run Streamlit app** (coming soon)
   ```bash
   streamlit run src/ui/app.py
   ```

## 🛠️ Development Status

### ✅ Completed
- [x] Project structure setup
- [x] Virtual environment with all dependencies
- [x] MCP Client implementation
- [x] MCP Tool Registry (4 tools: market prices, weather)
- [x] Environment configuration

### 🚧 In Progress
- [ ] Agent implementations (Supervisor, Agri-Expert, Policy-Navigator, Resource-Optimizer)
- [ ] Lambda function handler
- [ ] Streamlit UI
- [ ] AWS infrastructure deployment

### 📋 Upcoming
- [ ] Bedrock Knowledge Base setup
- [ ] Testing suite
- [ ] Documentation
- [ ] Pilot deployment

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run property-based tests
pytest tests/property_based/

# Run all tests with coverage
pytest --cov=src tests/
```

## 📚 Documentation

- [Architecture](docs/architecture.md) - System design and components
- [API Documentation](docs/api.md) - API endpoints and usage
- [Deployment Guide](docs/deployment.md) - AWS deployment instructions
- [User Guide](docs/user_guide.md) - For farmers using the system

## 🤝 Contributing

This is a hackathon project. For questions or suggestions, please open an issue.

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🏆 Hackathon

Built for **AWS AI for Bharat Hackathon** - Empowering rural India with AI.

## 👥 Team

- Sandeep Udeg - [GitHub](https://github.com/sandeepudeg)

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**Status**: 🟡 In Development | **Target**: MVP by Week 9
