#!/usr/bin/env python3
"""
URE MVP Streamlit UI
User interface for Unified Rural Ecosystem
"""

import streamlit as st
import sys
import os
from pathlib import Path
import base64
from datetime import datetime
import json
import uuid
import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="GramSetu - Rural AI Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1B5E20;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #000000;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1976D2;
    }
    .assistant-message {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-left: 4px solid #43A047;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .agri-expert {
        background-color: #4CAF50;
        color: #FFFFFF;
    }
    .policy-navigator {
        background-color: #2196F3;
        color: #FFFFFF;
    }
    .resource-optimizer {
        background-color: #FF9800;
        color: #FFFFFF;
    }
    .supervisor {
        background-color: #9C27B0;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'location' not in st.session_state:
    # Auto-detect location on first load
    try:
        from utils.location_detector import get_location_detector
        detector = get_location_detector()
        st.session_state.location = detector.get_location_from_ip()
        logger_msg = f"Location detected: {detector.get_location_string(st.session_state.location)}"
    except Exception as e:
        # Fallback to default location
        st.session_state.location = {
            'city': 'Nashik',
            'region': 'Maharashtra',
            'country': 'India',
            'district': 'Nashik'
        }
if 'user_profile' not in st.session_state:
    # Pre-fill district from detected location
    detected_district = st.session_state.location.get('district', 'Nashik')
    st.session_state.user_profile = {
        'name': '',
        'village': '',
        'district': detected_district,
        'phone': '',
        'crops': [],
        'land_size_acres': 0.0
    }
if 'profile_saved' not in st.session_state:
    st.session_state.profile_saved = False
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = set()
if 'quick_action_query' not in st.session_state:
    st.session_state.quick_action_query = ""


def get_agent_badge(agent_name: str) -> str:
    """Generate HTML badge for agent"""
    agent_classes = {
        'agri-expert': 'agri-expert',
        'policy-navigator': 'policy-navigator',
        'resource-optimizer': 'resource-optimizer',
        'supervisor': 'supervisor'
    }
    
    agent_labels = {
        'agri-expert': '🌱 Agri Expert',
        'policy-navigator': '📋 Policy Navigator',
        'resource-optimizer': '⚡ Resource Optimizer',
        'supervisor': '🎯 Supervisor'
    }
    
    css_class = agent_classes.get(agent_name, 'supervisor')
    label = agent_labels.get(agent_name, '🤖 Assistant')
    
    return f'<span class="agent-badge {css_class}">{label}</span>'


def encode_image(image_file) -> str:
    """Encode image to base64"""
    return base64.b64encode(image_file.read()).decode('utf-8')


def save_user_profile_local(profile: dict) -> bool:
    """Save user profile locally (for development)"""
    try:
        # In production, this would call the API
        # For now, just update session state
        st.session_state.user_profile = profile
        st.session_state.profile_saved = True
        return True
    except Exception as e:
        st.error(f"Failed to save profile: {e}")
        return False


def save_user_profile_api(profile: dict) -> bool:
    """Save user profile via API (for production)"""
    try:
        api_url = os.getenv('API_GATEWAY_URL', '').replace('/query', '/profile')
        
        if not api_url or 'localhost' in api_url:
            # Fallback to local save
            return save_user_profile_local(profile)
        
        payload = {
            'user_id': st.session_state.user_id,
            'profile': profile
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            st.session_state.user_profile = profile
            st.session_state.profile_saved = True
            return True
        else:
            st.error(f"Failed to save profile: {response.text}")
            return False
            
    except Exception as e:
        # Fallback to local save
        return save_user_profile_local(profile)


def submit_feedback_local(message_id: str, rating: str, comment: str = "") -> bool:
    """Submit feedback locally (for development)"""
    try:
        # In production, this would call the feedback API
        st.session_state.feedback_submitted.add(message_id)
        return True
    except Exception as e:
        st.error(f"Failed to submit feedback: {e}")
        return False


def submit_feedback_api(message_id: str, query: str, response: str, rating: str, comment: str = "", agent_name: str = "") -> bool:
    """Submit feedback via API (for production)"""
    try:
        api_url = os.getenv('API_GATEWAY_URL', '').replace('/query', '/feedback')
        
        if not api_url or 'localhost' in api_url:
            # Fallback to local save
            return submit_feedback_local(message_id, rating, comment)
        
        payload = {
            'user_id': st.session_state.user_id,
            'query_id': message_id,
            'rating': rating,
            'comment': comment,
            'query_text': query,
            'response_text': response,
            'agent_name': agent_name
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            st.session_state.feedback_submitted.add(message_id)
            return True
        else:
            return submit_feedback_local(message_id, rating, comment)
            
    except Exception as e:
        # Fallback to local save
        return submit_feedback_local(message_id, rating, comment)


def process_query_local(query: str, image_data: str = None, location: dict = None) -> dict:
    """Process query using local agents (for development)"""
    from agents.supervisor import supervisor_agent
    
    try:
        # Add location context to query if available
        if location:
            from utils.location_detector import get_location_detector
            detector = get_location_detector()
            location_str = detector.get_location_string(location)
            query_with_context = f"[User Location: {location_str}] {query}"
        else:
            query_with_context = query
        
        # For now, route directly to supervisor
        response = supervisor_agent(query_with_context)
        
        return {
            'success': True,
            'response': str(response),
            'agent_used': 'supervisor',
            'metadata': {'location': location}
        }
    except Exception as e:
        return {
            'success': False,
            'response': f"Error: {str(e)}",
            'agent_used': 'error',
            'metadata': {}
        }


# Header
st.markdown('<h1 class="main-header">🌾 GramSetu</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your AI-Powered Rural Assistant</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Language selection
    language = st.selectbox(
        "Language / भाषा",
        options=['en', 'hi', 'mr'],
        format_func=lambda x: {
            'en': '🇬🇧 English',
            'hi': '🇮🇳 हिंदी',
            'mr': '🇮🇳 मराठी'
        }[x],
        index=0
    )
    st.session_state.language = language
    
    st.divider()
    
    # Location Display
    st.header("📍 Your Location")
    if st.session_state.location:
        from utils.location_detector import get_location_detector
        detector = get_location_detector()
        location_str = detector.get_location_string(st.session_state.location)
        st.success(f"📍 {location_str}")
        st.caption("Auto-detected from your IP address")
    
    st.divider()
    
    # User Profile Form
    st.header("👤 User Profile")
    
    if not st.session_state.profile_saved:
        with st.form("profile_form"):
            name = st.text_input("Name / नाव", value=st.session_state.user_profile.get('name', ''))
            village = st.text_input("Village / गाव", value=st.session_state.user_profile.get('village', ''))
            
            # District dropdown with auto-detected value
            districts = ['Nashik', 'Pune', 'Ahmednagar', 'Dhule', 'Jalgaon', 'Aurangabad', 'Mumbai', 'Nagpur', 'Solapur', 'Kolhapur', 'Other']
            current_district = st.session_state.user_profile.get('district', 'Nashik')
            
            # Find index of current district
            try:
                district_index = districts.index(current_district)
            except ValueError:
                district_index = 0  # Default to Nashik
            
            district = st.selectbox(
                "District / जिल्हा",
                options=districts,
                index=district_index,
                help="Auto-detected from your location. Change if incorrect."
            )
            
            phone = st.text_input("Phone / फोन", value=st.session_state.user_profile.get('phone', ''), placeholder="+91XXXXXXXXXX")
            
            crops_options = ['Wheat', 'Rice', 'Cotton', 'Sugarcane', 'Onion', 'Tomato', 'Grapes', 'Other']
            crops = st.multiselect("Crops / पिके", options=crops_options, default=st.session_state.user_profile.get('crops', []))
            
            land_size = st.number_input("Land Size (acres) / जमीन (एकर)", min_value=0.0, max_value=1000.0, value=st.session_state.user_profile.get('land_size_acres', 0.0), step=0.5)
            
            submitted = st.form_submit_button("💾 Save Profile")
            
            if submitted:
                profile = {
                    'name': name,
                    'village': village,
                    'district': district,
                    'phone': phone,
                    'crops': crops,
                    'land_size_acres': land_size
                }
                
                if save_user_profile_api(profile):
                    st.success("✅ Profile saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save profile. Please try again.")
    else:
        # Display saved profile
        st.success("✅ Profile Saved")
        profile = st.session_state.user_profile
        st.text(f"Name: {profile.get('name', 'N/A')}")
        st.text(f"Village: {profile.get('village', 'N/A')}")
        st.text(f"District: {profile.get('district', 'N/A')}")
        st.text(f"Crops: {', '.join(profile.get('crops', []))}")
        st.text(f"Land: {profile.get('land_size_acres', 0)} acres")
        
        if st.button("✏️ Edit Profile"):
            st.session_state.profile_saved = False
            st.rerun()
    
    st.text(f"User ID: {st.session_state.user_id[:8]}...")
    
    st.divider()
    
    # Help Guide
    st.header("❓ Help Guide")
    
    with st.expander("📖 How to Use GramSetu"):
        st.markdown("""
        **Welcome to GramSetu!** Your AI-powered rural assistant.
        
        **What can I help you with?**
        - 🌱 Crop disease identification
        - 💰 Market prices and trends
        - 📋 Government schemes (PM-Kisan, PMFBY, etc.)
        - 💧 Irrigation recommendations
        - 🌤️ Weather forecasts
        - 🌾 Farming best practices
        
        **How to ask questions:**
        1. Type your question in the chat box below
        2. Upload a crop image (optional) for disease identification
        3. Press Enter or click Send
        4. Get instant AI-powered answers!
        
        **Example Questions:**
        - "What disease is affecting my tomato plant?"
        - "What are current onion prices in Nashik?"
        - "Am I eligible for PM-Kisan scheme?"
        - "When should I irrigate my wheat crop?"
        - "What's the weather forecast for next week?"
        """)
    
    with st.expander("🌍 Language Support"):
        st.markdown("""
        **Available Languages:**
        - 🇬🇧 English
        - 🇮🇳 हिंदी (Hindi)
        - 🇮🇳 मराठी (Marathi)
        
        **How to change language:**
        1. Select your preferred language from the dropdown above
        2. All responses will be translated automatically
        3. You can ask questions in any language!
        """)
    
    with st.expander("📷 Image Upload"):
        st.markdown("""
        **For Crop Disease Identification:**
        1. Click "Browse files" below the chat
        2. Select a clear photo of the affected crop
        3. Supported formats: JPG, JPEG, PNG
        4. Ask your question about the disease
        5. Our AI will analyze the image and provide diagnosis
        
        **Tips for best results:**
        - Take photos in good lighting
        - Focus on the affected area
        - Include leaves, stems, or fruits showing symptoms
        - Avoid blurry or dark images
        """)
    
    with st.expander("👤 User Profile"):
        st.markdown("""
        **Why create a profile?**
        - Get personalized recommendations
        - Save your conversation history
        - Receive location-specific advice
        - Track your farming progress
        
        **What information do we collect?**
        - Name and village (for personalization)
        - Crops you grow (for relevant advice)
        - Land size (for resource planning)
        - Phone number (optional, for support)
        
        **Automatic Location Detection:**
        - Your location is automatically detected from your IP address
        - District is pre-filled in the profile form
        - You can change it if the detection is incorrect
        - Location helps provide weather and market price info
        
        **Your data is safe:**
        - All data is encrypted
        - We never share your information
        - You can delete your profile anytime
        """)
    
    with st.expander("💬 Feedback"):
        st.markdown("""
        **Help us improve!**
        
        After each response, you can:
        - 👍 Thumbs up if the answer was helpful
        - 👎 Thumbs down if it wasn't helpful
        - Add comments to explain what went wrong
        
        Your feedback helps us:
        - Improve answer accuracy
        - Train better AI models
        - Understand farmer needs
        - Fix issues quickly
        """)
    
    with st.expander("🔒 Privacy & Safety"):
        st.markdown("""
        **Your Privacy Matters:**
        - All conversations are encrypted
        - Personal information is anonymized
        - Data stored securely on AWS
        - No data shared with third parties
        
        **Content Safety:**
        - AI responses are filtered for safety
        - Harmful content is automatically blocked
        - Only agricultural topics are supported
        - Report any inappropriate content
        
        **Support:**
        - For technical issues, contact support
        - For farming advice, ask in the chat
        - Emergency? Call local agriculture office
        """)
    
    with st.expander("📞 Contact & Support"):
        st.markdown("""
        **Need Help?**
        
        **Technical Support:**
        - Email: support@gramsetu.in
        - Phone: 1800-XXX-XXXX (Toll-free)
        - Hours: 9 AM - 6 PM (Mon-Sat)
        
        **Agricultural Helpline:**
        - Kisan Call Center: 1800-180-1551
        - Available 24/7 in multiple languages
        
        **Emergency:**
        - For crop emergencies, contact your local agriculture officer
        - For weather alerts, check local news
        """)
    
    st.divider()
    
    # Quick actions
    st.header("🚀 Quick Actions")
    if st.button("🌱 Crop Disease Help", help="Get help identifying crop diseases and pests"):
        st.session_state.quick_action_query = 'I need help identifying a crop disease'
        st.rerun()
    
    if st.button("📋 Government Schemes", help="Learn about PM-Kisan, PMFBY, and other schemes"):
        st.session_state.quick_action_query = 'What government schemes are available for farmers?'
        st.rerun()
    
    if st.button("💰 Market Prices", help="Check current market prices for crops"):
        st.session_state.quick_action_query = 'What are the current market prices for crops?'
        st.rerun()
    
    if st.button("💧 Irrigation Tips", help="Get irrigation recommendations for your crops"):
        st.session_state.quick_action_query = 'When should I irrigate my crops?'
        st.rerun()
    
    if st.button("🌤️ Weather Forecast", help="Get weather forecast for your area"):
        st.session_state.quick_action_query = 'What is the weather forecast for the next few days?'
        st.rerun()
    
    st.divider()
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main chat area
st.header("💬 Chat")

# Display welcome message if no messages
if len(st.session_state.messages) == 0:
    st.info("""
    👋 **Welcome to GramSetu!**
    
    I'm your AI-powered rural assistant. I can help you with:
    - 🌱 Crop disease identification (upload a photo!)
    - 💰 Market prices and trends
    - 📋 Government schemes and eligibility
    - 💧 Irrigation and water management
    - 🌤️ Weather forecasts
    - 🌾 Farming best practices
    
    **Try asking:**
    - "What disease is affecting my tomato plant?"
    - "What are current onion prices?"
    - "Am I eligible for PM-Kisan?"
    
    💡 **Tip:** Check the Help Guide in the sidebar for more information!
    """)

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    role = message['role']
    content = message['content']
    
    if role == 'user':
        st.markdown(
            f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>',
            unsafe_allow_html=True
        )
    else:
        agent = message.get('agent', 'supervisor')
        badge = get_agent_badge(agent)
        st.markdown(
            f'<div class="chat-message assistant-message">{badge}<br>{content}</div>',
            unsafe_allow_html=True
        )
        
        # Feedback buttons for assistant messages
        message_id = f"msg_{idx}"
        
        if message_id not in st.session_state.feedback_submitted:
            col1, col2, col3 = st.columns([1, 1, 8])
            
            with col1:
                if st.button("👍", key=f"thumbs_up_{idx}"):
                    # Get the previous user message
                    user_query = ""
                    if idx > 0 and st.session_state.messages[idx-1]['role'] == 'user':
                        user_query = st.session_state.messages[idx-1]['content']
                    
                    if submit_feedback_api(message_id, user_query, content, "positive", "", agent):
                        st.success("Thanks for your feedback!")
                        st.rerun()
            
            with col2:
                if st.button("👎", key=f"thumbs_down_{idx}"):
                    st.session_state[f"show_comment_{idx}"] = True
                    st.rerun()
            
            # Show comment box if thumbs down was clicked
            if st.session_state.get(f"show_comment_{idx}", False):
                with st.form(key=f"feedback_form_{idx}"):
                    comment = st.text_area("What went wrong?", key=f"comment_{idx}")
                    submit_comment = st.form_submit_button("Submit Feedback")
                    
                    if submit_comment:
                        # Get the previous user message
                        user_query = ""
                        if idx > 0 and st.session_state.messages[idx-1]['role'] == 'user':
                            user_query = st.session_state.messages[idx-1]['content']
                        
                        if submit_feedback_api(message_id, user_query, content, "negative", comment, agent):
                            st.success("Thanks for your feedback!")
                            st.session_state[f"show_comment_{idx}"] = False
                            st.rerun()
        else:
            st.caption("✅ Feedback submitted")

# Image upload
uploaded_image = st.file_uploader(
    "📷 Upload crop image (optional)",
    type=['jpg', 'jpeg', 'png'],
    help="Upload a clear photo of your crop for disease identification. Supported formats: JPG, JPEG, PNG. Take photos in good lighting and focus on affected areas."
)

if uploaded_image:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    with col2:
        st.info("Image uploaded! Ask a question about this crop.")

# Chat input
# Use quick action query if set, otherwise empty
default_query = st.session_state.quick_action_query if st.session_state.quick_action_query else ""

user_input = st.chat_input(
    "Ask me anything about farming, schemes, or resources...",
    key="chat_input"
)

# If there's a quick action query, show it in a text input for editing
if st.session_state.quick_action_query and not user_input:
    st.info(f"💡 Quick Action: {st.session_state.quick_action_query}")
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("✅ Send this query", use_container_width=True):
            user_input = st.session_state.quick_action_query
            st.session_state.quick_action_query = ""
    with col2:
        if st.button("❌ Clear", use_container_width=True):
            st.session_state.quick_action_query = ""
            st.rerun()

if user_input:
    # Clear quick action query if it was used
    if st.session_state.quick_action_query:
        st.session_state.quick_action_query = ""
    
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input
    })
    
    # Process query
    with st.spinner("🤔 Thinking..."):
        # Encode image if provided
        image_data = None
        if uploaded_image:
            image_data = encode_image(uploaded_image)
        
        # Get response with location context
        result = process_query_local(user_input, image_data, st.session_state.location)
        
        # Add assistant message
        st.session_state.messages.append({
            'role': 'assistant',
            'content': result['response'],
            'agent': result['agent_used']
        })
    
    st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🌾 GramSetu - Empowering Rural India with AI</p>
    <p>Powered by AWS Bedrock & Strands SDK</p>
</div>
""", unsafe_allow_html=True)
