# app/__init__.py
"""
AI Agriculture Chatbot Package

A bilingual (English/Marathi) AI-powered chatbot specifically designed 
for farmers in Maharashtra, India. Provides agricultural advice, 
market information, weather guidance, and government scheme details.
"""

__version__ = "1.0.0"
__author__ = "AI Agriculture Chatbot Team"
__email__ = "support@aiagrichatbot.com"

import logging
from app.config import Config
from app.utils import setup_logging

# Setup logging when package is imported
logger = setup_logging(Config.LOG_LEVEL, Config.LOG_FILE)
logger.info(f"AI Agriculture Chatbot v{__version__} package initialized")
