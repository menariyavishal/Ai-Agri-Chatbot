// AI Agri Chatbot - Fixed Frontend JavaScript

class AgriChatbot {
    constructor() {
        this.currentLanguage = 'mr'; // Default to Marathi
        this.isTyping = false;
        this.messageHistory = [];
        this.sessionId = localStorage.getItem('agri_chatbot_session_id') || null;
        this.typingDelay = {min: 500, max: 3000}; // Realistic typing delay range
        this.typingSpeed = {min: 30, max: 90}; // Characters per second
        this.suggestionsVisible = false;
        this.debug = true; // Enable console logs for debugging
        
        this.initializeElements();
        this.bindEvents();
        this.loadTranslations();
        this.initializeChat();
        
        // Log initialization state
        if (this.debug) this.logInitializationState();
    }
    
    logInitializationState() {
        console.log('==== AgriChatbot Initialization ====');
        console.log('Sidebar Toggle:', this.sidebarToggle ? 'Found' : 'Missing');
        console.log('Sidebar:', this.sidebar ? 'Found' : 'Missing');
        console.log('Close Sidebar Button:', this.closeSidebar ? 'Found' : 'Missing');
        console.log('Sidebar Overlay:', this.sidebarOverlay ? 'Found' : 'Missing');
        console.log('Language Selector:', this.languageSelect ? 'Found' : 'Missing');
        console.log('====================================');
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.languageSelect = document.getElementById('languageSelect');
        this.charCount = document.getElementById('charCount');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.typingText = document.getElementById('typingText');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.processingText = document.getElementById('processingText');
        this.errorToast = document.getElementById('errorToast');
        this.quickBtns = document.querySelectorAll('.quick-btn');
        this.welcomeMessage = document.getElementById('welcomeMessage');
        this.quickActions = document.querySelector('.quick-actions');
        
        // Sidebar elements
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.sidebar = document.getElementById('sidebar');
        this.closeSidebar = document.getElementById('closeSidebar');
        this.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.currentLanguageDisplay = document.getElementById('currentLanguageDisplay');
        
        // Recent questions elements
        this.recentQuestions = document.getElementById('recentQuestions');
        this.suggestedQuestionsToggle = document.getElementById('suggestedQuestionsToggle');
        this.questionsList = document.getElementById('questionsList');
        
        // Check if all essential elements exist
        this.validateElements();
    }
    
    validateElements() {
        // Check if critical sidebar elements exist
        if (!this.sidebarToggle) {
            console.error('Error: Sidebar toggle button not found!');
            // Create the element if it doesn't exist
            this.sidebarToggle = document.createElement('div');
            this.sidebarToggle.id = 'sidebarToggle';
            this.sidebarToggle.className = 'sidebar-toggle';
            this.sidebarToggle.setAttribute('aria-label', 'Open settings menu');
            this.sidebarToggle.setAttribute('aria-expanded', 'false');
            this.sidebarToggle.innerHTML = '<i class="fas fa-globe"></i>';
            document.body.appendChild(this.sidebarToggle);
        }
        
        if (!this.sidebar) {
            console.error('Error: Sidebar not found!');
        }
        
        if (!this.closeSidebar) {
            console.error('Error: Close sidebar button not found!');
        }
        
        if (!this.sidebarOverlay) {
            console.error('Error: Sidebar overlay not found!');
            // Create the overlay if it doesn't exist
            this.sidebarOverlay = document.createElement('div');
            this.sidebarOverlay.id = 'sidebarOverlay';
            this.sidebarOverlay.className = 'sidebar-overlay';
            document.body.appendChild(this.sidebarOverlay);
        }
    }

    bindEvents() {
        // Send message events
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.userInput) {
            this.userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Input events
            this.userInput.addEventListener('input', () => {
                this.updateCharCount();
                // We'll implement suggestions later
                // this.checkForSuggestions();
            });
        }
        
