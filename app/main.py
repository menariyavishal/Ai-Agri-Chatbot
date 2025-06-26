from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import logging
import os
import uuid
from datetime import datetime

from app.config import Config
from app.chatbot import chatbot
from app.utils import setup_logging

# Initialize Flask app
app = Flask(__name__, 
           template_folder='../webapp/templates',
           static_folder='../webapp/static')

app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Enable CORS for API endpoints
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Setup logging
logger = setup_logging(Config.LOG_LEVEL, Config.LOG_FILE)

# Initialize application
logger.info("Initializing AI Agriculture Chatbot...")
logger.info(f"Environment: {Config.FLASK_ENV}")
logger.info(f"Debug mode: {Config.DEBUG}")

@app.route('/')
def index():
    """Serve the main chat interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_api():
    """Main chat API endpoint"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'status': 'error'
            }), 400
        
        user_input = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_input:
            return jsonify({
                'error': 'Empty message',
                'status': 'error'
            }), 400
        
        # Process the query using direct Gemini integration
        from app.answer_generator import answer_generator
        language = data.get('language', 'mr')  # Default to Marathi
        
        # Generate response
        answer = answer_generator.generate_response(user_input, language)
        
        # Create response
        response = {
            'answer': answer,
            'status': 'success',
            'session_id': session_id or str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add session ID to Flask session for web interface
        if 'session_id' not in session:
            session['session_id'] = response.get('session_id')
        
        logger.info(f"Chat API - Query processed successfully")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat API error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'status': 'error',
            'message': 'काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा.'
        }), 500

@app.route('/api/welcome', methods=['GET'])
def welcome_api():
    """Get welcome message"""
    try:
        language = request.args.get('lang', 'mr')
        session_id = request.args.get('session_id') or session.get('session_id')
        
        # Create a new session if none exists
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get appropriate welcome message
        from app.utils import get_welcome_message
        welcome_msg = get_welcome_message(language)
        
        response = {
            'message': welcome_msg,
            'language': language,
            'status': 'success',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store session ID
        if 'session_id' not in session:
            session['session_id'] = response.get('session_id')
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Welcome API error: {e}")
        return jsonify({
            'error': 'Failed to get welcome message',
            'status': 'error'
        }), 500

@app.route('/api/session/info', methods=['GET'])
def session_info_api():
    """Get session information"""
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id:
            return jsonify({
                'error': 'No session found',
                'status': 'error'
            }), 404
        
        session_info = chatbot.get_session_info(session_id)
        
        if not session_info:
            return jsonify({
                'error': 'Session not found',
                'status': 'error'
            }), 404
        
        return jsonify({
            'session_info': session_info,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Session info API error: {e}")
        return jsonify({
            'error': 'Failed to get session info',
            'status': 'error'
        }), 500

@app.route('/api/stats', methods=['GET'])
def stats_api():
    """Get chatbot statistics (for admin/monitoring)"""
    try:
        stats = chatbot.get_stats()
        return jsonify({
            'stats': stats,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'components': {
                'chatbot': 'healthy',
                'translator': 'healthy',
                'answer_generator': 'healthy'
            }
        }
        
        # Check if Gemini API key is configured
        if not Config.GEMINI_API_KEY:
            health_status['status'] = 'unhealthy'
            health_status['components']['answer_generator'] = 'missing_api_key'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/generate', methods=['POST'])
def generate_response():
    """Generate AI response using Gemini API directly"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        user_input = data.get('prompt', '').strip()
        
        if not user_input:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"Processing prompt: {user_input[:50]}...")
        
        # Generate response using Gemini
        from app.answer_generator import answer_generator
        response_text = answer_generator.generate_response(user_input, 'mr')
        
        logger.info("Response generated successfully")
        return jsonify({'response': response_text})
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'माफ करा, काहीतरी चूक झाली आहे. कृपया पुन्हा प्रयत्न करा.'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'API endpoint not found',
            'status': 'error'
        }), 404
    else:
        return render_template('index.html')  # Serve SPA for non-API routes

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500
    else:
        return "Internal server error. Please try again later.", 500

@app.before_request
def before_request():
    """Run before each request"""
    # Clean up old sessions periodically (every 100th request approximately)
    import random
    if random.randint(1, 100) == 1:
        chatbot.cleanup_old_sessions()

@app.after_request
def after_request(response):
    """Run after each request"""
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

if __name__ == '__main__':
    try:
        logger.info(f"Starting AI Agriculture Chatbot on {Config.HOST}:{Config.PORT}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise