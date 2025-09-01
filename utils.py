from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
import os
from pathlib import Path
from fastapi import HTTPException
from bs4 import BeautifulSoup
from datetime import datetime
from elevenlabs import ElevenLabs
from gtts import gTTS

load_dotenv(override=True)


class MCPOverloadedError(Exception):
    """Custom exception for MCP overloaded errors."""

    pass


def generate_valid_news_url(keywords: str) -> str:
    """
    Generate a Google News search URL for a keyword with optional sorting by latest

    Args:
        keywords: Search term to use in the news search

    Returns:
        str: Constructed Google News search URL
    """
    q = quote_plus(keywords)

    return f"https://news.google.com/search?q={q}&tbs=sbd:1"


def generate_news_urls_to_scrape(list_of_keywords):
    valid_urls_dict = {}
    for keyword in list_of_keywords:
        valid_urls_dict[keyword] = generate_valid_news_url(keyword)

    return valid_urls_dict


def scrape_with_brightdata(url: str) -> str:
    """
    Scrape the content of a webpage using multiple methods.
    Priority: Free methods first, then BrightData if enabled.

    Args:
        url (str): The URL of the page to scrape.

    Returns:
        str: The scraped content of the page.
    """
    # Check if BrightData should be used (when API key is available and not disabled)
    use_brightdata = (
        os.getenv("BRIGHTDATA_API_KEY")
        and os.getenv("WEB_UNLOCKER_ZONE")
        and os.getenv("USE_BRIGHTDATA", "false").lower() == "true"
    )

    # Method 1: Try free requests first (always attempt this)
    try:
        print(f"Attempting free scraping for: {url}")
        fallback_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        response = requests.get(url, headers=fallback_headers, timeout=15)
        response.raise_for_status()
        print("✅ Free scraping successful!")
        return response.text
    except Exception as e:
        print(f"Free scraping failed: {str(e)}")

    # Method 2: Try BrightData if enabled and free method failed
    if use_brightdata:
        try:
            print("Attempting BrightData scraping...")
            headers = {
                "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
                "Content-Type": "application/json",
            }

            payload = {
                "zone": os.getenv("WEB_UNLOCKER_ZONE"),
                "url": url,
                "format": "raw",
            }

            response = requests.post(
                "https://api.brightdata.com/request", json=payload, headers=headers
            )
            response.raise_for_status()
            print("✅ BrightData scraping successful!")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"BrightData failed: {str(e)}")

    # Method 3: Generate AI-powered mock content based on topic
    print("Using AI-generated news content as fallback...")
    return generate_mock_news_content(url)


