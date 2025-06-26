# AI Agri Chatbot - Project Summary

## Project Overview

The AI Agri Chatbot is a specialized assistant designed for farmers in Maharashtra, India, providing agricultural advice, market information, weather guidance, and details about government schemes. It features bilingual support (English and Marathi) and is powered by Google's Gemini AI model for intelligent responses.

## Key Features

- **Bilingual Support**: Fully supports both English and Marathi languages
- **Direct Gemini AI Integration**: Uses Google's Gemini API for generating relevant agricultural responses
- **Agriculture-Focused**: Specialized in farming topics with built-in topic verification
- **Modern Web Interface**: Responsive design with intuitive chat interface
- **Session Management**: Maintains conversation context across sessions
- **Quick Action Suggestions**: Provides common farming-related query shortcuts
- **Error Handling**: Robust error handling with user-friendly messages
- **Logging**: Comprehensive logging system for monitoring and improvement

## Project Structure

```
ai-agri-chatbot/
│
├── app/                            # Backend Logic
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Flask main application
│   ├── answer_generator.py         # Gemini AI integration
│   ├── chatbot.py                  # Legacy orchestration layer
│   ├── translator.py               # Language detection & translation
│   ├── config.py                   # Configuration management
│   └── utils.py                    # Helper functions
│
├── webapp/                         # Frontend
│   ├── static/                     # Static assets
│   │   ├── css/
│   │   │   └── style.css          # Enhanced styling
│   │   └── js/
│   │       └── script.js          # Frontend logic
│   └── templates/
│       └── index.html             # Main interface
│
├── data/                           # Data files
│   └── logs/                       # Application logs
│       ├── app.log                 # System logs
│       └── chat_logs.json          # Conversation logs
│
├── requirements.txt                # Dependencies
└── run_new.py                      # Application runner
```

## Code Flow

### Application Startup

1. **Initialization**: `run_new.py` is the entry point that:
   - Loads environment variables
   - Configures Python path
   - Imports and sets up the Flask application

2. **Configuration**: `app/config.py` manages:
   - API keys (Gemini, Google Translate)
   - Model parameters
   - Environment settings
   - Safety settings

3. **Logging Setup**: `app/utils.py` configures logging to both console and file

### Request Handling Flow

1. **Web Interface**: User interacts with `webapp/templates/index.html`
2. **API Endpoints**: Frontend JavaScript sends requests to one of the Flask endpoints:
   - `/api/chat` - Main conversation endpoint
   - `/generate` - Direct Gemini API access
   - `/api/welcome` - Welcome message retrieval

3. **Backend Processing**:
   - `app/main.py` routes the request to appropriate handlers
   - Language detection occurs via `app/translator.py`
   - AI response generation via `app/answer_generator.py`
   - Response is returned to the frontend

4. **Response Display**: Frontend JavaScript (`script.js`) updates the UI with the response

### AI Integration Flow

1. **Query Processing**:
   - User input is validated and cleaned
   - Language is detected (English or Marathi)
   - Topic relevance is checked (agricultural vs. non-agricultural)

2. **Prompt Enhancement**:
   - Relevant agricultural context is added to the prompt
   - Language-specific instructions are included

3. **Gemini API Call**:
   - Enhanced prompt is sent to Gemini model
   - Safety settings are applied
   - Generation parameters control response quality

4. **Response Handling**:
   - AI response is processed and formatted
   - Conversation is logged for analysis
   - Response is returned to the user

## Key Components

### Backend Components

1. **answer_generator.py**
   - Core AI functionality using Gemini API
   - Handles prompt construction and response generation
   - Implements agricultural relevance checking

2. **main.py**
   - Flask application with API endpoints
   - Request handling and routing
   - Error handling and session management

3. **utils.py**
   - Helper functions for text processing
   - Logging utilities
   - Agriculture-related keyword checking

4. **translator.py**
   - Language detection
   - Translation between English and Marathi
   - Uses Google Translate API

5. **config.py**
   - Centralized configuration management
   - Environment variables handling
   - Model and API settings

### Frontend Components

1. **index.html**
   - Modern responsive chat interface
   - Language selection
   - Quick action buttons

2. **script.js**
   - Frontend logic in AgriChatbot class
   - API communication
   - UI updates and animations
   - Session management

3. **style.css**
   - Responsive design
   - Color scheme and visual elements
   - Accessibility features

## API Endpoints

1. **`/api/chat`** (POST)
   - Main chat endpoint
   - Processes user messages and returns AI responses
   - Handles session tracking

2. **`/generate`** (POST)
   - Direct access to Gemini AI
   - Simplified interface for quick responses
   - Fallback endpoint

3. **`/api/welcome`** (GET)
   - Retrieves welcome message in specified language
   - Creates new session if needed

4. **`/api/session/info`** (GET)
   - Returns information about current session
   - Used for debugging and analytics

5. **`/api/health`** (GET)
   - System health check endpoint
   - Verifies API keys and service status

## Environment Variables

- **GEMINI_API_KEY**: Required - Google Gemini API key
- **GOOGLE_TRANSLATE_API_KEY**: Optional - Google Translate API key
- **FLASK_ENV**: development/production (default: production)
- **PORT**: Port number (default: 5000)
- **HOST**: Host address (default: 0.0.0.0)
- **LOG_LEVEL**: Logging level (default: INFO)

## Dependencies

- **Flask**: Web framework
- **Google Generative AI**: Gemini AI integration
- **Requests**: HTTP client for API calls
- **Python-dotenv**: Environment variable management
- **Flask-CORS**: Cross-origin resource sharing support

## Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables (`.env` file or system environment)
3. Run the application: `python run_new.py`
4. Access the web interface at http://localhost:5000

## Future Improvements

1. **Enhanced Analytics**: Track conversation quality and user satisfaction
2. **Expanded Knowledge Base**: Add more agricultural data specific to Maharashtra
3. **Offline Mode**: Implement basic functionality when internet connectivity is limited
4. **Voice Interface**: Add speech-to-text and text-to-speech capabilities
5. **Mobile App**: Develop companion mobile application
