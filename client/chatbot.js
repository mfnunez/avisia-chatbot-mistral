/**
 * Avisia Chatbot - GTM-Injected AI Assistant (Mistral AI Edition)
 * Vanilla JavaScript implementation with smart content extraction
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        API_ENDPOINT: 'YOUR_CLOUD_RUN_URL', // Replace with your Cloud Run URL
        POSITION: 'bottom-right', // Options: bottom-right, bottom-left, top-right, top-left
        PRIMARY_COLOR: '#4285f4',
        STORAGE_KEY: 'avisia_chatbot_history',
        MAX_MESSAGES: 20,
        EXTRACTION_DELAY: 1000 // Wait for dynamic content to load
    };

    // State management
    let conversationHistory = [];
    let isOpen = false;
    let isLoading = false;
    let pageContent = '';

    /**
     * Smart Content Extraction
     * Extracts main content while filtering out navigation, ads, and irrelevant elements
     */
    function extractPageContent() {
        // Selectors to exclude (navigation, ads, scripts, etc.)
        const excludeSelectors = [
            'nav', 'header', 'footer', 'aside',
            '[role="navigation"]', '[role="banner"]', '[role="complementary"]',
            '.nav', '.navbar', '.menu', '.sidebar',
            '.advertisement', '.ad', '.ads', '.promo',
            'script', 'style', 'noscript', 'iframe',
            '[class*="cookie"]', '[id*="cookie"]',
            '[class*="popup"]', '[class*="modal"]',
            '.chatbot', '#avisia-chatbot' // Exclude the chatbot itself
        ];

        // Selectors to prioritize (main content areas)
        const prioritySelectors = [
            'main',
            'article',
            '[role="main"]',
            '.content', '.main-content', '#content',
            '.article', '.post', '.entry'
        ];

        let content = '';

        // Try to extract from priority areas first
        for (const selector of prioritySelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach(el => {
                    // Remove excluded elements from this section
                    const clone = el.cloneNode(true);
                    excludeSelectors.forEach(excludeSelector => {
                        clone.querySelectorAll(excludeSelector).forEach(e => e.remove());
                    });
                    content += clone.innerText + '\n\n';
                });

                if (content.trim().length > 100) {
                    return cleanContent(content);
                }
            }
        }

        // Fallback: extract from body and filter
        const bodyClone = document.body.cloneNode(true);

        // Remove excluded elements
        excludeSelectors.forEach(selector => {
            bodyClone.querySelectorAll(selector).forEach(el => el.remove());
        });

        content = bodyClone.innerText;
        return cleanContent(content);
    }

    /**
     * Clean and normalize extracted content
     */
    function cleanContent(text) {
        return text
            .replace(/\s+/g, ' ') // Normalize whitespace
            .replace(/\n\s*\n\s*\n/g, '\n\n') // Remove excessive line breaks
            .trim()
            .substring(0, 50000); // Limit to 50k chars
    }

    /**
     * Load conversation history from session storage
     */
    function loadHistory() {
        try {
            const stored = sessionStorage.getItem(CONFIG.STORAGE_KEY);
            if (stored) {
                conversationHistory = JSON.parse(stored);
            }
        } catch (e) {
            console.warn('Failed to load chat history:', e);
        }
    }

    /**
     * Save conversation history to session storage
     */
    function saveHistory() {
        try {
            // Keep only last MAX_MESSAGES
            if (conversationHistory.length > CONFIG.MAX_MESSAGES) {
                conversationHistory = conversationHistory.slice(-CONFIG.MAX_MESSAGES);
            }
            sessionStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(conversationHistory));
        } catch (e) {
            console.warn('Failed to save chat history:', e);
        }
    }

    /**
     * Create chatbot UI
     */
    function createChatbotUI() {
        // Create container
        const container = document.createElement('div');
        container.id = 'avisia-chatbot';
        container.className = `avisia-chatbot-container ${CONFIG.POSITION}`;

        container.innerHTML = `
            <div class="avisia-chatbot-widget ${isOpen ? 'open' : ''}">
                <div class="avisia-chatbot-header">
                    <div class="avisia-chatbot-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                        <span>Ask about this page</span>
                    </div>
                    <button class="avisia-chatbot-close" aria-label="Close chat">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="avisia-chatbot-messages" id="avisia-chatbot-messages">
                    <div class="avisia-message avisia-message-assistant">
                        <div class="avisia-message-content">
                            Hi! I'm here to help you with any questions about this page. What would you like to know?
                        </div>
                    </div>
                </div>
                <div class="avisia-chatbot-input-area">
                    <input
                        type="text"
                        class="avisia-chatbot-input"
                        id="avisia-chatbot-input"
                        placeholder="Ask a question..."
                        autocomplete="off"
                    />
                    <button class="avisia-chatbot-send" id="avisia-chatbot-send" aria-label="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
            <button class="avisia-chatbot-toggle" id="avisia-chatbot-toggle" aria-label="Open chat">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
                <span class="avisia-chatbot-badge" id="avisia-chatbot-badge" style="display: none;">1</span>
            </button>
        `;

        document.body.appendChild(container);

        // Attach event listeners
        attachEventListeners();

        // Restore conversation history
        loadHistory();
        renderHistory();
    }

    /**
     * Attach event listeners
     */
    function attachEventListeners() {
        const toggle = document.getElementById('avisia-chatbot-toggle');
        const close = document.querySelector('.avisia-chatbot-close');
        const input = document.getElementById('avisia-chatbot-input');
        const send = document.getElementById('avisia-chatbot-send');

        toggle.addEventListener('click', toggleChat);
        close.addEventListener('click', toggleChat);
        send.addEventListener('click', sendMessage);

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    /**
     * Toggle chat open/closed
     */
    function toggleChat() {
        isOpen = !isOpen;
        const widget = document.querySelector('.avisia-chatbot-widget');
        const toggle = document.getElementById('avisia-chatbot-toggle');
        const badge = document.getElementById('avisia-chatbot-badge');

        if (isOpen) {
            widget.classList.add('open');
            toggle.style.display = 'none';
            document.getElementById('avisia-chatbot-input').focus();
            badge.style.display = 'none';
        } else {
            widget.classList.remove('open');
            toggle.style.display = 'flex';
        }
    }

    /**
     * Render conversation history
     */
    function renderHistory() {
        const messagesContainer = document.getElementById('avisia-chatbot-messages');

        // Clear except welcome message
        const welcomeMsg = messagesContainer.querySelector('.avisia-message-assistant');
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeMsg);

        conversationHistory.forEach(msg => {
            addMessageToUI(msg.role, msg.content, false);
        });

        scrollToBottom();
    }

    /**
     * Add message to UI
     */
    function addMessageToUI(role, content, shouldScroll = true) {
        const messagesContainer = document.getElementById('avisia-chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `avisia-message avisia-message-${role}`;

        messageDiv.innerHTML = `
            <div class="avisia-message-content">${escapeHtml(content)}</div>
        `;

        messagesContainer.appendChild(messageDiv);

        if (shouldScroll) {
            scrollToBottom();
        }
    }

    /**
     * Show loading indicator
     */
    function showLoading() {
        const messagesContainer = document.getElementById('avisia-chatbot-messages');
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'avisia-message avisia-message-assistant avisia-message-loading';
        loadingDiv.id = 'avisia-loading';

        loadingDiv.innerHTML = `
            <div class="avisia-message-content">
                <div class="avisia-loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;

        messagesContainer.appendChild(loadingDiv);
        scrollToBottom();
    }

    /**
     * Remove loading indicator
     */
    function removeLoading() {
        const loading = document.getElementById('avisia-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Scroll messages to bottom
     */
    function scrollToBottom() {
        const messagesContainer = document.getElementById('avisia-chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Send message to API
     */
    async function sendMessage() {
        const input = document.getElementById('avisia-chatbot-input');
        const message = input.value.trim();

        if (!message || isLoading) return;

        // Add user message to UI
        addMessageToUI('user', message);
        conversationHistory.push({ role: 'user', content: message });
        saveHistory();

        // Clear input
        input.value = '';

        // Show loading
        isLoading = true;
        showLoading();

        try {
            // Extract page content if not already done
            if (!pageContent) {
                pageContent = extractPageContent();
            }

            // Call API
            const response = await fetch(`${CONFIG.API_ENDPOINT}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    pageContent: pageContent,
                    pageUrl: window.location.href,
                    conversationHistory: conversationHistory.slice(0, -1) // Exclude current message
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            // Remove loading
            removeLoading();

            // Add assistant response
            addMessageToUI('assistant', data.response);
            conversationHistory.push({ role: 'assistant', content: data.response });
            saveHistory();

        } catch (error) {
            console.error('Chat error:', error);
            removeLoading();
            addMessageToUI('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            isLoading = false;
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    /**
     * Initialize chatbot
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Wait a bit for dynamic content to load
        setTimeout(() => {
            pageContent = extractPageContent();
            createChatbotUI();
        }, CONFIG.EXTRACTION_DELAY);
    }

    // Start initialization
    init();

})();
