#!/usr/bin/env python3
"""
URE MVP Streamlit UI - Minimal Fast-Loading Version
"""

import streamlit as st
import os
import uuid
import requests

# Configuration
USE_API_MODE = os.getenv('USE_API_MODE', 'true').lower() == 'true'
API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query')

# Page configuration
st.set_page_config(
    page_title="GramSetu",
    page_icon="🌾",
    layout="centered"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Header
st.title("🌾 GramSetu")
st.caption("Your AI-Powered Rural Assistant")

# Welcome message
if len(st.session_state.messages) == 0:
    st.info("""
    Welcome! I can help you with:
    - 🌱 Crop disease identification
    - 💰 Market prices
    - 📋 Government schemes
    - 🌤️ Weather forecasts
    - 💧 Irrigation tips
    """)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

# Chat input
if prompt := st.chat_input("Ask me anything about farming..."):
    # Add user message
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_ENDPOINT,
                    json={
                        'user_id': st.session_state.user_id,
                        'query': prompt,
                        'language': 'en'
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('response', 'No response')
                else:
                    answer = f"Error: {response.status_code}"
            except Exception as e:
                answer = f"Connection error: {str(e)}"
            
            st.write(answer)
            st.session_state.messages.append({'role': 'assistant', 'content': answer})

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    if USE_API_MODE:
        st.success("🌐 AWS Mode")
    else:
        st.info("💻 Local Mode")
    
    st.divider()
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption(f"User ID: {st.session_state.user_id[:8]}...")
