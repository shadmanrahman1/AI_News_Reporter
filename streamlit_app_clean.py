# -*- coding: utf-8 -*-
"""
AI News Reporter - Streamlit Application
Enhanced for seamless client testing with Streamlit secrets
"""

import streamlit as st
import os
import io
from typing import Dict, Any, List
import requests
from groq import Groq
from social_analyzer import analyze_social_media_discussion
from news_scraper import scrape_news_content
from utils import create_news_summary, scrape_with_brightdata, generate_valid_news_url
import tempfile


# Page configuration
st.set_page_config(
    page_title="AI News Reporter",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-success {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-error {
        color: #F44336;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def main():
    st.title("🎙️ AI News Reporter")
    st.subheader("Professional News Broadcasting Powered by AI")

    # Initialize session state
    if "topics" not in st.session_state:
        st.session_state.topics = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""

    # API Key Configuration using Streamlit secrets for demo key
    # Try to get API key from multiple sources
    api_key = None

    # 1. Check Streamlit secrets (for deployed version)
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except:
        pass

    # 2. Check environment variables
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    if api_key:
        st.sidebar.success("✅ Ready for Testing!")
        st.sidebar.info("Demo API key configured - start testing immediately!")
    else:
        st.sidebar.warning("⚠️ API Key Required")

    # Optional: Allow clients to use their own API key
    with st.sidebar.expander(
        "🔧 Advanced: Use Custom API Key", expanded=not bool(api_key)
    ):
        if api_key:
            st.markdown("*Optional: Use your own API key for unlimited access*")
        else:
            st.markdown("*Required: Enter your API key to use the app*")
            st.markdown(
                "Get your free key from [Groq Console](https://console.groq.com/keys)"
            )

        custom_api_key = st.text_input(
            "Groq API Key:",
            type="password",
            placeholder="gsk_...",
            help="Get your free key from console.groq.com",
        )

        if custom_api_key:
            if custom_api_key.startswith("gsk_"):
                api_key = custom_api_key
                os.environ["GROQ_API_KEY"] = custom_api_key
                st.success("✅ Using your custom API key")
            else:
                st.error("❌ API key should start with 'gsk_'")
        elif not api_key:
            st.info("👆 Enter your API key above to start testing")

    # Check if we have a valid API key
    if not api_key:
        st.warning("🔑 API Key Required")
        st.markdown("""
        ### 🚀 Quick Start Guide:
        1. **Get Free API Key**: Visit [Groq Console](https://console.groq.com/keys)
        2. **Sign up** (completely free, no credit card required)
        3. **Create API Key** and copy it
        4. **Paste it** in the sidebar input field
        5. **Start generating** professional news reports!
        
        ### ✨ What You Can Do:
        - 🎵 Generate audio news reports on any topic
        - 📊 Analyze social media discussions  
        - 🏆 Cover sports, technology, politics, and more
        - 💾 Download MP3 files for broadcasting
        """)
        return

    # Set the API key in environment for the session
    os.environ["GROQ_API_KEY"] = api_key

    # Main interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📝 News Topics")

        # Topic input
        new_topic = st.text_input(
            "Enter a news topic:",
            placeholder="e.g., NBA playoffs, Tesla earnings, AI technology...",
            key=f"topic_input_{st.session_state.input_key}",
        )

        col_add, col_clear = st.columns([1, 1])

        with col_add:
            if st.button("➕ Add Topic", use_container_width=True):
                if new_topic and new_topic.strip():
                    st.session_state.topics.append(new_topic.strip())
                    st.session_state.input_key += 1
                    st.rerun()

        with col_clear:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.topics = []
                st.rerun()

        # Display current topics
        if st.session_state.topics:
            st.markdown("**Current Topics:**")
            for i, topic in enumerate(st.session_state.topics):
                col_topic, col_remove = st.columns([4, 1])
                with col_topic:
                    st.write(f"• {topic}")
                with col_remove:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.topics.pop(i)
                        st.rerun()

    with col2:
        st.markdown("### 🎵 Audio Generation")

        if st.session_state.topics:
            if st.button(
                "🎙️ Generate News Report", type="primary", use_container_width=True
            ):
                with st.spinner("🔄 Generating professional news report..."):
                    try:
                        audio_file = generate_news_audio_streamlit(
                            st.session_state.topics
                        )

                        if audio_file:
                            st.success("✅ News report generated successfully!")

                            # Audio player
                            with open(audio_file, "rb") as f:
                                audio_bytes = f.read()

                            st.audio(audio_bytes, format="audio/mp3")

                            # Download button
                            st.download_button(
                                label="📥 Download MP3",
                                data=audio_bytes,
                                file_name=f"news_report_{len(st.session_state.topics)}_topics.mp3",
                                mime="audio/mp3",
                            )
                        else:
                            st.error("❌ Failed to generate audio. Please try again.")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info(
                            "💡 Try with different topics or check your connection."
                        )
        else:
            st.info("📝 Add some topics to generate a news report")

        # Quick topic suggestions
        st.markdown("### 💡 Quick Topics")
        suggestions = [
            "NBA playoffs",
            "Tesla stock",
            "AI technology",
            "Climate change",
            "Cryptocurrency",
        ]

        for suggestion in suggestions:
            if st.button(f"📌 {suggestion}", key=f"suggest_{suggestion}"):
                st.session_state.topics.append(suggestion)
                st.rerun()

    # Information section
    st.markdown("---")

    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.markdown("""
        ### 🎯 Features
        - **AI-Powered Analysis**: Advanced language models
        - **Social Media Integration**: Real-time discussions
        - **Professional Audio**: Broadcast-quality output
        - **Multi-Topic Support**: Comprehensive coverage
        """)

    with info_col2:
        st.markdown("""
        ### 🚀 How It Works
        1. **Add Topics**: Enter any news topics
        2. **AI Analysis**: Analyzes social media & news
        3. **Content Generation**: Creates professional reports
        4. **Audio Synthesis**: Converts to broadcast audio
        """)

    with info_col3:
        st.markdown("""
        ### ✨ Benefits
        - **Instant Results**: Fast AI processing
        - **Professional Quality**: Broadcast-ready audio
        - **Free Testing**: Generous usage limits
        - **Easy Download**: MP3 format support
        """)


def generate_news_audio_streamlit(topics: List[str]) -> str:
    """Generate news audio for given topics using Streamlit interface"""
    try:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Social Media Analysis
        status_text.text("🔍 Analyzing social media discussions...")
        progress_bar.progress(20)

        social_content = {}
        for topic in topics:
            try:
                content = analyze_social_media_discussion(topic)
                social_content[topic] = content
            except Exception as e:
                st.warning(f"Social analysis failed for {topic}: {str(e)}")
                social_content[topic] = f"Unable to analyze social media for {topic}"

        # Step 2: News Content Scraping
        status_text.text("📰 Gathering news content...")
        progress_bar.progress(40)

        news_content = {}
        for topic in topics:
            try:
                news_url = generate_valid_news_url(topic)
                content = scrape_with_brightdata(news_url)
                news_content[topic] = (
                    content[:1000] if content else f"Limited news data for {topic}"
                )
            except Exception as e:
                st.warning(f"News scraping failed for {topic}: {str(e)}")
                news_content[topic] = f"Unable to gather news for {topic}"

        # Step 3: AI Content Generation
        status_text.text("🤖 Generating professional news summary...")
        progress_bar.progress(60)

        combined_content = {
            "social_media": social_content,
            "news": news_content,
            "topics": topics,
        }

        news_summary = create_news_summary(combined_content)

        # Step 4: Audio Generation
        status_text.text("🎵 Creating audio broadcast...")
        progress_bar.progress(80)

        # Create temporary file for audio
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_file.close()

        # Generate audio using gTTS
        from gtts import gTTS

        tts = gTTS(text=news_summary, lang="en", slow=False)
        tts.save(audio_file.name)

        # Complete
        status_text.text("✅ News report completed!")
        progress_bar.progress(100)

        return audio_file.name

    except Exception as e:
        st.error(f"Error generating news audio: {str(e)}")
        return None


if __name__ == "__main__":
    main()
