// Configuration
const API_ENDPOINT = 'https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query';
const SESSION_ID = generateSessionId();

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

// Event Listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Generate unique session ID
function generateSessionId() {
    return 'web_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Add message to chat
function addMessage(content, isUser = false, agent = 'supervisor') {
    // Remove welcome message if it exists
    const welcome = chatContainer.querySelector('.welcome');
    if (welcome) {
        welcome.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (!isUser && agent) {
        // Add agent badge for assistant messages
        const badge = getAgentBadge(agent);
        contentDiv.innerHTML = badge + '<br>' + escapeHtml(content);
    } else {
        if (isUser) {
            contentDiv.innerHTML = '<strong>You:</strong><br>' + escapeHtml(content);
        } else {
            contentDiv.textContent = content;
        }
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Get agent badge HTML
function getAgentBadge(agent) {
    const badges = {
        'supervisor': '<span class="agent-badge badge-supervisor">🎯 Supervisor</span>',
        'agri-expert': '<span class="agent-badge badge-agri-expert">🌱 Agri Expert</span>',
        'policy-navigator': '<span class="agent-badge badge-policy">📋 Policy Navigator</span>',
        'resource-optimizer': '<span class="agent-badge badge-resource">⚡ Resource Optimizer</span>'
    };
    return badges[agent] || badges['supervisor'];
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Show loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'loading-indicator';
    
    const loadingContent = document.createElement('div');
    loadingContent.className = 'message-content loading';
    loadingContent.innerHTML = '<span></span><span></span><span></span>';
    
    loadingDiv.appendChild(loadingContent);
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Remove loading indicator
function removeLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) {
        loading.remove();
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = `Error: ${message}`;
    chatContainer.appendChild(errorDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Remove error after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

// Send message to API
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Add user message
    addMessage(message, true);
    
    // Clear input
    userInput.value = '';
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: message,
                session_id: SESSION_ID,
                user_id: 'web_user',
                language: 'en'
            })
        });
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Remove loading
        removeLoading();
        
        // Add assistant response
        if (data.response) {
            const agent = data.agent_used || 'supervisor';
            addMessage(data.response, false, agent);
        } else if (data.error) {
            showError(data.error);
        } else {
            showError('Unexpected response format from API');
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeLoading();
        showError(error.message || 'Failed to connect to the server. Please try again.');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Initialize
userInput.focus();
