import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    text = text.strip()
    
    return text

def is_agriculture_related(text: str) -> bool:
    """Check if query is agriculture-related"""
    agriculture_keywords = [
        # English keywords
        'crop', 'farm', 'agriculture', 'plant', 'seed', 'harvest', 'soil', 'fertilizer',
        'pesticide', 'irrigation', 'weather', 'rain', 'drought', 'yield', 'market', 'price',
        'government', 'scheme', 'subsidy', 'loan', 'insurance', 'cultivation', 'farming',
        
        # Marathi keywords
        'शेती', 'पीक', 'बियाणे', 'खत', 'कीटकनाशक', 'पाणी', 'पाऊस', 'हवामान', 'बाजार', 'भाव',
        'सरकार', 'योजना', 'अनुदान', 'कर्ज', 'विमा', 'लागवड', 'शेतकरी', 'माती', 'कापणी'
    ]
    
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in agriculture_keywords)

def log_conversation(user_input: str, bot_response: str, language: str, session_id: str = None):
    """Log conversation for analysis and improvement"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id,
        'user_input': user_input,
        'bot_response': bot_response,
        'language': language,
        'is_agriculture_related': is_agriculture_related(user_input)
    }
    
    log_file = 'data/logs/chat_logs.json'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    try:
        # Read existing logs
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logging.error(f"Failed to log conversation: {e}")

def load_knowledge_base() -> Dict[str, Any]:
    """Load agricultural knowledge base"""
    knowledge_file = 'data/farming_knowledge.json'
    
    try:
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load knowledge base: {e}")
    
    # Return default knowledge base
    return {
        "crops": {
            "rice": {"season": "kharif", "water_requirement": "high"},
            "wheat": {"season": "rabi", "water_requirement": "medium"},
            "cotton": {"season": "kharif", "water_requirement": "high"},
            "sugarcane": {"season": "year_round", "water_requirement": "very_high"}
        },
        "seasons": {
            "kharif": {"months": "June-October", "crops": ["rice", "cotton", "sugarcane"]},
            "rabi": {"months": "November-April", "crops": ["wheat", "gram", "mustard"]},
            "zaid": {"months": "April-June", "crops": ["watermelon", "cucumber"]}
        }
    }

def create_response_template(message: str, language: str = 'mr', status: str = 'success') -> Dict[str, Any]:
    """Create standardized response template"""
    return {
        'response': message,
        'language': language,
        'status': status,
        'timestamp': datetime.now().isoformat()
    }

def validate_input(text: str, max_length: int = 1000) -> tuple[bool, str]:
    """Validate user input"""
    if not text or not text.strip():
        return False, "Empty input provided"
    
    if len(text) > max_length:
        return False, f"Input too long. Maximum {max_length} characters allowed"
    
    # Check for potentially harmful content (basic check)
    harmful_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
    text_lower = text.lower()
    
    if any(pattern in text_lower for pattern in harmful_patterns):
        return False, "Potentially harmful content detected"
    
    return True, "Valid input"

def format_error_message(language: str = 'mr') -> str:
    """Get error message in appropriate language"""
    error_messages = {
        'mr': 'माफ करा, काहीतरी चूक झाली आहे. कृपया पुन्हा प्रयत्न करा.',
        'en': 'Sorry, something went wrong. Please try again.'
    }
    return error_messages.get(language, error_messages['mr'])

def get_welcome_message(language: str = 'mr') -> str:
    """Get welcome message in appropriate language"""
    welcome_messages = {
        'mr': 'नमस्कार मित्रा! मी कोती आहे. मी तुमच्या शेतीसंबंधी सर्व प्रश्नांची उत्तरे देण्यासाठी इथे आहे. पिके, हवामान, बाजारभाव, सरकारी योजना - काहीही विचारा!',
        'en': 'Hello friend! I am Koti. I am here to answer all your agriculture-related questions. Ask me about crops, weather, market prices, government schemes - anything!'
    }
    return welcome_messages.get(language, welcome_messages['mr'])