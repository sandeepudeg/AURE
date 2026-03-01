"""
Bedrock Guardrails Integration
Filters harmful content and off-topic responses
"""

import boto3
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class BedrockGuardrails:
    """
    Bedrock Guardrails for content safety filtering
    
    Features:
    - Block harmful pesticide advice
    - Block off-topic content (politics, religion)
    - Allow legitimate agricultural advice
    - Low false positive rate (< 5%)
    """
    
    def __init__(
        self,
        guardrail_id: Optional[str] = None,
        guardrail_version: str = "DRAFT"
    ):
        """
        Initialize Bedrock Guardrails
        
        Args:
            guardrail_id: Guardrail ID (from environment if not provided)
            guardrail_version: Guardrail version (default: DRAFT)
        """
        self.client = boto3.client('bedrock-runtime')
        self.guardrail_id = guardrail_id or os.getenv('BEDROCK_GUARDRAIL_ID')
        self.guardrail_version = guardrail_version
        
        if not self.guardrail_id:
            logger.warning("No guardrail ID configured - guardrails disabled")
        else:
            logger.info(f"Guardrails initialized: {self.guardrail_id} (v{self.guardrail_version})")
    
    def apply_guardrails(
        self,
        text: str,
        source: str = "OUTPUT"
    ) -> Dict[str, Any]:
        """
        Apply guardrails to text content
        
        Args:
            text: Text to check
            source: Source type ("INPUT" or "OUTPUT")
        
        Returns:
            Dictionary with:
            - blocked: bool (True if content blocked)
            - action: str (BLOCKED or NONE)
            - reason: str (reason for blocking)
            - filtered_text: str (original or filtered text)
        """
        # If no guardrail configured, allow all content
        if not self.guardrail_id:
            return {
                'blocked': False,
                'action': 'NONE',
                'reason': 'No guardrail configured',
                'filtered_text': text
            }
        
        try:
            # Apply guardrails using Bedrock API
            response = self.client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source=source,
                content=[{
                    'text': {
                        'text': text
                    }
                }]
            )
            
            action = response.get('action', 'NONE')
            blocked = action == 'GUARDRAIL_INTERVENED'
            
            # Extract assessments
            assessments = response.get('assessments', [])
            reasons = []
            
            for assessment in assessments:
                # Check topic policy violations
                topic_policy = assessment.get('topicPolicy', {})
                if topic_policy.get('topics'):
                    for topic in topic_policy['topics']:
                        if topic.get('action') == 'BLOCKED':
                            reasons.append(f"Topic blocked: {topic.get('name', 'unknown')}")
                
                # Check content policy violations
                content_policy = assessment.get('contentPolicy', {})
                if content_policy.get('filters'):
                    for filter_item in content_policy['filters']:
                        if filter_item.get('action') == 'BLOCKED':
                            reasons.append(f"Content blocked: {filter_item.get('type', 'unknown')}")
                
                # Check word policy violations
                word_policy = assessment.get('wordPolicy', {})
                if word_policy.get('customWords'):
                    for word in word_policy['customWords']:
                        if word.get('action') == 'BLOCKED':
                            reasons.append(f"Blocked word: {word.get('match', 'unknown')}")
            
            reason = '; '.join(reasons) if reasons else 'Content passed guardrails'
            
            logger.info(f"Guardrail check: action={action}, blocked={blocked}")
            
            return {
                'blocked': blocked,
                'action': action,
                'reason': reason,
                'filtered_text': text if not blocked else '[Content blocked by safety filters]'
            }
        
        except Exception as e:
            logger.error(f"Guardrail check failed: {e}")
            # On error, allow content but log the issue
            return {
                'blocked': False,
                'action': 'ERROR',
                'reason': f'Guardrail check failed: {str(e)}',
                'filtered_text': text
            }
    
    def check_input(self, text: str) -> Dict[str, Any]:
        """
        Check user input for harmful content
        
        Args:
            text: User input text
        
        Returns:
            Guardrail check result
        """
        return self.apply_guardrails(text, source="INPUT")
    
    def check_output(self, text: str) -> Dict[str, Any]:
        """
        Check agent output for harmful content
        
        Args:
            text: Agent output text
        
        Returns:
            Guardrail check result
        """
        return self.apply_guardrails(text, source="OUTPUT")


# Singleton instance
_guardrails_instance = None


def get_guardrails() -> BedrockGuardrails:
    """Get singleton guardrails instance"""
    global _guardrails_instance
    if _guardrails_instance is None:
        _guardrails_instance = BedrockGuardrails()
    return _guardrails_instance


if __name__ == "__main__":
    # Test guardrails
    guardrails = BedrockGuardrails()
    
    # Test legitimate agricultural advice
    result1 = guardrails.check_output(
        "Apply neem oil spray to control aphids on tomato plants. "
        "Mix 2 tablespoons per liter of water."
    )
    print(f"Test 1 (legitimate advice): {result1}")
    
    # Test harmful pesticide advice
    result2 = guardrails.check_output(
        "Use DDT pesticide to kill all insects. "
        "Apply large amounts directly to crops."
    )
    print(f"Test 2 (harmful advice): {result2}")
    
    # Test off-topic content
    result3 = guardrails.check_output(
        "Vote for our political party in the upcoming elections. "
        "We will solve all your problems."
    )
    print(f"Test 3 (off-topic): {result3}")
