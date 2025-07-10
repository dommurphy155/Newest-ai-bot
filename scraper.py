import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_html(session, url):
    async with session.get(url) as response:
        return await response.text()

async def scrape_news():
    urls = [
        "https://www.investing.com/news/forex-news",
        "https://www.forexfactory.com/",
        # Add up to 20 trusted sources
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, url) for url in urls]
        pages = await asyncio.gather(*tasks)
        # Parse pages with BeautifulSoup and extract news headlines or sentiment
        # Placeholder logic here
        results = []
        for page in pages:
            soup = BeautifulSoup(page, 'html.parser')
            # Extract headlines or sentiment
            results.append('Sample headline or sentiment')
        return results