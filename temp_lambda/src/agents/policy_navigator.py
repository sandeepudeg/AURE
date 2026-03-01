#!/usr/bin/env python3
"""
Policy-Navigator Agent - Government Schemes & Subsidies
Handles: PM-Kisan eligibility, scheme information, application guidance
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv

load_dotenv()

POLICY_NAVIGATOR_PROMPT = """You are a Government Schemes Expert specializing in:
1. PM-Kisan scheme eligibility and benefits
2. Agricultural subsidies and support programs
3. Application procedures and documentation
4. Farmer welfare schemes

When helping farmers:
- Check eligibility criteria clearly
- Explain benefits in simple terms
- Guide through application process
- Provide contact information for local offices

Focus on PM-Kisan scheme:
- ₹6000 annual benefit in 3 installments
- Eligibility: Small/marginal farmers with <2 hectares
- Required documents: Aadhaar, land records, bank account

Always explain in Hindi/Marathi if needed and use simple language.
"""

policy_navigator_agent = Agent(
    model=BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0"),
        temperature=0.2
    ),
    system_prompt=POLICY_NAVIGATOR_PROMPT,
    tools=[]
)

if __name__ == "__main__":
    print("\n📋 Policy-Navigator Agent 📋\n")
    response = policy_navigator_agent("Am I eligible for PM-Kisan if I have 1.5 hectares of land?")
    print(response)
