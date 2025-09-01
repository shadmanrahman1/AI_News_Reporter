from fastapi import FastAPI, HTTPException, Response
from pathlib import Path

from models import NewsRequest
from news_scraper import NewsScraper
from social_analyzer import analyze_social_discussions

app = FastAPI()


@app.post("/generate-news-audio")
async def generate_news_audio(request: NewsRequest):
    try:
        print(
            f"Received request: topics={request.topics}, source_type={request.source_type}"
        )
        results = {}

        # Process both news and social media based on source_type
        if request.source_type.lower() in ["news", "both"]:
            print("Processing news...")
            news_scraper = NewsScraper()
            results["news"] = await news_scraper.scrape_news(request.topics)
            print(
                f"News results: {len(results.get('news', {}).get('news_analysis', {})) if results.get('news') else 0} topics"
            )

        if request.source_type.lower() in ["reddit", "social", "both"]:
            print("Processing social media...")
            results["social"] = await analyze_social_discussions(request.topics)
            print(
                f"Social results: {len(results.get('social', {}).get('social_analysis', {})) if results.get('social') else 0} topics"
            )

        news_data = results.get("news", {})
        social_data = results.get("social", {})

        # Use Groq instead of Ollama for faster processing
        print("Generating broadcast news...")
        from utils import generate_broadcast_news_with_groq

        # Generate broadcast news using both sources
        news_summary = generate_broadcast_news_with_groq(
            news_data, social_data, request.topics
        )
        print(f"Generated summary length: {len(news_summary) if news_summary else 0}")

        # Use free gTTS instead of ElevenLabs
        print("Converting to audio...")
        from utils import tts_to_audio

        audio_path = tts_to_audio(text=news_summary, language="en")
        print(f"Audio path: {audio_path}")

        if audio_path and Path(audio_path).exists():
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=news_summary.mp3"
                },
            )
        else:
            raise HTTPException(
                status_code=500, detail="Audio file could not be generated or found."
            )

    except Exception as e:
        print(f"Error in generate_news_audio: {str(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}


@app.post("/test-groq")
async def test_groq_only():
    """Test endpoint that only uses Groq for text generation"""
    try:
        from utils import summarize_with_groq

        test_text = "Breaking news: Local team wins championship"
        summary = summarize_with_groq(test_text)
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend:app", host="0.0.0.0", port=1234, reload=True)
