// AI Agri Chatbot - Frontend JavaScript

class AgriChatbot {
    constructor() {
        this.currentLanguage = 'mr'; // Default to Marathi
        this.isTyping = false;
        this.messageHistory = [];
        this.sessionId = localStorage.getItem('agri_chatbot_session_id') || null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadTranslations();
        this.initializeChat();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.languageSelect = document.getElementById('languageSelect');
        this.charCount = document.getElementById('charCount');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.errorToast = document.getElementById('errorToast');
        this.quickBtns = document.querySelectorAll('.quick-btn');
    }

    bindEvents() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Input events
        this.userInput.addEventListener('input', () => this.updateCharCount());
        this.userInput.addEventListener('focus', () => this.hideQuickActions());
        
        // Language change
        this.languageSelect.addEventListener('change', (e) => {
            this.changeLanguage(e.target.value);
        });

        // Quick action buttons
        this.quickBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = btn.getAttribute('data-query');
                this.userInput.value = query;
                this.sendMessage();
            });
        });
    }

    loadTranslations() {
        this.translations = {
            en: {
                welcome: "Welcome to AI Agri Assistant! I'm here to help you with farming questions, crop advice, and agricultural guidance. How can I assist you today?",
                placeholder: "Ask me anything about farming...",
                seasonBtn: "Seasonal Crops",
                soilBtn: "Soil Health",
                pestBtn: "Pest Control",
                weatherBtn: "Weather Tips",
                processing: "Processing your query...",
                errorMessage: "Something went wrong. Please try again.",
                typing: "AI is thinking..."
            },
            mr: {
                welcome: "AI कृषी सहाय्यकामध्ये आपले स्वागत आहे! मी शेतकरी प्रश्न, पीक सल्ला आणि कृषी मार्गदर्शनासाठी येथे आहे. आज मी तुमची कशी मदत करू शकतो?",
                placeholder: "शेतीबद्दल काहीही विचारा...",
                seasonBtn: "हंगामी पिके",
                soilBtn: "मातीचे आरोग्य",
                pestBtn: "कीड नियंत्रण",
                weatherBtn: "हवामान टिप्स",
                processing: "तुमची क्वेरी प्रक्रिया करत आहे...",
                errorMessage: "काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा.",
                typing: "AI विचार करत आहे..."
            }
        };
    }

    async initializeChat() {
        this.updateCharCount();
        
        // Check if there's a saved language preference
        const savedLanguage = localStorage.getItem('agri_chatbot_language');
        if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'mr')) {
            this.currentLanguage = savedLanguage;
            this.languageSelect.value = savedLanguage;
        }
        
        this.updateUILanguage();
        
        // Get welcome message from server
        try {
            const response = await this.fetchWelcomeMessage();
            if (response && response.message) {
                document.getElementById('welcomeMessage').textContent = response.message;
                
                // Save session ID if provided
                if (response.session_id) {
                    this.sessionId = response.session_id;
                    localStorage.setItem('agri_chatbot_session_id', this.sessionId);
                }
            }
        } catch (error) {
            console.error('Failed to fetch welcome message:', error);
        }
        
        this.scrollToBottom();
    }

    async fetchWelcomeMessage() {
        try {
            const response = await fetch(`/api/welcome?lang=${this.currentLanguage}&session_id=${this.sessionId || ''}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Welcome message error:', error);
            return null;
        }
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isTyping) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.updateCharCount();
        this.hideQuickActions();
        
        // Show typing indicator
        this.showTyping();        try {
            const response = await this.callChatbotAPI(message);
            this.hideTyping();
            
            if (response) {
                // Get the answer from the response
                let botAnswer = '';
                if (response.answer) {
                    botAnswer = response.answer;
                } else if (response.response) {
                    botAnswer = response.response;
                } else if (typeof response === 'string') {
                    botAnswer = response;
                } else {
                    throw new Error('Invalid response format');
                }
                
                this.addMessage(botAnswer, 'bot');
                
                // Store in message history
                this.messageHistory.push({
                    user: message,
                    bot: botAnswer,
                    timestamp: new Date().toISOString(),
                    language: this.currentLanguage
                });
                
                // Update session ID if provided
                if (response.session_id && !this.sessionId) {
                    this.sessionId = response.session_id;
                    localStorage.setItem('agri_chatbot_session_id', this.sessionId);
                }
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            this.hideTyping();
            this.showError(this.translations[this.currentLanguage].errorMessage);
            console.error('Chat error:', error);
        }
    }

    async callChatbotAPI(message) {
        try {
            // First try the main chat API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    language: this.currentLanguage
                })
            });

            if (response.ok) {
                return await response.json();
            }
            
            // Fallback to the direct generate API if main API fails
            console.log("Falling back to direct generate API");
            const fallbackResponse = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: message
                })
            });

            if (!fallbackResponse.ok) {
                throw new Error(`HTTP error! status: ${fallbackResponse.status}`);
            }

            return await fallbackResponse.json();
        } catch (error) {
            console.error("API call failed:", error);
            throw error;
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process message content (handle markdown, links, etc.)
        const processedContent = this.processMessageContent(content);
        contentDiv.innerHTML = `<p>${processedContent}</p>`;
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add fade-in animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease-out';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
    }

    processMessageContent(content) {
        // Convert markdown-style formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    }

    showTyping() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.sendBtn.disabled = true;
        this.sendBtn.style.opacity = '0.6';
        this.userInput.disabled = true;
    }

    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
        this.sendBtn.disabled = false;
        this.sendBtn.style.opacity = '1';
        this.userInput.disabled = false;
        this.userInput.focus();
    }

    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        this.errorToast.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.errorToast.style.display = 'none';
    }

    updateCharCount() {
        const length = this.userInput.value.length;
        this.charCount.textContent = `${length}/500`;
        
        if (length > 450) {
            this.charCount.style.color = '#F44336';
        } else if (length > 400) {
            this.charCount.style.color = '#FF9800';
        } else {
            this.charCount.style.color = '#666666';
        }
    }

    hideQuickActions() {
        const quickActions = document.querySelector('.quick-actions');
        if (quickActions && this.messageHistory.length > 0) {
            quickActions.style.display = 'none';
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    changeLanguage(newLanguage) {
        this.currentLanguage = newLanguage;
        this.updateUILanguage();
        
        // Save language preference
        localStorage.setItem('agri_chatbot_language', newLanguage);
    }

    updateUILanguage() {
        const lang = this.translations[this.currentLanguage];
        
        // Update UI elements
        document.getElementById('welcomeMessage').textContent = lang.welcome;
        this.userInput.placeholder = lang.placeholder;
        document.getElementById('seasonBtn').textContent = lang.seasonBtn;
        document.getElementById('soilBtn').textContent = lang.soilBtn;
        document.getElementById('pestBtn').textContent = lang.pestBtn;
        document.getElementById('weatherBtn').textContent = lang.weatherBtn;
        
        // Update dynamic elements
        const processingText = document.querySelector('.loading-spinner p');
        if (processingText) {
            processingText.textContent = lang.processing;
        }
        
        document.getElementById('typingIndicator').innerHTML = `<i class="fas fa-robot"></i> ${lang.typing}`;
    }
}

// Global error handler function
function hideError() {
    document.getElementById('errorToast').style.display = 'none';
}

// Initialize the chatbot when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new AgriChatbot();
});
