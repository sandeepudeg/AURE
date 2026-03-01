// Configuration
const API_ENDPOINT = 'https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query';

// State management
const state = {
    sessionId: generateSessionId(),
    userId: generateUserId(),
    language: 'en',
    location: { city: 'Nashik', region: 'Maharashtra', country: 'India', district: 'Nashik' },
    profile: {
        name: '',
        village: '',
        district: 'Nashik',
        phone: '',
        crops: [],
        landSize: 0
    },
    profileSaved: false,
    feedbackSubmitted: new Set(),
    uploadedImage: null
};

// DOM Elements
const elements = {
    chatContainer: document.getElementById('chatContainer'),
    userInput: document.getElementById('userInput'),
    sendButton: document.getElementById('sendButton'),
    languageSelect: document.getElementById('languageSelect'),
    clearChatBtn: document.getElementById('clearChatBtn'),
    userProfileForm: document.getElementById('userProfileForm'),
    profileForm: document.getElementById('profileForm'),
    profileDisplay: document.getElementById('profileDisplay'),
    editProfileBtn: document.getElementById('editProfileBtn'),
    userId: document.getElementById('userId'),
    imageUploadBtn: document.getElementById('imageUploadBtn'),
    imageUpload: document.getElementById('imageUpload'),
    imagePreview: document.getElementById('imagePreview'),
    previewImg: document.getElementById('previewImg'),
    removeImageBtn: document.getElementById('removeImageBtn')
};

// Initialize
function init() {
    // Set user ID display
    elements.userId.textContent = state.userId.substring(0, 8) + '...';
    
    // Event listeners
    elements.sendButton.addEventListener('click', sendMessage);
    elements.userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    elements.languageSelect.addEventListener('change', (e) => {
        state.language = e.target.value;
        console.log('Language changed to:', state.language);
    });
    
    elements.clearChatBtn.addEventListener('click', clearChat);
    elements.userProfileForm.addEventListener('submit', saveProfile);
    elements.editProfileBtn.addEventListener('click', editProfile);
    
    // Image upload
    elements.imageUploadBtn.addEventListener('click', () => elements.imageUpload.click());
    elements.imageUpload.addEventListener('change', handleImageUpload);
    elements.removeImageBtn.addEventListener('click', removeImage);
    
    // Quick action buttons
    document.querySelectorAll('.btn-quick-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const query = e.target.getAttribute('data-query');
            elements.userInput.value = query;
            sendMessage();
        });
    });
    
    // Expander functionality
    document.querySelectorAll('.expander-header').forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            content.classList.toggle('active');
        });
    });
    
    console.log('GramSetu Web UI initialized');
}

