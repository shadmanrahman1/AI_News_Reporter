# setup steamlit
import streamlit as st
import requests

# Configure page
st.set_page_config(
    page_title="AI News Reporter",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded"
)

BACKENED_URL = "http://localhost:1234"


def main():
    st.title("🎙️ AI News Reporter")
    st.subheader("Professional News Broadcasting Powered by AI")

    # Initialize the session state
    if "topics" not in st.session_state:
        st.session_state.topics = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

    # Setup sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        source_type = st.selectbox(
            "Data Source",
            options=["Both", "News", "Social Media"],
            format_func=lambda x: {
                "Both": "� Social Media & 📰 News",
                "News": "📰 News",
                "Social Media": "� Social Media",
            }[x],
        )

    # Topic Management
    st.markdown("#### 📝 Topic Management")
    col1, col2 = st.columns([4, 1])
    with col1:
        new_topic = st.text_input(
            "Enter a topic for news analysis",
            key=f"topic_intput_{st.session_state.input_key}",
            placeholder="e.g., 'Technology', 'Politics', 'Finance', 'Entertainment'",
        )
    with col2:
        add_disabled = len(st.session_state.topics) >= 3 or not new_topic.strip()
        if st.button("Add ➕ ", disabled=add_disabled):
            st.session_state.topics.append(new_topic.strip())
            st.session_state.input_key += 1
            st.rerun()

    # Add or remove topics

    if st.session_state.topics:
        st.subheader("✅ Current Topics")
        for i, topic in enumerate(st.session_state.topics[:3]):
            cols = st.columns([4, 1])
            cols[0].write(f"{i + 1}. {topic}")
            if cols[1].button("Remove ❌", key=f"remove_{i}"):
                del st.session_state.topics[i]
                st.rerun()

    # Analysis Controls
    st.markdown("----")
    st.subheader("🎙️ Generate News Broadcast")

    if st.button("🚀 Generate News Audio", disabled=len(st.session_state.topics) == 0):
        if not st.session_state.topics:
            st.error("Please add at least one topic to generate a news broadcast.")
        else:
            with st.spinner("🔍 Analyzing discussions and generating professional news broadcast..."):
                try:
                    # Map frontend values to backend values
                    source_mapping = {
                        "Social Media": "social",
                        "News": "news",
                        "Both": "both"
                    }
                    backend_source_type = source_mapping.get(source_type, source_type.lower())
                    
                    response = requests.post(
                        f"{BACKENED_URL}/generate-news-audio",
                        json={
                            "topics": st.session_state.topics,
                            "source_type": backend_source_type,
                        },
                    )

                    if response.status_code == 200:
                        st.audio(response.content, format="audio/mpeg")
                        st.download_button(
                            "Download Audio Summary",
                            data=response.content,
                            file_name="news_summary.mp3",
                            type="primary",
                        )
                    else:
                        handle_api_error(response)

                except requests.exceptions.ConnectionError:
                    st.error("🪧 Connection Error: Could not reach the backend server.")
                except Exception as e:
                    st.error(f"⁉️Unexpected error: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>🎙️ AI News Reporter</strong> - Professional News Broadcasting Powered by AI</p>
            <p>Built with FastAPI + Streamlit + Groq AI + Google TTS</p>
            <p><em>Transforming social media discussions into professional news broadcasts</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )


def handle_api_error(response):
    try:
        error_detail = response.json().get("details", "Error occurred")
        st.error(f"API Error: ({response.status_code}): {error_detail}")
    except ValueError:
        st.error(f"Unexpected error: {response.text}")


if __name__ == "__main__":
    main()
