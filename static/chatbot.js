// AI-Powered Steganography Chatbot
// Uses Hugging Face API through backend

// Chatbot state
let chatHistory = [];
let conversationHistory = [];
let isOpen = false;
let isWaitingForResponse = false;

// Initialize chatbot
function initChatbot() {
    createChatbotUI();
    attachEventListeners();

    // Add initial greeting
    addBotMessage("Hi! I'm your AI steganography assistant. Ask me anything about hiding messages in text or images!");
}

// Create chatbot UI elements
function createChatbotUI() {
    const chatbotHTML = `
        <div id="chatbot-container" class="chatbot-container">
            <div id="chatbot-toggle" class="chatbot-toggle" title="Chat with AI Assistant">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    <path d="M8 10h.01"></path>
                    <path d="M12 10h.01"></path>
                    <path d="M16 10h.01"></path>
                </svg>
            </div>

            <div id="chatbot-window" class="chatbot-window" style="display: none;">
                <div class="chatbot-header">
                    <div class="chatbot-header-info">
                        <div class="chatbot-avatar">🔐</div>
                        <div class="chatbot-header-text">
                            <h3>Stego Assistant</h3>
                            <span class="chatbot-status" id="chatbot-status">Online</span>
                        </div>
                    </div>
                    <button id="chatbot-close" class="chatbot-close">×</button>
                </div>

                <div id="chatbot-messages" class="chatbot-messages">
                </div>

                <div class="chatbot-input-container">
                    <input
                        type="text"
                        id="chatbot-input"
                        class="chatbot-input"
                        placeholder="Type a message..."
                        autocomplete="off"
                    >
                    <button id="chatbot-send" class="chatbot-send">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>

                <div class="chatbot-suggestions">
                    <button class="suggestion-btn" data-question="What is steganography?">What is steganography?</button>
                    <button class="suggestion-btn" data-question="How do I hide a message in an image?">Hide in image</button>
                    <button class="suggestion-btn" data-question="What is LSB encoding?">LSB encoding</button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
}

// Attach event listeners
function attachEventListeners() {
    const toggle = document.getElementById('chatbot-toggle');
    const close = document.getElementById('chatbot-close');
    const send = document.getElementById('chatbot-send');
    const input = document.getElementById('chatbot-input');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    toggle.addEventListener('click', openChat);
    close.addEventListener('click', closeChat);
    send.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isWaitingForResponse) sendMessage();
    });

    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            document.getElementById('chatbot-input').value = question;
            sendMessage();
        });
    });
}

// Open chat window
function openChat() {
    const window = document.getElementById('chatbot-window');
    const toggle = document.getElementById('chatbot-toggle');
    window.style.display = 'flex';
    toggle.style.display = 'none';
    isOpen = true;

    // Focus input
    setTimeout(() => {
        document.getElementById('chatbot-input').focus();
    }, 100);
}

// Close chat window
function closeChat() {
    const window = document.getElementById('chatbot-window');
    const toggle = document.getElementById('chatbot-toggle');
    window.style.display = 'none';
    toggle.style.display = 'flex';
    isOpen = false;
}

// Send message
async function sendMessage() {
    if (isWaitingForResponse) return;

    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addUserMessage(message);
    input.value = '';

    // Disable input while waiting
    isWaitingForResponse = true;
    setInputEnabled(false);
    updateStatus('Thinking...');

    // Add typing indicator
    addTypingIndicator();

    // Get AI response
    try {
        const response = await getAIResponse(message);
        removeTypingIndicator();
        addBotMessage(response);
        updateStatus('Powered by AI');
    } catch (error) {
        removeTypingIndicator();
        addBotMessage("I'm having trouble connecting right now. Please try again in a moment.");
        updateStatus('Connection issue');
        console.error('Chatbot error:', error);
    } finally {
        isWaitingForResponse = false;
        setInputEnabled(true);
        document.getElementById('chatbot-input').focus();
    }
}

// Get AI response from backend
async function getAIResponse(message) {
    const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            conversation_history: conversationHistory
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Update conversation history
    conversationHistory.push(
        { role: 'user', content: message },
        { role: 'assistant', content: data.response }
    );

    // Keep only last 6 messages (3 exchanges)
    if (conversationHistory.length > 6) {
        conversationHistory = conversationHistory.slice(-6);
    }

    return data.response;
}

// Add user message to chat
function addUserMessage(message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    const messageHTML = `
        <div class="chat-message user-message">
            <div class="message-content">${escapeHtml(message)}</div>
        </div>
    `;
    messagesDiv.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    const messageHTML = `
        <div class="chat-message bot-message">
            <div class="message-avatar">🔐</div>
            <div class="message-content">${formatBotMessage(message)}</div>
        </div>
    `;
    messagesDiv.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

// Add typing indicator
function addTypingIndicator() {
    const messagesDiv = document.getElementById('chatbot-messages');
    const typingHTML = `
        <div class="chat-message bot-message typing-indicator" id="typing-indicator">
            <div class="message-avatar">🔐</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    messagesDiv.insertAdjacentHTML('beforeend', typingHTML);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Update status text
function updateStatus(text) {
    const status = document.getElementById('chatbot-status');
    if (status) {
        status.textContent = text;
    }
}

// Enable/disable input
function setInputEnabled(enabled) {
    const input = document.getElementById('chatbot-input');
    const send = document.getElementById('chatbot-send');

    input.disabled = !enabled;
    send.disabled = !enabled;

    if (!enabled) {
        input.style.opacity = '0.6';
        send.style.opacity = '0.6';
    } else {
        input.style.opacity = '1';
        send.style.opacity = '1';
    }
}

// Format bot message (handle line breaks)
function formatBotMessage(message) {
    return escapeHtml(message).replace(/\n/g, '<br>');
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Scroll chat to bottom
function scrollToBottom() {
    const messagesDiv = document.getElementById('chatbot-messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
} else {
    initChatbot();
}