// Utility functions
function generateSessionId() {
    return 'web_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function generateUserId() {
    return 'user_' + Math.random().toString(36).substr(2, 16);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Message handling
function addMessage(content, isUser = false, agent = 'supervisor', messageId = null) {
    // Remove welcome message if it exists
    const welcome = elements.chatContainer.querySelector('.welcome');
    if (welcome) {
        welcome.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.dataset.messageId = messageId || Date.now();
    
    const contentDiv = document.createElement('div');
    contentDiv.className = `chat-message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    if (!isUser && agent) {
        const badge = getAgentBadge(agent);
        contentDiv.innerHTML = badge + '<br>' + escapeHtml(content);
        
        // Add feedback buttons
        if (!state.feedbackSubmitted.has(messageDiv.dataset.messageId)) {
            const feedbackDiv = createFeedbackButtons(messageDiv.dataset.messageId, content);
            contentDiv.appendChild(feedbackDiv);
        }
    } else {
        if (isUser) {
            contentDiv.innerHTML = '<strong>You:</strong><br>' + escapeHtml(content);
        } else {
            contentDiv.textContent = content;
        }
    }
    
    messageDiv.appendChild(contentDiv);
    elements.chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function getAgentBadge(agent) {
    const badges = {
        'supervisor': '<span class="agent-badge badge-supervisor">🎯 Supervisor</span>',
        'agri-expert': '<span class="agent-badge badge-agri-expert">🌱 Agri Expert</span>',
        'policy-navigator': '<span class="agent-badge badge-policy">📋 Policy Navigator</span>',
        'resource-optimizer': '<span class="agent-badge badge-resource">⚡ Resource Optimizer</span>'
    };
    return badges[agent] || badges['supervisor'];
}

function createFeedbackButtons(messageId, content) {
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'feedback-buttons';
    feedbackDiv.innerHTML = `
        <button class="feedback-btn" data-rating="positive" data-message-id="${messageId}">👍</button>
        <button class="feedback-btn" data-rating="negative" data-message-id="${messageId}">👎</button>
    `;
    
    feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const rating = e.target.getAttribute('data-rating');
            const msgId = e.target.getAttribute('data-message-id');
            
            if (rating === 'positive') {
                submitFeedback(msgId, rating, '');
            } else {
                showFeedbackForm(msgId, feedbackDiv);
            }
        });
    });
    
    return feedbackDiv;
}

function showFeedbackForm(messageId, feedbackDiv) {
    const formDiv = document.createElement('div');
    formDiv.className = 'feedback-form';
    formDiv.innerHTML = `
        <textarea placeholder="What went wrong?" rows="3"></textarea>
        <button class="btn btn-primary btn-sm">Submit Feedback</button>
    `;
    
    const submitBtn = formDiv.querySelector('button');
    const textarea = formDiv.querySelector('textarea');
    
    submitBtn.addEventListener('click', () => {
        submitFeedback(messageId, 'negative', textarea.value);
        formDiv.remove();
    });
    
    feedbackDiv.appendChild(formDiv);
}

function submitFeedback(messageId, rating, comment) {
    state.feedbackSubmitted.add(messageId);
    
    // Find the message element and update it
    const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageEl) {
        const feedbackButtons = messageEl.querySelector('.feedback-buttons');
        if (feedbackButtons) {
            feedbackButtons.innerHTML = '<div class="feedback-submitted">✅ Feedback submitted</div>';
        }
    }
    
    console.log('Feedback submitted:', { messageId, rating, comment });
    
    // In production, send to API
    // sendFeedbackToAPI(messageId, rating, comment);
}

// Loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message';
    loadingDiv.id = 'loading-indicator';
    
    const loadingContent = document.createElement('div');
    loadingContent.className = 'loading';
    loadingContent.innerHTML = '<span></span><span></span><span></span>';
    
    loadingDiv.appendChild(loadingContent);
    elements.chatContainer.appendChild(loadingDiv);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function removeLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) {
        loading.remove();
    }
}

// Error handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = `Error: ${message}`;
    elements.chatContainer.appendChild(errorDiv);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    
    setTimeout(() => errorDiv.remove(), 5000);
}

// Send message
async function sendMessage() {
    const message = elements.userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input
    elements.userInput.disabled = true;
    elements.sendButton.disabled = true;
    
    // Add user message
    addMessage(message, true);
    
    // Clear input
    elements.userInput.value = '';
    
    // Show loading
    showLoading();
    
    try {
        const payload = {
            query: message,
            session_id: state.sessionId,
            user_id: state.userId,
            language: state.language,
            location: state.location
        };
        
        // Add image if uploaded
        if (state.uploadedImage) {
            payload.image = state.uploadedImage;
        }
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        removeLoading();
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Add assistant response
        if (data.response) {
            const agent = data.agent_used || 'supervisor';
            const messageId = Date.now();
            addMessage(data.response, false, agent, messageId);
        } else if (data.error) {
            showError(data.error);
        } else {
            showError('Unexpected response format from API');
        }
        
        // Clear uploaded image after sending
        if (state.uploadedImage) {
            removeImage();
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeLoading();
        showError(error.message || 'Failed to connect to the server. Please try again.');
    } finally {
        // Re-enable input
        elements.userInput.disabled = false;
        elements.sendButton.disabled = false;
        elements.userInput.focus();
    }
}

// Profile management
function saveProfile(e) {
    e.preventDefault();
    
    const name = document.getElementById('profileName').value;
    const village = document.getElementById('profileVillage').value;
    const district = document.getElementById('profileDistrict').value;
    const phone = document.getElementById('profilePhone').value;
    const landSize = parseFloat(document.getElementById('profileLandSize').value);
    
    // Get selected crops
    const crops = [];
    document.querySelectorAll('#cropsCheckboxes input[type="checkbox"]:checked').forEach(cb => {
        crops.push(cb.value);
    });
    
    state.profile = {
        name,
        village,
        district,
        phone,
        crops,
        landSize
    };
    
    state.profileSaved = true;
    
    // Update display
    elements.profileForm.style.display = 'none';
    elements.profileDisplay.style.display = 'block';
    
    const summary = `
        Name: ${name || 'N/A'}<br>
        Village: ${village || 'N/A'}<br>
        District: ${district}<br>
        Crops: ${crops.join(', ') || 'N/A'}<br>
        Land: ${landSize} acres
    `;
    
    document.getElementById('profileSummary').innerHTML = summary;
    
    console.log('Profile saved:', state.profile);
}

function editProfile() {
    elements.profileForm.style.display = 'block';
    elements.profileDisplay.style.display = 'none';
}

// Image handling
function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.match('image/(jpeg|jpg|png)')) {
        showError('Please upload a JPG, JPEG, or PNG image');
        return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('Image size must be less than 5MB');
        return;
    }
    
    // Read and encode image
    const reader = new FileReader();
    reader.onload = (event) => {
        const base64 = event.target.result.split(',')[1];
        state.uploadedImage = base64;
        
        // Show preview
        elements.previewImg.src = event.target.result;
        elements.imagePreview.style.display = 'flex';
        
        console.log('Image uploaded and encoded');
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    state.uploadedImage = null;
    elements.imagePreview.style.display = 'none';
    elements.imageUpload.value = '';
    console.log('Image removed');
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        elements.chatContainer.innerHTML = `
            <div class="welcome">
                <strong>👋 Welcome to GramSetu!</strong>
                <p style="margin-top: 0.5rem;">
                    I'm your AI-powered rural assistant. I can help you with:
                </p>
                <ul>
                    <li>🌱 Crop disease identification (upload a photo!)</li>
                    <li>💰 Market prices and trends</li>
                    <li>📋 Government schemes and eligibility</li>
                    <li>💧 Irrigation and water management</li>
                    <li>🌤️ Weather forecasts</li>
                    <li>🌾 Farming best practices</li>
                </ul>
                <p style="margin-top: 1rem;">
                    <strong>Try asking:</strong>
                </p>
                <ul>
                    <li>"What disease is affecting my tomato plant?"</li>
                    <li>"What are current onion prices?"</li>
                    <li>"Am I eligible for PM-Kisan?"</li>
                </ul>
                <p style="margin-top: 1rem;">
                    <small>💡 <strong>Tip:</strong> Check the Help Guide in the sidebar for more information!</small>
                </p>
            </div>
        `;
        
        // Reset state
        state.feedbackSubmitted.clear();
        state.sessionId = generateSessionId();
        
        console.log('Chat cleared');
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
