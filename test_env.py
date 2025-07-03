"""
Test script to verify environment variables are loaded correctly.
Run this script to check if your API keys are accessible.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment
gemini_key = os.environ.get("GEMINI_API_KEY")
translate_key = os.environ.get("GOOGLE_TRANSLATE_API_KEY")

def mask_api_key(key):
    """Mask API key for secure display"""
    if not key:
        return "Not found"
    if len(key) <= 8:
        return "***" 
    return key[:4] + "..." + key[-4:]

print("\nEnvironment Variable Check")
print("-------------------------")
print(f"GEMINI_API_KEY: {mask_api_key(gemini_key)}")
print(f"GOOGLE_TRANSLATE_API_KEY: {mask_api_key(translate_key)}")
print("\nStatus:")
print(f"Gemini API Key: {'✓ Found' if gemini_key else '✗ Missing'}")
print(f"Translate API Key: {'✓ Found' if translate_key else '✗ Missing or not required'}")
print("\nNote: This script only checks if the variables are set, not if the keys are valid.")
print("-------------------------")
