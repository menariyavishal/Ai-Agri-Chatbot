import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.translator import language_processor
from app.answer_generator import answer_generator
from app.utils import (
    validate_input, 
    log_conversation, 
    create_response_template,
    format_error_message,
    get_welcome_message,
    is_agriculture_related
)

logger = logging.getLogger(__name__)

class AgriChatbot:
    """Main chatbot orchestrator that handles the complete conversation flow"""
    
    def __init__(self):
        self.session_data = {}
        logger.info("AgriChatbot initialized successfully")
    
    def create_session(self) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        self.session_data[session_id] = {
            'created_at': datetime.now().isoformat(),
            'conversation_count': 0,
            'preferred_language': 'mr',  # Default to Marathi
            'last_activity': datetime.now().isoformat()
        }
        logger.info(f"New session created: {session_id}")
        return session_id
    
    def get_welcome_response(self, session_id: str = None, language: str = 'mr') -> Dict[str, Any]:
        """Get welcome message for new users"""
        if not session_id:
            session_id = self.create_session()
        
        # Update session language preference
        if session_id in self.session_data:
            self.session_data[session_id]['preferred_language'] = language
        
        welcome_msg = get_welcome_message(language)
        
        return {
            'response': welcome_msg,
            'language': language,
            'status': 'success',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'is_welcome': True
        }
    
    def process_query(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """
        Main method to process user queries through the complete pipeline:
        1. Input validation
        2. Language detection
        3. Translation (if needed)
        4. AI response generation
        5. Response translation (if needed)
        6. Logging
        """
        
        # Create session if not provided
        if not session_id:
            session_id = self.create_session()
        
        try:
            # Step 1: Input validation
            is_valid, validation_message = validate_input(user_input)
            if not is_valid:
                logger.warning(f"Invalid input: {validation_message}")
                return create_response_template(
                    format_error_message('mr'),
                    'mr',
                    'error'
                )
            
            # Step 2: Language processing
            processed_text, detected_language, original_text = language_processor.process_query(user_input)
            
            # Update session data
            self._update_session(session_id, detected_language)
            
            # Step 3: Check if query is agriculture-related
            if not is_agriculture_related(original_text):
                redirect_response = self._get_redirect_response(detected_language)
                
                # Log the interaction
                log_conversation(
                    user_input=original_text,
                    bot_response=redirect_response,
                    language=detected_language,
                    session_id=session_id
                )
                
                return create_response_template(
                    redirect_response,
                    detected_language,
                    'redirect'
                )
            
            # Step 4: Generate AI response
            logger.info(f"Generating response for query: '{processed_text[:50]}...'")
            
            # Generate response in English (Gemini works better with English)
            ai_response = answer_generator.generate_response(processed_text, 'en')
            
            # Step 5: Translate response if needed
            final_response = language_processor.process_response(ai_response, detected_language)
            
            # Step 6: Log conversation
            log_conversation(
                user_input=original_text,
                bot_response=final_response,
                language=detected_language,
                session_id=session_id
            )
            
            # Step 7: Create response
            response_data = create_response_template(
                final_response,
                detected_language,
                'success'
            )
            response_data['session_id'] = session_id
            
            logger.info(f"Query processed successfully for session {session_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            
            # Determine language for error message
            try:
                _, detected_lang, _ = language_processor.process_query(user_input)
            except:
                detected_lang = 'mr'  # Default fallback
            
            error_response = format_error_message(detected_lang)
            
            # Log the error
            log_conversation(
                user_input=user_input,
                bot_response=f"ERROR: {str(e)}",
                language=detected_lang,
                session_id=session_id
            )
            
            return create_response_template(
                error_response,
                detected_lang,
                'error'
            )
    
    def _update_session(self, session_id: str, detected_language: str):
        """Update session data with new interaction"""
        if session_id in self.session_data:
            self.session_data[session_id].update({
                'last_activity': datetime.now().isoformat(),
                'conversation_count': self.session_data[session_id]['conversation_count'] + 1,
                'preferred_language': detected_language
            })
        else:
            # Create session if it doesn't exist
            self.session_data[session_id] = {
                'created_at': datetime.now().isoformat(),
                'conversation_count': 1,
                'preferred_language': detected_language,
                'last_activity': datetime.now().isoformat()
            }
    
    def _get_redirect_response(self, language: str) -> str:
        """Get response for non-agriculture queries"""
        redirect_messages = {
            'mr': """मी कोती आहे - तुमचा शेती सहायक! 🌾
            
मी फक्त शेतीशी संबंधित प्रश्नांची उत्तरे देतो:
• पिकांची माहिती (भात, गहू, कापूस, ऊस इ.)
• हवामान आणि हंगामी सल्ले
• बाजारभाव आणि विक्री
• सरकारी योजना आणि अनुदान
• मातीची काळजी आणि खते
• कीटक आणि रोग व्यवस्थापन

कृपया मला शेतीबद्दल विचारा! 🚜""",
            
            'en': """I am Koti - your agriculture assistant! 🌾
            
I only answer agriculture-related questions about:
• Crop information (Rice, Wheat, Cotton, Sugarcane etc.)
• Weather and seasonal advice
• Market prices and sales
• Government schemes and subsidies
• Soil care and fertilizers
• Pest and disease management

Please ask me about farming! 🚜"""
        }
        
        return redirect_messages.get(language, redirect_messages['mr'])
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.session_data.get(session_id)
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up sessions older than specified hours"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session_data in self.session_data.items():
            try:
                last_activity = datetime.fromisoformat(session_data['last_activity'])
                if (current_time - last_activity).total_seconds() > (hours * 3600):
                    sessions_to_remove.append(session_id)
            except:
                # Remove sessions with invalid timestamps
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.session_data[session_id]
            logger.info(f"Cleaned up old session: {session_id}")
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics"""
        total_sessions = len(self.session_data)
        total_conversations = sum(
            session['conversation_count'] 
            for session in self.session_data.values()
        )
        
        # Language distribution
        language_stats = {'mr': 0, 'en': 0}
        for session in self.session_data.values():
            lang = session.get('preferred_language', 'mr')
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'total_conversations': total_conversations,
            'language_distribution': language_stats,
            'active_sessions': total_sessions
        }

# Global chatbot instance
chatbot = AgriChatbot()

# Convenience functions for backward compatibility
def process_user_query(user_input: str, session_id: str = None) -> Dict[str, Any]:
    """Convenience function to process user query"""
    return chatbot.process_query(user_input, session_id)

def get_welcome_message_response(session_id: str = None, language: str = 'mr') -> Dict[str, Any]:
    """Convenience function to get welcome message"""
    return chatbot.get_welcome_response(session_id, language)