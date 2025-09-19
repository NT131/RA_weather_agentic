"""
Streamlit Frontend for Weather Outfit AI

A simple, user-friendly interface for getting outfit recommendations.
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Weather Outfit AI",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

class WeatherOutfitClient:
    """Client to interact with the Weather Outfit AI API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def check_health(self) -> Dict[str, Any]:
        """Check if the API is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def get_outfit_recommendation(self, location: str, style_preference: str = "casual", time_horizon: str = "now") -> Dict[str, Any]:
        """Get outfit recommendation from the API."""
        try:
            payload = {
                "location": location,
                "style_preference": style_preference,
                "time_horizon": time_horizon
            }
            
            response = requests.post(
                f"{self.base_url}/outfit-recommendation",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def chat_with_ai(self, message: str, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        """Send a natural language message to the AI chat system."""
        try:
            payload = {
                "message": message,
                "conversation_history": conversation_history or []
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}

def init_session_state():
    """Initialize session state variables."""
    if 'recommendations_history' not in st.session_state:
        st.session_state.recommendations_history = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "chat"  # "form" or "chat" - default to chat
    if 'api_client' not in st.session_state:
        api_url = st.sidebar.text_input(
            "API URL", 
            value="http://localhost:8000",
            help="URL of the Weather Outfit AI API"
        )
        st.session_state.api_client = WeatherOutfitClient(api_url)

def display_weather_info(weather_data: Dict[str, Any]):
    """Display weather information in a nice format."""
    if not weather_data:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Temperature", 
            f"{weather_data.get('temperature', 'N/A')}°C",
            delta=f"Feels like {weather_data.get('feels_like', 'N/A')}°C"
        )
    
    with col2:
        st.metric("Humidity", f"{weather_data.get('humidity', 'N/A')}%")
    
    with col3:
        st.metric("Wind Speed", f"{weather_data.get('wind_speed', 'N/A')} km/h")
    
    if weather_data.get('description'):
        st.info(f"🌤️ **Weather**: {weather_data['description'].title()}")

def display_outfit_recommendation(recommendation: Dict[str, Any]):
    """Display outfit recommendation in a structured way."""
    st.markdown("### 👕 Your Outfit Recommendation")
    
    # Main recommendation text
    if recommendation.get('outfit_suggestion'):
        st.markdown(recommendation['outfit_suggestion'])
    
    # Additional info if available
    if recommendation.get('additional_info'):
        st.markdown(f"**💡 Tip**: {recommendation['additional_info']}")


def display_chat_message(role: str, content: str, weather_info: Optional[Dict] = None):
    """Display a chat message with proper styling."""
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)
            # Display weather info if available
            if weather_info:
                with st.expander("🌤️ Weather Details"):
                    display_weather_info(weather_info)


def chat_interface():
    """Render the chat interface."""
    st.markdown("### 💬 Chat with Weather Outfit AI")
    st.markdown("Ask me anything about outfit recommendations, weather, or fashion advice!")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            display_chat_message(
                message["role"], 
                message["content"], 
                message.get("weather_info")
            )
    
    # Chat input
    if prompt := st.chat_input("Ask me about outfits, weather, or fashion advice..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare conversation history for API
                conversation_history = []
                for msg in st.session_state.chat_history[-10:]:  # Last 10 messages
                    if msg["role"] == "user":
                        conversation_history.append(f"User: {msg['content']}")
                    else:
                        conversation_history.append(f"Bot: {msg['content']}")
                
                # Get response from API
                result = st.session_state.api_client.chat_with_ai(
                    message=prompt,
                    conversation_history=conversation_history
                )
                
                if result["status"] == "success":
                    data = result["data"]
                    response_text = data.get("response", "I couldn't generate a response.")
                    weather_info = data.get("weather", {})
                    
                    # Display the response
                    st.markdown(response_text)
                    
                    # Display weather info if available
                    if weather_info:
                        with st.expander("🌤️ Weather Details"):
                            display_weather_info(weather_info)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response_text,
                        "weather_info": weather_info if weather_info else None
                    })
                    
                    # Add to recommendations history if it's an outfit recommendation
                    if data.get("outfit_suggestion"):
                        recommendation_entry = {
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "location": data.get("location", "Unknown"),
                            "style": "chat-based",
                            "recommendation": response_text,
                            "weather": weather_info
                        }
                        st.session_state.recommendations_history.insert(0, recommendation_entry)
                        
                        # Keep only last 10 recommendations
                        if len(st.session_state.recommendations_history) > 10:
                            st.session_state.recommendations_history = st.session_state.recommendations_history[:10]
                
                else:
                    error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", help="Clear the chat history"):
        st.session_state.chat_history = []
        st.rerun()


def form_interface():
    """Render the traditional form interface."""
    with st.container():
        st.markdown("### 📍 Location & Preferences")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            location = st.text_input(
                "Location",
                placeholder="e.g., New York, London, Tokyo",
                help="Enter the city or location for weather data"
            )
        
        with col2:
            style_preference = st.selectbox(
                "Style Preference",
                ["casual", "business", "formal", "sporty", "trendy"],
                help="Choose your preferred style"
            )
        
        time_horizon = st.selectbox(
            "Time Horizon",
            ["now", "today", "tomorrow", "this week"],
            help="When do you need the outfit recommendation?"
        )
        
        # Get recommendation button
        if st.button("🎯 Get Outfit Recommendation", type="primary", use_container_width=True):
            if not location.strip():
                st.error("Please enter a location")
                return
            
            with st.spinner("Getting your perfect outfit recommendation... 🤔"):
                result = st.session_state.api_client.get_outfit_recommendation(
                    location=location.strip(),
                    style_preference=style_preference,
                    time_horizon=time_horizon
                )
                
                if result["status"] == "success":
                    data = result["data"]
                    
                    # Display weather information
                    st.markdown("### 🌤️ Weather Information")
                    display_weather_info(data.get("weather", {}))
                    
                    st.markdown("---")
                    
                    # Display outfit recommendation
                    display_outfit_recommendation(data)
                    
                    # Save to history
                    recommendation_entry = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "location": location,
                        "style": style_preference,
                        "recommendation": data.get("outfit_suggestion", ""),
                        "weather": data.get("weather", {})
                    }
                    st.session_state.recommendations_history.insert(0, recommendation_entry)
                    
                    # Keep only last 10 recommendations
                    if len(st.session_state.recommendations_history) > 10:
                        st.session_state.recommendations_history = st.session_state.recommendations_history[:10]
                
                else:
                    st.error(f"❌ Error getting recommendation: {result.get('error', 'Unknown error')}")


def main():
    """Main Streamlit application."""
    init_session_state()
    
    # Header
    st.title("👕 Weather Outfit AI")
    st.markdown("Get personalized outfit recommendations based on real-time weather data")
    
    # Mode selector
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Choose your interaction style:")
    with col2:
        mode = st.selectbox(
            "Mode",
            ["� Chat Mode", "� Form Mode"],
            index=0 if st.session_state.current_mode == "chat" else 1,
            label_visibility="collapsed"
        )
        
        # Update session state based on selection
        if mode == "� Chat Mode":
            st.session_state.current_mode = "chat"
        else:
            st.session_state.current_mode = "form"
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Settings")
    
    # API Health Check
    with st.sidebar:
        st.markdown("### 🏥 API Status")
        health_check = st.session_state.api_client.check_health()
        
        if health_check["status"] == "healthy":
            st.success("✅ API is healthy")
        else:
            st.error(f"❌ API Error: {health_check.get('error', 'Unknown error')}")
            st.warning("Make sure the FastAPI server is running on the specified URL")
            st.code("uv run uvicorn weather_outfit_ai.app:app --host 0.0.0.0 --port 8000")
        
        # Mode information in sidebar
        st.markdown("### 📖 Mode Info")
        if st.session_state.current_mode == "chat":
            st.info("**Chat Mode**: Have natural conversations about fashion and weather")
        else:
            st.info("**Form Mode**: Use structured inputs for quick recommendations")
    
    st.markdown("---")
    
    # Render the appropriate interface
    if st.session_state.current_mode == "chat":
        chat_interface()
    else:
        form_interface()
    
    # History section (only show for form mode or if there are recommendations)
    if st.session_state.recommendations_history and st.session_state.current_mode == "form":
        st.markdown("---")
        st.markdown("### 📚 Recent Recommendations")
        
        for i, entry in enumerate(st.session_state.recommendations_history):
            with st.expander(f"🕐 {entry['timestamp']} - {entry['location']} ({entry['style']})"):
                st.markdown(f"**Weather**: {entry['weather'].get('description', 'N/A')} - {entry['weather'].get('temperature', 'N/A')}°C")
                st.markdown(f"**Recommendation**: {entry['recommendation']}")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 Powered by OpenAI**")
    
    with col2:
        st.markdown("**🌡️ Real-time Weather**")
    
    with col3:
        st.markdown("**👔 Smart Wardrobe**")

if __name__ == "__main__":
    main()