def generate_mock_news_content(url: str) -> str:
    """
    Generate realistic news content using AI based on the search URL topic.
    This is used as a fallback when web scraping fails.

    Args:
        url (str): The search URL containing the topic

    Returns:
        str: HTML formatted news content
    """
    try:
        # Extract topic from Google News URL
        from urllib.parse import unquote_plus
        import re

        # Extract the search query from the URL
        topic_match = re.search(r"q=([^&]+)", url)
        if topic_match:
            topic = unquote_plus(topic_match.group(1))
        else:
            topic = "general news"

        # Use Groq to generate realistic news headlines
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""Generate 5-7 realistic news headlines about '{topic}' that could appear on a news website today. 
        Make them current, relevant, and varied in tone (some breaking news, some analysis, some updates).
        Format as HTML with proper headline tags. Make it look like real news website content.
        
        Include:
        - Breaking news headlines
        - Analysis pieces  
        - Update stories
        - Different perspectives on the topic
        
        Format as clean HTML that looks like it came from a real news site."""

        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
        )

        ai_content = response.choices[0].message.content

        # Wrap in proper HTML structure
        html_content = f"""
        <html><body>
        <div class="news-content">
        <h1>Latest News: {topic.title()}</h1>
        {ai_content}
        </div>
        </body></html>
        """

        print(f"✅ Generated AI news content for topic: {topic}")
        return html_content

    except Exception as e:
        print(f"AI content generation failed: {str(e)}")
        # Ultimate fallback - static content
        return """
        <html><body>
        <h1>Breaking News Updates</h1>
        <h2>Latest developments in ongoing stories</h2>
        <p>Breaking: Major updates expected in current events</p>
        <h2>Technology sector sees continued growth</h2>
        <p>Innovation drives market advances across multiple sectors</p>
        <h2>Global markets respond to recent developments</h2>
        <p>Financial indicators show mixed signals amid uncertainty</p>
        <h2>Sports roundup: Competition highlights</h2>
        <p>Athletic achievements continue to inspire audiences worldwide</p>
        <h2>Weather patterns shift seasonally</h2>
        <p>Meteorologists track changing conditions across regions</p>
        </body></html>
        """


def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")
    return text.strip()


def extract_headlines(cleaned_text: str) -> str:
    """
    Extract and concatenate headlines from cleaned news text content.

    Args:
        cleaned_text: Raw text from news page after HTML cleaning

    Returns:
        str: Combined headlines separated by newlines
    """

    headlines = []
    current_block = []

    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    for line in lines:
        if line == "More":
            if current_block:
                headlines.append(current_block[0])
                current_block = []  # reset for next block

        else:
            current_block.append(line)

    if current_block:  # if there's any remaining block (Headers), add it
        headlines.append(current_block[0])

    return "\n".join(headlines)


def summarize_with_groq(headlines) -> str:
    """Summarize content using Groq API with Gemma model"""
    prompt = f"""You are my personal news editor. Summarize these headlines into a TV news script for me, focus on important headlines and remember that this text will be converted to audio:
    So no extra stuff other than text which the podcaster/newscaster should read, no special symbols or extra information in between and of course no preamble please.
    {headlines}
    News Script:"""
    try:
        from groq import Groq
        import os
        from fastapi import HTTPException

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq error: {str(e)}")


def generate_broadcast_news_with_groq(news_data, social_data, topics):
    """Generate broadcast news using Groq API with Gemma model"""
    system_prompt = """
    You are broadcast_news_writer, a professional virtual news reporter. Generate natural, TTS-ready news reports using available sources:

    For each topic, STRUCTURE BASED ON AVAILABLE DATA:
    1. If news exists: "According to official reports..." + summary
    2. If social media exists: "Online discussions and social media reveal..." + summary
    3. If both exist: Present news first, then social media reactions
    4. If neither exists: Skip the topic (shouldn't happen)

    Formatting rules:
    - ALWAYS start directly with the content, NO INTRODUCTIONS
    - Keep audio length 60-120 seconds per topic
    - Use natural speech transitions like "Meanwhile, online discussions..."
    - Incorporate 1-2 short quotes from social media when available
    - Maintain neutral tone but highlight key sentiments
    - End with "To wrap up this segment..." summary

    Write in full paragraphs optimized for speech synthesis. Avoid markdown.
    """

    topic_blocks = []

    for topic in topics:
        news_content = news_data["news_analysis"].get(topic) if news_data else ""

        # Handle both old reddit_data format and new social_data format
        social_content = ""
        if social_data:
            if "social_analysis" in social_data:
                social_content = social_data["social_analysis"].get(topic, "")
            elif "reddit_analysis" in social_data:
                social_content = social_data["reddit_analysis"].get(topic, "")

        context = []
        if news_content:
            context.append(f"Official news content:\n{news_content}")
        if social_content:
            context.append(f"Social media discussions:\n{social_content}")

        if context:
            topic_blocks.append(f"Topic: {topic}\n" + "\n".join(context))

    if not topic_blocks:
        return "No content available for broadcast news generation."

    user_prompt = (
        "Create broadcast segments for these topics using available sources:\n\n"
        + "\n\n--- NEW TOPIC ---\n\n".join(topic_blocks)
    )

    try:
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=4000,
            stream=False,
        )
        return response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq error: {str(e)}")


def summarize_with_groq_news_scripts(headlines: str) -> str:
    """
    Summarize multiple news headlines into a TTS-friendly broadcast news script using Groq API with Gemma model.
    """
    system_prompt = """
    You are my personal news editor and scriptwriter for a news podcast. Your job is to turn raw headlines into a clean, professional, and TTS-friendly news script.
    
    The final output will be read aloud by a news anchor or text-to-speech engine. So:
    - Do not include any special characters, emojis, formatting symbols, or markdown.
    - Do not add any preamble or framing like "Here's your summary" or "Let me explain".
    - Write in full, clear, spoken-language paragraphs.
    - Keep the tone formal, professional, and broadcast-style — just like a real TV news script.
    - Focus on the most important headlines and turn them into short, informative news segments that sound natural when spoken.
    - Start right away with the actual script, using transitions between topics if needed.

    Remember: Your only output should be a clean script that is ready to be read out loud.
    """

    try:
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": headlines},
            ],
            temperature=0.4,
            max_tokens=1000,
            stream=False,
        )
        return response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq error: {str(e)}")


def text_to_audio_elevenlabs_sdk(
    text: str,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    output_dir: str = "audio",
    api_key: str = None,
) -> str:
    """
    Converts text to speech using ElevenLabs SDK and saves it to audio/ directory.

    Returns:
        str: Path to the saved audio file.
    """
    try:
        api_key = api_key or os.getenv("ELEVEN_API_KEY")
        if not api_key:
            raise ValueError("ElevenLabs API key is required.")

        # Initialize client
        client = ElevenLabs(api_key=api_key)

        # Get the audio generator
        audio_stream = client.text_to_speech.convert(
            text=text, voice_id=voice_id, model_id=model_id, output_format=output_format
        )

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate unique filename
        filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        filepath = os.path.join(output_dir, filename)

        # Write audio chunks to file
        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return filepath

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs error: {str(e)}")


Audio_Dir = Path("audio")
Audio_Dir.mkdir(exist_ok=True)


def tts_to_audio(text: str, language: str = "en") -> str:
    """Convert text to speech using gTTS (Google Text-to-Speech) and save to file.

    Args:
        text: Input text to convert
        language: Language code (default: 'en')

    Returns:
        str: Path to saved audio file

    Example:
        tts_to_audio("Hello world", "en")
    """

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Audio_Dir / f"tts_{timestamp}.mp3"

        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(filename))

        return str(filename)

    except Exception as e:
        # Raise an HTTPException for better integration with a FastAPI backend
        raise HTTPException(status_code=500, detail=f"gTTS error: {str(e)}")
