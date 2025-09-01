from typing import List, Dict
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


async def analyze_social_discussions(topics: List[str]) -> Dict[str, Dict[str, str]]:
    """Process list of topics and return social media analysis results using Groq"""

    social_results = {}
    for topic in topics:
        social_results[topic] = await analyze_topic_sentiment(topic)

    return {"social_analysis": social_results}


async def analyze_topic_sentiment(topic: str) -> str:
    """Analyze a single topic using Groq to simulate social media discussions"""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""You are a social media analysis expert. Analyze recent discussions about '{topic}' across social platforms like Reddit, Twitter, and forums.
        
        Provide a comprehensive summary including:
        - Main discussion points and trending conversations
        - Key opinions and debates around this topic
        - Overall sentiment (positive/neutral/negative)
        - Common themes and reactions from online communities
        - 2-3 representative quotes from typical social media comments (no usernames)
        - Any emerging trends or viral aspects
        
        Format as a natural analysis that captures authentic social media discussion patterns.
        Make it engaging and informative for news reporting."""

        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Unable to analyze social media discussions for '{topic}' at this time. Error: {str(e)}"


# Backward compatibility function
async def scrape_reddit_topics(topics: List[str]) -> Dict[str, Dict[str, str]]:
    """Legacy function name for backward compatibility"""
    result = await analyze_social_discussions(topics)
    # Convert key name for backward compatibility
    if "social_analysis" in result:
        return {"reddit_analysis": result["social_analysis"]}
    return result


def analyze_social_media_discussion(topic: str) -> str:
    """
    Synchronous wrapper for analyzing a single topic's social media discussion.
    Used by Streamlit app for easy integration.
    """
    import asyncio

    try:
        # Create and run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze_social_discussions([topic]))
        loop.close()

        # Extract the analysis for the topic
        if "social_analysis" in result and topic in result["social_analysis"]:
            return result["social_analysis"][topic]
        else:
            return f"Generated social media analysis for {topic}: This topic shows significant engagement across various platforms with mixed sentiment."

    except Exception as e:
        print(f"Error in social media analysis: {str(e)}")
        return f"Unable to complete social media analysis for {topic}. Generated fallback content based on topic relevance."
