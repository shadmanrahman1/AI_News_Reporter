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

# Import backend functions
try:
    from news_scraper import NewsScraper
    from social_analyzer import analyze_social_discussions
    from utils import generate_broadcast_news_with_groq, tts_to_audio
except ImportError as e:
    st.error(f"Import error: {e}")


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

    # API Key Configuration
    api_key = os.getenv("GROQ_API_KEY")

    # If no environment API key, show user input
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
        )

        st.markdown("---")
        st.markdown("### 📊 Current Configuration")
        st.success("✅ Free Tier Mode")
        st.info("📈 Zero monthly costs")
        st.info("🤖 AI-powered content generation")

    # Topic Management
    st.markdown("#### 📝 Topic Management")
    col1, col2 = st.columns([4, 1])

    with col1:
        new_topic = st.text_input(
            "Enter a topic for news analysis",
            key=f"topic_input_{st.session_state.input_key}",
            placeholder="e.g., 'Technology', 'Politics', 'Finance', 'Sports'",
        )

    with col2:
        add_disabled = len(st.session_state.topics) >= 3 or not new_topic.strip()
        if st.button("Add ➕", disabled=add_disabled):
            st.session_state.topics.append(new_topic.strip())
            st.session_state.input_key += 1
            st.rerun()

    # Display current topics
    if st.session_state.topics:
        st.subheader("✅ Current Topics")
        for i, topic in enumerate(st.session_state.topics[:3]):
            cols = st.columns([4, 1])
            cols[0].write(f"{i + 1}. {topic}")
            if cols[1].button("Remove ❌", key=f"remove_{i}"):
                del st.session_state.topics[i]
                st.rerun()

    # News Generation
    st.markdown("---")
    st.subheader("🎙️ Generate News Broadcast")

    if st.button("🚀 Generate News Audio", disabled=len(st.session_state.topics) == 0):
        if not st.session_state.topics:
            st.error("Please add at least one topic to generate a news broadcast.")
        else:
            generate_news_audio_streamlit(st.session_state.topics, source_type)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>🎙️ AI News Reporter</strong> - Professional News Broadcasting Powered by AI</p>
            <p>Built with FastAPI + Streamlit + Groq AI + Google TTS</p>
            <p><em>Transforming social media discussions into professional news broadcasts</em></p>
            <p>🌐 <strong>Free Tier Mode</strong> - Zero monthly costs | 🚀 <strong>Deployed on Streamlit Cloud</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def generate_news_audio_streamlit(topics, source_type):
    """Generate news audio directly in Streamlit (backend functionality integrated)"""

    with st.spinner(
        "🔍 Analyzing discussions and generating professional news broadcast..."
    ):
        try:
            # Map frontend values to backend values
            source_mapping = {"Social Media": "social", "News": "news", "Both": "both"}
            backend_source_type = source_mapping.get(source_type, source_type.lower())

            # Initialize results
            results = {}

            # Process news if requested
            if backend_source_type in ["news", "both"]:
                st.info("📰 Processing news sources...")
                news_scraper = NewsScraper()

                # Run async function in Streamlit
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results["news"] = loop.run_until_complete(
                        news_scraper.scrape_news(topics)
                    )
                finally:
                    loop.close()

                st.success(
                    f"✅ News analysis complete: {len(results.get('news', {}).get('news_analysis', {}))} topics"
                )

            # Process social media if requested
            if backend_source_type in ["social", "both"]:
                st.info("📱 Processing social media discussions...")

                # Run async function in Streamlit
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results["social"] = loop.run_until_complete(
                        analyze_social_discussions(topics)
                    )
                finally:
                    loop.close()

                st.success(
                    f"✅ Social media analysis complete: {len(results.get('social', {}).get('social_analysis', {}))} topics"
                )

            # Generate broadcast news
            st.info("🎙️ Generating professional broadcast script...")
            news_data = results.get("news", {})
            social_data = results.get("social", {})

            news_summary = generate_broadcast_news_with_groq(
                news_data, social_data, topics
            )

            if news_summary:
                st.success(
                    f"✅ Broadcast script generated ({len(news_summary)} characters)"
                )

                # Show preview of the script
                with st.expander("📄 Preview Generated Script"):
                    st.write(
                        news_summary[:500] + "..."
                        if len(news_summary) > 500
                        else news_summary
                    )

                # Generate audio
                st.info("🔊 Converting to audio...")
                audio_path = tts_to_audio(text=news_summary, language="en")

                if audio_path and Path(audio_path).exists():
                    st.success("✅ Audio generation successful!")

                    # Display audio player
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()

                    st.audio(audio_bytes, format="audio/mpeg")

                    # Download button
                    st.download_button(
                        label="📥 Download Audio Summary",
                        data=audio_bytes,
                        file_name=f"news_summary_{'-'.join(topics[:2])}.mp3",
                        mime="audio/mpeg",
                    )

                else:
                    st.error("❌ Audio generation failed")
            else:
                st.error("❌ Failed to generate news summary")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()
