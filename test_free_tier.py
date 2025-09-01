#!/usr/bin/env python3
"""Test script for free-tier news scraping functionality."""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from utils import scrape_with_brightdata, generate_valid_news_url
from news_scraper import NewsScraper


async def test_free_tier():
    """Test the free tier scraping functionality."""

    print("🧪 Testing Free Tier News Scraping")
    print("=" * 50)

    # Test 1: Direct URL scraping
    print("\n1. Testing direct URL scraping...")
    test_url = generate_valid_news_url("artificial intelligence")
    print(f"Generated URL: {test_url}")

    try:
        content = scrape_with_brightdata(test_url)
        print(f"✅ Scraping successful! Content length: {len(content)} characters")
        print(f"First 200 chars: {content[:200]}...")
    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")

    # Test 2: News scraper integration
    print("\n2. Testing NewsScraper integration...")
    try:
        scraper = NewsScraper()
        results = await scraper.scrape_news(["technology"])
        print(f"✅ News scraping successful!")
        print(f"Results: {results}")
    except Exception as e:
        print(f"❌ News scraping failed: {str(e)}")

    print("\n" + "=" * 50)
    print("✅ Free tier testing complete!")


if __name__ == "__main__":
    asyncio.run(test_free_tier())
