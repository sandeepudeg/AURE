"""
Amazon Translate Integration
Translates responses to Hindi/Marathi
"""

import boto3
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AmazonTranslate:
    """
    Amazon Translate for multi-language support
    
    Features:
    - Translate to Hindi (hi)
    - Translate to Marathi (mr)
    - Automatic language detection
    - Fast translation (< 500ms)
    """
    
    # Language codes
    ENGLISH = 'en'
    HINDI = 'hi'
    MARATHI = 'mr'
    
    # Language names
    LANGUAGE_NAMES = {
        'en': 'English',
        'hi': 'Hindi',
        'mr': 'Marathi'
    }
    
    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize Amazon Translate
        
        Args:
            region_name: AWS region (from environment if not provided)
        """
        self.region = region_name or os.getenv('AWS_REGION', 'us-east-1')
        self.client = boto3.client('translate', region_name=self.region)
        
        logger.info(f"Amazon Translate initialized (region: {self.region})")
    
    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (en, hi, mr)
            source_language: Source language code (default: auto-detect)
        
        Returns:
            Dictionary with:
            - translated_text: str (translated text)
            - source_language: str (detected/specified source language)
            - target_language: str (target language)
            - success: bool (translation success)
            - error: str (error message if failed)
        """
        # If target is English or same as source, return original
        if target_language == self.ENGLISH:
            return {
                'translated_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'success': True,
                'error': None
            }
        
        try:
            # Call Amazon Translate
            response = self.client.translate_text(
                Text=text,
                SourceLanguageCode=source_language,
                TargetLanguageCode=target_language
            )
            
            translated_text = response.get('TranslatedText', text)
            detected_source = response.get('SourceLanguageCode', source_language)
            
            logger.info(
                f"Translation successful: {detected_source} → {target_language} "
                f"({len(text)} chars)"
            )
            
            return {
                'translated_text': translated_text,
                'source_language': detected_source,
                'target_language': target_language,
                'success': True,
                'error': None
            }
        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                'translated_text': text,  # Return original on error
                'source_language': source_language,
                'target_language': target_language,
                'success': False,
                'error': str(e)
            }
    
    def translate_to_hindi(self, text: str) -> str:
        """
        Translate text to Hindi
        
        Args:
            text: Text to translate
        
        Returns:
            Translated text (or original if translation fails)
        """
        result = self.translate_text(text, self.HINDI)
        return result['translated_text']
    
    def translate_to_marathi(self, text: str) -> str:
        """
        Translate text to Marathi
        
        Args:
            text: Text to translate
        
        Returns:
            Translated text (or original if translation fails)
        """
        result = self.translate_text(text, self.MARATHI)
        return result['translated_text']
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with:
            - language_code: str (detected language code)
            - language_name: str (language name)
            - confidence: float (confidence score)
        """
        try:
            # Use translate with auto-detect to get source language
            response = self.client.translate_text(
                Text=text[:100],  # Use first 100 chars for detection
                SourceLanguageCode='auto',
                TargetLanguageCode='en'
            )
            
            language_code = response.get('SourceLanguageCode', 'unknown')
            language_name = self.LANGUAGE_NAMES.get(language_code, language_code)
            
            return {
                'language_code': language_code,
                'language_name': language_name,
                'confidence': 1.0  # Amazon Translate doesn't provide confidence
            }
        
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                'language_code': 'unknown',
                'language_name': 'Unknown',
                'confidence': 0.0
            }
    
    def translate_response(
        self,
        response: str,
        user_language: str
    ) -> str:
        """
        Translate agent response to user's preferred language
        
        Args:
            response: Agent response text
            user_language: User's preferred language (en, hi, mr)
        
        Returns:
            Translated response
        """
        if user_language == self.ENGLISH:
            return response
        
        result = self.translate_text(response, user_language)
        return result['translated_text']


# Singleton instance
_translate_instance = None


def get_translator() -> AmazonTranslate:
    """Get singleton translator instance"""
    global _translate_instance
    if _translate_instance is None:
        _translate_instance = AmazonTranslate()
    return _translate_instance


if __name__ == "__main__":
    # Test translation
    translator = AmazonTranslate()
    
    # Test English to Hindi
    text_en = "Apply neem oil spray to control aphids on tomato plants."
    result_hi = translator.translate_to_hindi(text_en)
    print(f"English: {text_en}")
    print(f"Hindi: {result_hi}")
    print()
    
    # Test English to Marathi
    result_mr = translator.translate_to_marathi(text_en)
    print(f"Marathi: {result_mr}")
    print()
    
    # Test language detection
    detection = translator.detect_language(text_en)
    print(f"Detected language: {detection}")
