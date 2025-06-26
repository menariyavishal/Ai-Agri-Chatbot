import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GOOGLE_TRANSLATE_API_KEY = os.environ.get("GOOGLE_TRANSLATE_API_KEY")
    
    # Model Configuration
    GEMINI_MODEL = "gemini-1.5-flash"
    
    # Generation Parameters
    GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    # Safety Settings
    SAFETY_SETTINGS = [
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
    
    # Application Settings
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'data/logs/app.log'
    
    # Chatbot Personality
    SYSTEM_PROMPTS = {
        'marathi': """तुम्ही कोती आहात, महाराष्ट्रातील शेतकऱ्यांसाठी एक AI सहायक. तुम्ही एका अनुभवी गावातील वडिलांसारखे बोलता आणि शेतकऱ्यांना त्यांच्या शेती, पिके, हवामान, बाजारभाव आणि सरकारी योजनांबद्दल मदत करता. तुम्ही नेहमी आदरपूर्वक, सोप्या भाषेत आणि व्यावहारिक सल्ले देता. जर प्रश्न मराठीत आहे तर उत्तर मराठीतच द्या.""",
        
        'english': """You are Koti, an AI assistant for farmers in Maharashtra, India. You speak like an experienced village elder and help farmers with their agriculture, crops, weather, market prices, and government schemes. You always respond respectfully, in simple language, and give practical advice. If the question is in English, respond in English.""",
        
        'bilingual': """You are Koti, a bilingual AI assistant for farmers in Maharashtra. You understand both English and Marathi and respond in the same language as the query. You act like an experienced village elder, helping farmers with agriculture, crops, weather, market prices, and government schemes. Always be respectful and give practical advice."""
    }
    
    # Translation Settings
    SUPPORTED_LANGUAGES = ['en', 'mr']  # English and Marathi
    DEFAULT_LANGUAGE = 'mr'  # Default to Marathi
    
    # Rate Limiting (future use)
    RATE_LIMIT_PER_MINUTE = 30
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file")
            
        if not cls.GOOGLE_TRANSLATE_API_KEY:
            import logging
            logging.warning("GOOGLE_TRANSLATE_API_KEY is not set. Translation features will use fallback mechanisms.")
        
    @classmethod
    def get_system_prompt(cls, language='bilingual'):
        """Get system prompt based on language"""
        return cls.SYSTEM_PROMPTS.get(language, cls.SYSTEM_PROMPTS['bilingual'])