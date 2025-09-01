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