        // Sidebar events
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent document click from firing
                this.toggleSidebar();
                if (this.debug) console.log('Sidebar toggle clicked');
            });
        }
        
        if (this.closeSidebar) {
            this.closeSidebar.addEventListener('click', () => {
                this.closeSidebarMenu();
                if (this.debug) console.log('Close sidebar clicked');
            });
        }
        
        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => {
                this.closeSidebarMenu();
                if (this.debug) console.log('Overlay clicked');
            });
        }
        
        // Collapsible menu for suggested questions
        if (this.suggestedQuestionsToggle) {
            this.suggestedQuestionsToggle.addEventListener('click', () => {
                this.toggleQuestionsList();
            });
        }
        
        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (this.sidebar && 
                this.sidebar.classList.contains('active') && 
                !this.sidebar.contains(e.target) && 
                e.target !== this.sidebarToggle) {
                this.closeSidebarMenu();
                if (this.debug) console.log('Outside clicked, closing sidebar');
            }
        });
        
        // Prevent clicks inside the sidebar from closing it
        if (this.sidebar) {
            this.sidebar.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // Language change
        if (this.languageSelect) {
            this.languageSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }

        // Quick action buttons
        this.quickBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                this.userInput.value = query;
                this.sendMessage();
            });
            
            // Add hover animation
            btn.addEventListener('mouseover', () => {
                btn.classList.add('hover-animation');
            });
            
            btn.addEventListener('mouseout', () => {
                btn.classList.remove('hover-animation');
            });
        });
        
        // Keyboard accessibility for chat history
        this.chatMessages.addEventListener('keydown', (e) => {
            if (e.key === 'Home') {
                this.chatMessages.scrollTop = 0;
            } else if (e.key === 'End') {
                this.scrollToBottom();
            }
        });
        
        // Sidebar toggle
        this.sidebarToggle.addEventListener('click', () => {
            this.toggleSidebar();
        });
        
        this.closeSidebar.addEventListener('click', () => {
            this.closeSidebarMenu();
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
                typing: "AI is thinking...",
                sendButtonLabel: "Send message",
                suggestedQuestions: "Suggested questions",
                timestamp: {
                    justNow: "Just now",
                    minutesAgo: " min ago",
                    hoursAgo: " hrs ago",
                    today: "Today at "
                }
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
                typing: "AI विचार करत आहे...",
                sendButtonLabel: "संदेश पाठवा",
                suggestedQuestions: "सुचवलेले प्रश्न",
                timestamp: {
                    justNow: "आत्ताच",
                    minutesAgo: " मिनिटांपूर्वी",
                    hoursAgo: " तासांपूर्वी",
                    today: "आज "
                }
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
        
        // Ensure quick actions are visible initially
        if (this.quickActions) {
            this.quickActions.style.display = 'flex';
            this.quickActions.setAttribute('data-moved', 'false');
        }
        
        // Ensure recent questions are hidden initially
        if (this.recentQuestions) {
            this.recentQuestions.style.display = 'none';
        }
        
        // Get welcome message from server
        try {
            const response = await this.fetchWelcomeMessage();
            if (response && response.message) {
                this.welcomeMessage.innerHTML = this.processMessageContent(response.message);
                
                // Save session ID if provided
                if (response.session_id) {
                    this.sessionId = response.session_id;
                    localStorage.setItem('agri_chatbot_session_id', this.sessionId);
                }
            }
        } catch (error) {
            console.error('Failed to fetch welcome message:', error);
        }
        
        // Focus on input field
        setTimeout(() => {
            this.userInput.focus();
        }, 500);
        
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
        
        // Check if this is the first user message
        if (this.messageHistory.filter(m => m.sender === 'user').length === 1) {
            // Move quick actions to sidebar after first user message
            this.moveQuickActionsToSidebar();
        } else {
            // Just hide quick actions for subsequent messages
            this.hideQuickActions();
        }
        
        // Show typing indicator with realistic delay
        this.showTyping();
        
        try {
            // Calculate a realistic typing delay based on message length
            const messageLength = message.length;
            const delayPerChar = Math.floor(Math.random() * 
                (this.typingSpeed.max - this.typingSpeed.min) + this.typingSpeed.min);
            const calculatedDelay = Math.min(
                this.typingDelay.max, 
                Math.max(this.typingDelay.min, messageLength * delayPerChar)
            );
            
            // Delay to simulate AI thinking and typing
            await new Promise(resolve => setTimeout(resolve, calculatedDelay));
            
            // Make API call to get response
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
        messageDiv.setAttribute('role', 'listitem');
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.setAttribute('aria-hidden', 'true');
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process message content (handle markdown, links, etc.)
        const processedContent = this.processMessageContent(content);
        
        // Create content container for proper styling
        const contentContainer = document.createElement('div');
        contentContainer.className = 'content-text';
        contentContainer.innerHTML = processedContent;
        contentDiv.appendChild(contentContainer);
        
        // Add timestamp
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = this.getFormattedTimestamp();
        contentDiv.appendChild(timestampDiv);
        
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
        if (!content) return '';
        
        // Convert markdown-style formatting to HTML with enhanced formatting
        return content
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code/monospace
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Lists - Ordered
            .replace(/^\d+\.\s+(.*?)(?=(\n|$))/gm, '<li>$1</li>')
            .replace(/(<li>.*?<\/li>)+/g, '<ol>$&</ol>')
            // Lists - Unordered
            .replace(/^-\s+(.*?)(?=(\n|$))/gm, '<li>$1</li>')
            .replace(/(<li>.*?<\/li>)+/g, function(match) {
                return match.includes('<ol>') ? match : '<ul>' + match + '</ul>';
            })
            // Headers
            .replace(/^#{3}\s+(.*?)(?=(\n|$))/gm, '<h3>$1</h3>')
            .replace(/^#{2}\s+(.*?)(?=(\n|$))/gm, '<h2>$1</h2>')
            .replace(/^#{1}\s+(.*?)(?=(\n|$))/gm, '<h1>$1</h1>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
            // Basic URLs (not in markdown link format)
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
            // Line breaks
            .replace(/\n/g, '<br>');
    }

    getFormattedTimestamp() {
        const now = new Date();
        const translations = this.translations[this.currentLanguage].timestamp;
        
        return translations.justNow;
    }

    showTyping() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.typingText.textContent = this.translations[this.currentLanguage].typing;
        this.sendBtn.disabled = true;
        this.sendBtn.style.opacity = '0.6';
        this.userInput.disabled = true;
        
        // Add typing animation
        const dotsElem = document.createElement('span');
        dotsElem.className = 'typing-dots';
        dotsElem.innerHTML = '<span>.</span><span>.</span><span>.</span>';
        this.typingText.appendChild(dotsElem);
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
            this.charCount.style.color = 'var(--error-color, #E74C3C)';
        } else if (length > 400) {
            this.charCount.style.color = 'var(--warning-color, #F39C12)';
        } else {
            this.charCount.style.color = 'var(--text-secondary, #555F60)';
        }
    }

    hideQuickActions() {
        if (!this.quickActions) return;
        
        if (this.messageHistory.length > 0) {
            // Only hide if we haven't already moved to sidebar
            if (this.quickActions.getAttribute('data-moved') !== 'true') {
                this.quickActions.style.display = 'none';
            }
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    // Sidebar Methods
    toggleSidebar() {
        // Ensure all sidebar elements exist
        if (!this.sidebar || !this.sidebarToggle) {
            console.error('Cannot toggle sidebar: Elements not found');
            return;
        }
        
        this.sidebar.classList.toggle('active');
        
        // Add accessibility attributes for screen readers
        const isExpanded = this.sidebar.classList.contains('active');
        this.sidebarToggle.setAttribute('aria-expanded', isExpanded);
        
        // Show/hide overlay
        if (this.sidebarOverlay) {
            if (isExpanded) {
                this.sidebarOverlay.style.visibility = 'visible';
                this.sidebarOverlay.style.opacity = '1';
            } else {
                this.sidebarOverlay.style.opacity = '0';
                setTimeout(() => {
                    this.sidebarOverlay.style.visibility = 'hidden';
                }, 300); // Match transition duration
            }
        }
        
        // Handle scroll locking
        if (isExpanded) {
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        } else {
            document.body.style.overflow = ''; // Restore scrolling
        }
    }
    
    closeSidebarMenu() {
        if (!this.sidebar) {
            return;
        }
        
        this.sidebar.classList.remove('active');
        this.sidebarToggle.setAttribute('aria-expanded', false);
        
        // Hide overlay
        if (this.sidebarOverlay) {
            this.sidebarOverlay.style.opacity = '0';
            setTimeout(() => {
                this.sidebarOverlay.style.visibility = 'hidden';
            }, 300); // Match transition duration
        }
        
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    openSidebarMenu() {
        this.sidebar.classList.add('open');
        this.sidebarToggle.setAttribute('aria-expanded', 'true');
        this.closeSidebar.setAttribute('aria-hidden', 'false');
        
        // Trap focus inside the sidebar
        this.trapFocus(this.sidebar);
        
        // Close the sidebar if clicked outside
        setTimeout(() => {
            document.addEventListener('click', this.handleClickOutsideSidebar);
        }, 0);
    }

    handleClickOutsideSidebar = (event) => {
        const isClickInside = this.sidebar.contains(event.target) || this.sidebarToggle.contains(event.target);
        if (!isClickInside) {
            this.closeSidebarMenu();
        }
    }

    trapFocus(element) {
        const focusableSelectors = 'a[href], area[href], iframe[tabindex], [tabindex]:not([tabindex="-1"]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])';
        const focusableElements = element.querySelectorAll(focusableSelectors);
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        element.addEventListener('keydown', function trapTabKey(e) {
            const isTabPressed = (e.key === 'Tab' || e.keyCode === 9);
            if (!isTabPressed) return;

            if (e.shiftKey) { // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else { // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });
        
        // Focus the first element initially
        if (firstElement) {
            firstElement.focus();
        }
    }

    removeFocusTrap() {
        const focusableSelectors = 'a[href], area[href], iframe[tabindex], [tabindex]:not([tabindex="-1"]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])';
        const focusableElements = this.sidebar.querySelectorAll(focusableSelectors);
        
        focusableElements.forEach(el => {
            el.removeEventListener('keydown', this.handleTabKey);
        });
    }

    handleTabKey(e) {
        const isTabPressed = (e.key === 'Tab' || e.keyCode === 9);
        if (!isTabPressed) return;

        const focusableElements = this.sidebar.querySelectorAll('a[href], area[href], iframe[tabindex], [tabindex]:not([tabindex="-1"]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])');
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) { // Shift + Tab
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else { // Tab
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
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
        this.welcomeMessage.textContent = lang.welcome;
        this.userInput.placeholder = lang.placeholder;
        
        // Update current language display
        const selectedOption = this.languageSelect.options[this.languageSelect.selectedIndex];
        this.currentLanguageDisplay.textContent = `Current: ${selectedOption.text}`;
        
        // Update quick action buttons
        const seasonBtn = document.getElementById('seasonBtn');
        const soilBtn = document.getElementById('soilBtn');
        const pestBtn = document.getElementById('pestBtn');
        const weatherBtn = document.getElementById('weatherBtn');
        
        if (seasonBtn) seasonBtn.textContent = lang.seasonBtn;
        if (soilBtn) soilBtn.textContent = lang.soilBtn;
        if (pestBtn) pestBtn.textContent = lang.pestBtn;
        if (weatherBtn) weatherBtn.textContent = lang.weatherBtn;
        
        // Update dynamic elements
        if (this.processingText) this.processingText.textContent = lang.processing;
        if (this.typingText) this.typingText.textContent = lang.typing;
        this.sendBtn.setAttribute('aria-label', lang.sendButtonLabel);
    }
    
    // Toggle questions list collapsible
    toggleQuestionsList() {
        if (!this.suggestedQuestionsToggle) return;
        
        this.suggestedQuestionsToggle.classList.toggle('active');
        const content = this.suggestedQuestionsToggle.nextElementSibling;
        
        if (content.style.maxHeight) {
            content.style.maxHeight = null;
            this.suggestedQuestionsToggle.querySelector('span').textContent = "Show Suggestions";
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            this.suggestedQuestionsToggle.querySelector('span').textContent = "Hide Suggestions";
        }
    }
    
    // Move quick action buttons to sidebar after first message
    moveQuickActionsToSidebar() {
        if (!this.quickActions || !this.questionsList || !this.recentQuestions) {
            if (this.debug) console.log('Missing elements for moving quick actions');
            return;
        }
        
        // First check if we've already done this
        if (this.quickActions.getAttribute('data-moved') === 'true') {
            return;
        }
        
        // Get all the quick action buttons
        const questions = [];
        this.quickBtns.forEach(btn => {
            const query = btn.getAttribute('data-query');
            const icon = btn.querySelector('i').className;
            const text = btn.querySelector('span').textContent;
            questions.push({ query, icon, text });
        });
        
        // Create list items for each question
        questions.forEach(q => {
            const li = document.createElement('li');
            li.innerHTML = `
                <button class="question-item" data-query="${q.query}">
                    <i class="${q.icon}"></i>
                    ${q.text}
                </button>
            `;
            this.questionsList.appendChild(li);
            
            // Add click event to each question
            const button = li.querySelector('button');
            button.addEventListener('click', () => {
                this.userInput.value = q.query;
                this.sendMessage();
                this.closeSidebarMenu();
            });
        });
        
        // Show the recent questions section
        this.recentQuestions.style.display = 'block';
        
        // Hide the original quick actions
        this.quickActions.style.display = 'none';
        this.quickActions.setAttribute('data-moved', 'true');
        
        // Open the collapsible by default
        setTimeout(() => {
            this.toggleQuestionsList();
        }, 300);
    }
}

// Global error handler function
function hideError() {
    const errorToast = document.getElementById('errorToast');
    if (errorToast) {
        errorToast.style.display = 'none';
    }
}

// Initialize the chatbot when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new AgriChatbot();
});