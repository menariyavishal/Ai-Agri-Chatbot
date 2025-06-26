import logging
from typing import Tuple, Optional
import re
import requests
import json
import os
from app.config import Config

logger = logging.getLogger(__name__)

class LanguageProcessor:
    """Enhanced language detection and translation using Google Translate API"""
    
    def __init__(self):
        self.api_key = Config.GOOGLE_TRANSLATE_API_KEY or os.environ.get('GOOGLE_TRANSLATE_API_KEY')
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        self.marathi_patterns = [
            # Devanagari script detection
            r'[\u0900-\u097F]',
            # Common Marathi words
            r'\b(आहे|आहेत|मी|तुम्ही|काय|कसे|कुठे|केव्हा|का|कोण)\b'
        ]
    
    def detect_language(self, text: str) -> str:
        """
        Enhanced language detection with fallback mechanisms
        Returns: 'mr' for Marathi, 'en' for English
        """
        if not text or not text.strip():
            return 'mr'  # Default to Marathi
        
        try:
            # First, check for Devanagari script (Marathi)
            if any(re.search(pattern, text) for pattern in self.marathi_patterns):
                logger.info("Detected Marathi based on script/patterns")
                return 'mr'
            
            # If no API key, use pattern-based detection only
            if not self.api_key:
                logger.warning("No Google Translate API key provided, using pattern-based detection only")
                return 'en'  # Default to English if no Devanagari detected
            
            # Use Google Translate API for detection
            url = f"{self.base_url}/detect?key={self.api_key}"
            payload = {
                "q": text
            }
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result["data"]["detections"][0][0]["language"]
                confidence = result["data"]["detections"][0][0]["confidence"]
                
                logger.info(f"Google Translate API detected language: {detected_lang} (confidence: {confidence})")
                
                # Map detected language to our supported languages
                if detected_lang in ['mr', 'hi']:  # Marathi or Hindi (close languages)
                    return 'mr'
                else:
                    return 'en'
            else:
                logger.warning(f"Google Translate API detection failed: {response.status_code}")
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'  # Default to English on errors
    
    def translate_to_english(self, text: str) -> str:
        """Translate Marathi text to English"""
        if not text or not text.strip():
            return ""
            
        try:
            # No need to translate if already in English
            if self.detect_language(text) == 'en':
                return text
                
            # If no API key, return original text
            if not self.api_key:
                logger.warning("No Google Translate API key provided, returning original text")
                return text
                
            url = f"{self.base_url}?key={self.api_key}"
            payload = {
                "q": text,
                "source": "mr",
                "target": "en",
                "format": "text"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result["data"]["translations"][0]["translatedText"]
                return translated_text
            else:
                logger.error(f"Translation to English failed: {response.status_code}")
                return text  # Return original text on API error
                
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text  # Return original text on error
    
    def translate_to_marathi(self, text: str) -> str:
        """Translate English text to Marathi"""
        if not text or not text.strip():
            return ""
            
        try:
            # No need to translate if already in Marathi
            if self.detect_language(text) == 'mr':
                return text
                
            # If no API key, return original text
            if not self.api_key:
                logger.warning("No Google Translate API key provided, returning original text")
                return text
                
            url = f"{self.base_url}?key={self.api_key}"
            payload = {
                "q": text,
                "source": "en",
                "target": "mr",
                "format": "text"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result["data"]["translations"][0]["translatedText"]
                return translated_text
            else:
                logger.error(f"Translation to Marathi failed: {response.status_code}")
                return text  # Return original text on API error
                
        except Exception as e:
            logger.error(f"Translation to Marathi failed: {e}")
            return text  # Return original text on error

# Create a singleton instance
language_processor = LanguageProcessor()

# Backward compatibility functions
def detect_language(text: str) -> str:
    """Backward compatibility function"""
    return language_processor.detect_language(text)

def translate_to_english(text: str) -> str:
    """Backward compatibility function"""
    return language_processor.translate_to_english(text)

def translate_to_marathi(text: str) -> str:
    """Backward compatibility function"""
    return language_processor.translate_to_marathi(text)
