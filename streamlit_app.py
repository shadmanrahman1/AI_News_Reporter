import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="🎙️ AI News Reporter",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Import backend functions - Direct imports instead of API calls
try:
    from news_scraper import NewsScraper
    from social_analyzer import analyze_social_discussions
    from utils import generate_broadcast_news_with_groq, tts_to_audio
except ImportError as e:
    st.error(f"Import error: {e}")


# Async wrapper functions for Streamlit compatibility
def run_async(coro):
    """Helper to run async functions in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def generate_news_content_direct(topics, source_type="both"):
    """Direct function call instead of API call"""
    try:
        # Initialize scraper
        scraper = NewsScraper()
        
        # Process news
        news_results = {}
        social_results = {}
        
        if source_type in ["both", "news"]:
            for topic in topics:
                news_data = run_async(scraper.scrape_topic_news(topic))
                news_results[topic] = news_data
        
        if source_type in ["both", "social_media"]:
            for topic in topics:
                social_data = run_async(analyze_social_discussions(topic))
                social_results[topic] = social_data
        
        # Generate broadcast news
        news_summary = generate_broadcast_news_with_groq(
            news_results=news_results,
            social_results=social_results,
            topics=topics
        )
        
        # Generate audio
        audio_path = tts_to_audio(news_summary)
        
        return {
            "news_summary": news_summary,
            "audio_path": audio_path,
            "news_results": news_results,
            "social_results": social_results
        }
        
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None


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

    # API Key Configuration - Support both environment and Streamlit secrets
    api_key = os.getenv("GROQ_API_KEY")
    
    # Try Streamlit secrets if no environment variable
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            os.environ["GROQ_API_KEY"] = api_key
        except (AttributeError, KeyError):
            pass

    # If no API key found, show user input
    if not api_key:
        st.sidebar.header("⚙️ Setup")
        st.sidebar.markdown("### 🔑 API Key Required")
        st.sidebar.info(
            "Get your free API key from [Groq Console](https://console.groq.com/keys)"
        )

        user_api_key = st.sidebar.text_input(
            "Enter your Groq API Key:",
            type="password",
            placeholder="gsk_...",
            help="Your API key should start with 'gsk_'",
        )

        if user_api_key:
            st.session_state.user_api_key = user_api_key
            # Set environment variable for this session
            os.environ["GROQ_API_KEY"] = user_api_key
            st.sidebar.success("✅ API Key configured!")
            st.rerun()
        else:
            st.warning(
                "🔑 Please enter your Groq API key in the sidebar to get started."
            )
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

    # Show current configuration status
    if api_key or st.session_state.user_api_key:
        st.sidebar.success("✅ API Key: Configured")
        st.sidebar.caption("Ready to generate news reports!")

    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        source_type = st.selectbox(
            "Data Source",
            options=["Both", "News", "Social Media"],
            format_func=lambda x: {
                "Both": "📱 Social Media & 📰 News",
                "News": "📰 News",
                "Social Media": "📱 Social Media",
            }[x],
            help="Choose your data sources for news generation",
        )

        # Convert to backend format
        source_mapping = {
            "Both": "both",
            "News": "news",
            "Social Media": "social_media",
        }
        backend_source = source_mapping[source_type]

    # Main content area
    st.markdown("### 📝 Enter News Topics")

    col1, col2 = st.columns([3, 1])

    with col1:
        topic_input = st.text_input(
            "What news topic would you like to cover?",
            placeholder="e.g., Barcelona FC, AI technology, climate change...",
            key=f"topic_input_{st.session_state.input_key}",
            help="Enter any topic you want news coverage on",
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Topic", use_container_width=True):
            if topic_input.strip():
                st.session_state.topics.append(topic_input.strip())
                st.session_state.input_key += 1
                st.rerun()

    # Display current topics
    if st.session_state.topics:
        st.markdown("### 📋 Current Topics:")
        for i, topic in enumerate(st.session_state.topics):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i+1}.** {topic}")
            with col2:
                if st.button("🗑️", key=f"delete_{i}", help="Remove topic"):
                    st.session_state.topics.pop(i)
                    st.rerun()

        # Clear all topics
        if st.button("🗑️ Clear All Topics"):
            st.session_state.topics = []
            st.rerun()

        # Generate news button
        st.markdown("---")
        if st.button("🎙️ Generate News Report", use_container_width=True, type="primary"):
            if not st.session_state.topics:
                st.warning("Please add at least one topic!")
                return

            with st.spinner("🔍 Gathering news and generating report..."):
                # Direct function call instead of API call
                result = generate_news_content_direct(
                    topics=st.session_state.topics,
                    source_type=backend_source
                )

                if result and result.get("news_summary"):
                    st.success("✅ News report generated successfully!")

                    # Display news summary
                    st.markdown("### 📰 Generated News Report")
                    st.markdown(result["news_summary"])

                    # Audio player
                    if result.get("audio_path") and os.path.exists(result["audio_path"]):
                        st.markdown("### 🎵 Audio Report")
                        
                        try:
                            with open(result["audio_path"], "rb") as audio_file:
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format="audio/mp3")
                                
                                # Download button
                                st.download_button(
                                    label="⬇️ Download Audio Report",
                                    data=audio_bytes,
                                    file_name=f"news_report_{len(st.session_state.topics)}_topics.mp3",
                                    mime="audio/mp3"
                                )
                        except Exception as e:
                            st.error(f"Error loading audio: {e}")

                    # Show data sources (expandable)
                    with st.expander("📊 View Source Data"):
                        if result.get("news_results"):
                            st.markdown("**📰 News Sources:**")
                            for topic, data in result["news_results"].items():
                                st.markdown(f"- **{topic}**: {len(str(data))} characters of news data")
                        
                        if result.get("social_results"):
                            st.markdown("**📱 Social Media Sources:**")
                            for topic, data in result["social_results"].items():
                                st.markdown(f"- **{topic}**: Social analysis completed")

                else:
                    st.error("❌ Failed to generate news report. Please try again.")

    else:
        st.info("👆 Add some topics above to get started!")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            🎙️ AI News Reporter - Powered by Groq AI | Free Tier Operation
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
