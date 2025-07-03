import logging
import google.generativeai as genai
from typing import Optional, Dict, Any
from app.config import Config
from app.utils import is_agriculture_related, load_knowledge_base

logger = logging.getLogger(__name__)

class GeminiAnswerGenerator:
    """Gemini AI-powered answer generator for agricultural queries"""
    
    def __init__(self):
        self.model = None
        self.knowledge_base = load_knowledge_base()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model with configuration"""
        try:
            Config.validate_config()
            # Use environment variable only - no fallback
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                logger.error("No API key provided. Set GEMINI_API_KEY in environment variables or .env file")
                raise ValueError("Missing API key for Gemini model")
                
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            logger.info(f"Gemini model {Config.GEMINI_MODEL} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def _create_enhanced_prompt(self, user_query: str, language: str = 'en') -> str:
        """Create enhanced prompt with agricultural context"""
        
        # Base system prompt for Koti character
        system_prompt = """तुम्ही कोती आहात, महाराष्ट्रातील शेतकऱ्यांसाठी एक AI सहायक. तुम्ही एका अनुभवी गावातील वडिलांसारखे बोलता आणि शेतकऱ्यांना त्यांच्या शेती, पिके, हवामान, बाजारभाव आणि सरकारी योजनांबद्दल मदत करता."""
        
        if language == 'mr':
            system_prompt += " नेहमी मराठीत उत्तर द्या आणि आदरपूर्वक बोला."
        else:
            system_prompt += " Always respond in English and speak respectfully."
        
        # Check if query is agriculture-related
        if not is_agriculture_related(user_query):
            redirect_message = {
                'en': "I specialize in helping farmers with agricultural questions. Please ask me about farming, crops, weather, market prices, or government schemes for farmers.",
                'mr': "मी शेतकऱ्यांना शेतीच्या प्रश्नांमध्ये मदत करण्यात तज्ञ आहे. कृपया मला शेती, पिके, हवामान, बाजारभाव किंवा शेतकऱ्यांसाठी सरकारी योजनांबद्दल विचारा."
            }
            return redirect_message.get(language, redirect_message['en'])
        
        # Create full prompt
        full_prompt = f"{system_prompt}\n\nUser: {user_query}\nKoti:"
        
        return full_prompt
    
    def generate_response(self, user_query: str, language: str = 'mr') -> str:
        """Generate AI response to user query"""
        try:
            if not self.model:
                try:
                    self._initialize_model()
                except ValueError as e:
                    logger.error(f"Model initialization failed: {e}")
                    return self._get_api_key_missing_message(language)
            
            # Create prompt
            prompt = self._create_enhanced_prompt(user_query, language)
            
            # Check if we got a redirect message
            if prompt in ["I specialize in helping farmers with agricultural questions. Please ask me about farming, crops, weather, market prices, or government schemes for farmers.",
                        "मी शेतकऱ्यांना शेतीच्या प्रश्नांमध्ये मदत करण्यात तज्ञ आहे. कृपया मला शेती, पिके, हवामान, बाजारभाव किंवा शेतकऱ्यांसाठी सरकारी योजनांबद्दल विचारा."]:
                return prompt
            
            # Configure safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ]
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            
            # Check if response was blocked
            if not response.text:
                logger.warning("Response was blocked or empty")
                return self._get_fallback_response(user_query, language)
            
            # Clean and return response
            cleaned_response = response.text.strip()
            logger.info(f"Generated response: {cleaned_response[:100]}...")
            
            return cleaned_response
            
        except ValueError as e:
            if "API key" in str(e):
                logger.error(f"API key error: {e}")
                return self._get_api_key_missing_message(language)
            logger.error(f"Value error generating response: {e}")
            return self._get_fallback_response(user_query, language)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(user_query, language)
    
    def _get_fallback_response(self, user_query: str, language: str) -> str:
        """Provide fallback response when AI fails"""
        
        fallback_responses = {
            'en': "I apologize, but I'm having trouble processing your query right now. Please try rephrasing your question or contact our support team.",
            'mr': "माफ करा, सध्या मला तुमच्या प्रश्नाची उत्तरे देण्यात अडचण येत आहे. कृपया तुमचा प्रश्न पुन्हा विचारा किंवा आमच्या सहाय्यता टीमशी संपर्क साधा."
        }
        
        # Try to provide basic information based on keywords
        if is_agriculture_related(user_query):
            return self._get_basic_agriculture_info(user_query, language)
        
        return fallback_responses.get(language, fallback_responses['en'])
    
    def _get_basic_agriculture_info(self, user_query: str, language: str) -> str:
        """Provide basic agricultural information as fallback"""
        
        query_lower = user_query.lower()
        
        # Basic crop information
        if any(word in query_lower for word in ['rice', 'भात', 'तांदूळ']):
            responses = {
                'en': "Rice is a major Kharif crop in Maharashtra. Best planted during June-July with monsoon rains. Requires adequate water and fertile soil.",
                'mr': "भात हे महाराष्ट्रातील प्रमुख खरीप पीक आहे. जून-जुलैमध्ये पावसाळ्यात लावले जाते. पुरेसे पाणी आणि सुपीक मातीची गरज असते."
            }
            return responses.get(language, responses['en'])
        
        elif any(word in query_lower for word in ['cotton', 'कापूस']):
            responses = {
                'en': "Cotton is an important cash crop in Maharashtra. Planted during Kharif season. Requires warm climate and moderate rainfall.",
                'mr': "कापूस हे महाराष्ट्रातील महत्वाचे नगदी पीक आहे. खरीप हंगामात लावले जाते. उष्ण हवामान आणि मध्यम पावसाची गरज असते."
            }
            return responses.get(language, responses['en'])
        
        # Default fallback
        default_responses = {
            'en': "For specific agricultural advice, please contact your local agriculture extension officer or visit the nearest Krishi Vigyan Kendra.",
            'mr': "विशिष्ट शेती सल्ल्यासाठी, कृपया तुमच्या स्थानिक कृषी विस्तार अधिकाऱ्याशी संपर्क साधा किंवा जवळच्या कृषी विज्ञान केंद्राला भेट द्या."
        }
        
        return default_responses.get(language, default_responses['en'])
    
    def _get_api_key_missing_message(self, language: str) -> str:
        """Return a user-friendly message when API key is missing"""
        messages = {
            'en': "The AI service is currently unavailable. The system administrator needs to set up the API key. Please contact support for assistance.",
            'mr': "AI सेवा सध्या उपलब्ध नाही. सिस्टम प्रशासकाने API की सेट करणे आवश्यक आहे. कृपया मदतीसाठी सपोर्टशी संपर्क साधा."
        }
        return messages.get(language, messages['en'])

# Global instance
answer_generator = GeminiAnswerGenerator()

# Backward compatibility function
def get_answer(query: str, language: str = 'en') -> str:
    """Backward compatibility function"""
    return answer_generator.generate_response(query, language)