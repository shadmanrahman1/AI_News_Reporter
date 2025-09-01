import asyncio
from typing import Dict, List

from aiolimiter import AsyncLimiter
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from dotenv import load_dotenv

from utils import (
    generate_news_urls_to_scrape,
    scrape_with_brightdata,
    clean_html,
    extract_headlines,
    summarize_with_groq,
)

load_dotenv()


class NewsScraper:
    _rate_limiter = AsyncLimiter(5, 1)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def scrape_news(self, topics: List[str]) -> Dict[str, str]:
        """Scrape and Analyze news articles based on provided topics."""
        results = {}

        for topic in topics:
            async with self._rate_limiter:
                try:
                    urls = generate_news_urls_to_scrape([topic])
                    search_html = scrape_with_brightdata(urls[topic])
                    clean_text = clean_html(search_html)
                    headlines = extract_headlines(clean_text)

                    summary = summarize_with_groq(headlines)

                    results[topic] = summary
                except Exception as e:
                    results[topic] = f"Error: {str(e)}"

                await asyncio.sleep(1)

        return {"news_analysis": results}
