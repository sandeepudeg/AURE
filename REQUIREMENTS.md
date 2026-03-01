# URE MVP - Python Dependencies Guide

This document explains the different requirements files and how to use them.

## Requirements Files

### 1. `requirements.txt` - Production Dependencies
Core dependencies needed to run the URE MVP application.

**Install:**
```bash
pip install -r requirements.txt
```

**Use for:**
- Production deployment
- Streamlit web app
- Lambda functions (use requirements-lambda.txt instead for optimized deployment)

---

### 2. `requirements-dev.txt` - Development Dependencies
All dependencies including development, testing, and documentation tools.

**Install:**
```bash
pip install -r requirements-dev.txt
```

**Use for:**
- Local development
- Running tests
- Code quality checks
- Documentation generation
- Debugging

---

### 3. `requirements-lambda.txt` - Lambda Deployment
Optimized dependencies for AWS Lambda deployment (minimal size).

**Install:**
```bash
pip install -r requirements-lambda.txt -t lambda_package/
```

**Use for:**
- AWS Lambda function deployment
- Minimizing package size
- Production Lambda layers

---

## Installation Instructions

### Local Development Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Verify installation:**
   ```bash
   pip list
   ```

---

### Lambda Deployment Setup

1. **Create Lambda package directory:**
   ```bash
   mkdir lambda_package
   ```

2. **Install Lambda dependencies:**
   ```bash
   pip install -r requirements-lambda.txt -t lambda_package/
   ```

3. **Copy Lambda function code:**
   ```bash
   cp src/lambda_handler.py lambda_package/
   cp src/mcp_client.py lambda_package/
   ```

4. **Create deployment package:**
   ```bash
   cd lambda_package
   zip -r ../lambda_deployment.zip .
   cd ..
   ```

5. **Deploy to AWS Lambda:**
   ```bash
   aws lambda update-function-code \
     --function-name ure-mvp-handler \
     --zip-file fileb://lambda_deployment.zip
   ```

---

### Streamlit App Setup

1. **Install Streamlit dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Streamlit app:**
   ```bash
   streamlit run src/streamlit_app.py
   ```

3. **Access app:**
   - Open browser to: http://localhost:8501

---

## Dependency Categories

### Core AWS SDK
- `boto3`: AWS SDK for Python
- `botocore`: Low-level AWS service access

### AI/ML
- `strands-agents`: Multi-agent orchestration
- `anthropic`: Claude API client for Bedrock

### Web Framework
- `streamlit`: Web UI framework

### Data Processing
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `scipy`: Scientific computing

### Image Processing
- `Pillow`: Image processing
- `opencv-python`: Computer vision (optional)

### Vector Database
- `opensearch-py`: OpenSearch client
- `pinecone-client`: Pinecone client (alternative)

### HTTP & API
- `requests`: HTTP library for MCP
- `httpx`: Modern HTTP client

### Testing
- `pytest`: Testing framework
- `hypothesis`: Property-based testing
- `moto`: Mock AWS services

### Code Quality
- `black`: Code formatter
- `flake8`: Linting
- `pylint`: Static analysis
- `mypy`: Type checking

---

## Version Pinning

All dependencies are pinned to specific versions for reproducibility:
- Ensures consistent behavior across environments
- Prevents breaking changes from automatic updates
- Facilitates debugging and troubleshooting

**To update dependencies:**
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

---

## Lambda Package Size Optimization

Lambda has a 250MB unzipped package size limit. To optimize:

1. **Remove unnecessary files:**
   ```bash
   cd lambda_package
   find . -type d -name "tests" -exec rm -rf {} +
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -delete
   find . -name "*.so" | grep -v "\.libs" | xargs strip
   ```

2. **Use Lambda Layers for large dependencies:**
   - Create layer for numpy, pandas, Pillow
   - Reduces main package size
   - Reusable across multiple functions

3. **Consider slim packages:**
   - Use `pandas-slim` instead of `pandas`
   - Use `Pillow-SIMD` for faster image processing

---

## Troubleshooting

### Issue: Package conflicts
**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Lambda package too large
**Solution:**
- Use Lambda Layers for large dependencies
- Remove unnecessary files (see optimization section)
- Use slim package versions

### Issue: Import errors in Lambda
**Solution:**
- Verify all dependencies in requirements-lambda.txt
- Check Lambda runtime version (Python 3.9+)
- Ensure package structure is correct

### Issue: Streamlit not starting
**Solution:**
```bash
pip install --upgrade streamlit
streamlit cache clear
streamlit run src/streamlit_app.py
```

---

## Additional Resources

- [AWS Lambda Deployment Guide](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Strands Agents SDK](https://github.com/strands-ai/strands-agents)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/sandeepudeg/Assembler_URE_Rural/issues
- Documentation: See `.kiro/specs/unified-rural-ecosystem/` directory
