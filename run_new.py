# run.py - Application Runner
"""
AI Agriculture Chatbot Application Runner

This script starts the Flask application with proper error handling
and logging. It serves as the main entry point for the application.

Usage:
    python run_new.py

Environment Variables:
    FLASK_ENV: development/production (default: production)
    PORT: Port number (default: 5000)
    HOST: Host address (default: 0.0.0.0)
    GEMINI_API_KEY: Required - Your Google Gemini API key
    GOOGLE_TRANSLATE_API_KEY: Optional - Your Google Translate API key
"""

import os
import sys
import logging
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Replace the translator.py with our new implementation
translator_new_path = os.path.join(project_root, 'app', 'translator_new.py')
translator_path = os.path.join(project_root, 'app', 'translator.py')
translator_backup_path = os.path.join(project_root, 'app', 'translator.py.bak')

# Create backup of original translator.py if it doesn't exist
if os.path.exists(translator_path) and not os.path.exists(translator_backup_path):
    shutil.copy2(translator_path, translator_backup_path)
    print(f"Created backup of original translator.py at {translator_backup_path}")

# Replace with new implementation
if os.path.exists(translator_new_path):
    shutil.copy2(translator_new_path, translator_path)
    print(f"Replaced translator.py with new implementation")

try:
    from app.main import app
    from app.config import Config
    from app.utils import setup_logging
    
    # Setup logging
    logger = setup_logging(Config.LOG_LEVEL, Config.LOG_FILE)
    
    # For testing purposes - if no Gemini API key, set a dummy one
    if not os.environ.get('GEMINI_API_KEY'):
        os.environ['GEMINI_API_KEY'] = 'dummy_key_for_testing'
        print("WARNING: Using dummy Gemini API key for testing purposes")
    
    def main():
        """Main application entry point"""
        try:
            # Validate configuration
            Config.validate_config()
            
            logger.info("="*50)
            logger.info("🌾 AI AGRICULTURE CHATBOT STARTING 🌾")
            logger.info("="*50)
            logger.info(f"Version: 1.0.0")
            logger.info(f"Environment: {Config.FLASK_ENV}")
            logger.info(f"Debug Mode: {Config.DEBUG}")
            logger.info(f"Host: {Config.HOST}")
            logger.info(f"Port: {Config.PORT}")
            logger.info(f"Model: {Config.GEMINI_MODEL}")
            logger.info("="*50)
            
            # Start the Flask application
            app.run(
                host=Config.HOST,
                port=Config.PORT,
                debug=Config.DEBUG,
                threaded=True,
                use_reloader=Config.DEBUG  # Only use reloader in debug mode
            )
            
        except ValueError as e:
            logger.error(f"Configuration Error: {e}")
            logger.error("Please check your .env file and ensure GEMINI_API_KEY is set")
            sys.exit(1)
            
        except KeyboardInterrupt:
            logger.info("Application stopped by user")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}", exc_info=True)
            sys.exit(1)
    
    if __name__ == '__main__':
        main()

except ImportError as e:
    print(f"Error importing application modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"Unexpected error during startup: {e}")
    sys.exit(1)
