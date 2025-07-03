# AI Agriculture Chatbot (Koti)

A bilingual chatbot for farmers built with Flask and Google Gemini AI. This chatbot, named "Koti," provides agricultural information and advice to farmers in English and Marathi.

## Features

- Provides agricultural information and advice in English and Marathi
- Specializes in crops, farming techniques, weather, market prices, and government schemes
- Character-based assistant with a unique personality (experienced village elder)
- Natural language processing capabilities to understand agricultural queries
- Secure API key management with environment variables
- Responsive, accessible web interface with mobile support
- Fallback mechanisms when AI service is unavailable

## Overview

The AI Agriculture Chatbot (Koti) is designed to assist farmers with agricultural questions. It leverages Google's Gemini AI to provide accurate, contextual information about farming practices, crop management, weather considerations, and more. The system uses a context-aware approach to maintain the character of "Koti," an experienced village elder who provides farming wisdom.

## Technical Architecture

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **AI**: Google Gemini AI (gemini-1.5-flash model)
- **Translation**: Google Translate API
- **Storage**: File-based logging and session management

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip package manager
- Google Gemini API key
- Google Translate API key (optional)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Copy `.env.example` to `.env`:
     ```
     cp .env.example .env
     ```
   - Open `.env` and replace placeholder values with your actual API keys
   - **Important**: Never commit your `.env` file to version control

### API Key Security

This application uses environment variables for secure API key management:

1. **Get your API keys**:
   - Gemini API key: https://makersuite.google.com/app/apikey
   - Google Translate API key: Google Cloud Console

2. **Set up your environment**:
   - Create a `.env` file at the project root (use `.env.example` as a template)
   - Add your API keys to this file
   - The `.gitignore` file excludes `.env` from version control

3. **Verify your configuration**:
   - Run `python test_env.py` to check if your API keys are correctly set up

### Running the Application

Start the application:

```
python run_new.py
```

The web interface will be available at http://127.0.0.1:5000

## Usage Guide

1. **Language Selection**: Choose between English and Marathi using the language selector in the sidebar
2. **Asking Questions**: Type your agriculture-related question in the chat input field
3. **Quick Actions**: Use the quick action buttons for common agricultural topics
4. **Suggested Questions**: After your first message, find suggested follow-up questions in the sidebar

## Project Structure

```
chatbot/
├── app/                # Application code
│   ├── __init__.py
│   ├── answer_generator.py  # Gemini AI integration
│   ├── chatbot.py      # Core chatbot logic
│   ├── config.py       # Configuration management
│   ├── main.py         # Flask application
│   ├── translator.py   # Language detection/translation
│   └── utils.py        # Utility functions
├── data/
│   └── logs/           # Application logs
├── webapp/             # Frontend files
│   ├── static/
│   │   ├── css/        # Stylesheets
│   │   └── js/         # JavaScript
│   └── templates/      # HTML templates
├── .env.example        # Example environment file
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
├── requirements.txt    # Dependencies
└── run_new.py          # Entry point
```

## Security Best Practices

- Regularly rotate your API keys
- Use different API keys for development and production
- Set up API key restrictions in Google Cloud Console
- Monitor your API usage
- Consider using a secrets manager for production environments

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- Google Gemini AI for powering the conversational capabilities
- Flask for the web framework
- All contributors to this project

