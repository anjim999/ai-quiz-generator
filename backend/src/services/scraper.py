"""
Wikipedia Scraper Service
=========================
Scrapes Wikipedia articles using BeautifulSoup.

As per assignment requirements:
- Library: BeautifulSoup
- Data source: Wikipedia article URLs (HTML scraping only, no Wikipedia API)
"""

import logging
from typing import Tuple, List
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Headers for requests (mimics a real browser to avoid 403 errors)
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

# Main content selector for Wikipedia articles
MAIN_SELECTOR = "#mw-content-text .mw-parser-output"

# Elements to remove from the content
ELEMENTS_TO_REMOVE = [
    "table",
    "style",
    "script",
    "noscript",
    "figure",
    "span.mw-editsection",
    "div.navbox",
    "div.reflist",
    "ol.references",
    "sup.reference",
    "div.toc",
    "div.thumb",
    "div.sidebar",
    "div.infobox",
    ".mw-empty-elt"
]


def clean_wikipedia_html(html: str) -> dict:
    """
    Clean Wikipedia HTML and extract useful content.
    
    Args:
        html: Raw HTML from Wikipedia
        
    Returns:
        Dict with:
        - title: Article title
        - cleaned_html: Cleaned HTML of main content
        - cleaned_text: Plain text content
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Extract title
    title_elem = soup.select_one("#firstHeading")
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
    
    # Find main content
    main_content = soup.select_one(MAIN_SELECTOR)
    
    if not main_content:
        logger.warning("Could not find main content selector")
        return {
            "title": title,
            "cleaned_html": html,
            "cleaned_text": ""
        }
    
    # Remove unwanted elements
    for selector in ELEMENTS_TO_REMOVE:
        for element in main_content.select(selector):
            element.decompose()
    
    # Extract text from paragraphs and list items
    parts = []
    for element in main_content.select("p, li"):
        text = element.get_text(separator=" ", strip=True)
        # Clean up whitespace
        text = " ".join(text.split())
        if text and len(text) > 10:  # Skip very short fragments
            parts.append(text)
    
    return {
        "title": title,
        "cleaned_html": str(main_content),
        "cleaned_text": "\n".join(parts)
    }


async def scrape_wikipedia(url: str) -> Tuple[str, str, List[str], str]:
    """
    Scrape a Wikipedia article.
    
    Args:
        url: Wikipedia article URL
        
    Returns:
        Tuple of (title, cleaned_text, sections, raw_html)
        
    Raises:
        Exception: If scraping fails
    """
    logger.info(f"Scraping Wikipedia article: {url}")
    
    try:
        # Use requests library which handles cookies better than httpx
        import requests as sync_requests
        import asyncio
        
        def fetch_url():
            session = sync_requests.Session()
            session.headers.update(BROWSER_HEADERS)
            response = session.get(url, timeout=20, allow_redirects=True)
            response.raise_for_status()
            return response.text
        
        # Run sync request in thread pool
        raw_html = await asyncio.to_thread(fetch_url)
        
    except sync_requests.Timeout:
        logger.error(f"Timeout while scraping {url}")
        raise Exception("Request timeout while fetching Wikipedia article")
    except sync_requests.HTTPError as e:
        logger.error(f"HTTP error while scraping {url}: {e}")
        raise Exception(f"Failed to fetch article: HTTP {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        raise Exception(f"Failed to fetch Wikipedia article: {str(e)}")
    
    # Clean the HTML
    result = clean_wikipedia_html(raw_html)
    title = result["title"]
    cleaned_text = result["cleaned_text"]
    cleaned_html = result["cleaned_html"]
    
    # Extract section headings
    soup = BeautifulSoup(cleaned_html, "lxml")
    sections = []
    for heading in soup.select("h2, h3"):
        text = heading.get_text(strip=True)
        # Remove [edit] links
        text = text.replace("[edit]", "").strip()
        if text and text not in ["Contents", "See also", "References", "External links", "Notes"]:
            sections.append(text)
    
    logger.info(f"Scraped article: {title} ({len(cleaned_text)} chars, {len(sections)} sections)")
    
    return (title, cleaned_text, sections, raw_html)


async def get_article_preview(url: str) -> dict:
    """
    Get a quick preview of a Wikipedia article (title and first paragraph).
    Used for URL validation and preview feature.
    
    Args:
        url: Wikipedia article URL
        
    Returns:
        Dict with title and preview text
    """
    try:
        import requests as sync_requests
        import asyncio
        
        def fetch_url():
            session = sync_requests.Session()
            session.headers.update(BROWSER_HEADERS)
            response = session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            return response.text
        
        html = await asyncio.to_thread(fetch_url)
        soup = BeautifulSoup(html, "lxml")
        
        title_elem = soup.select_one("#firstHeading")
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"
        
        # Get first paragraph
        first_p = soup.select_one("#mw-content-text .mw-parser-output > p:not(.mw-empty-elt)")
        preview = ""
        if first_p:
            preview = first_p.get_text(strip=True)[:300]
            if len(first_p.get_text(strip=True)) > 300:
                preview += "..."
        
        return {
            "title": title,
            "preview": preview,
            "valid": True
        }
        
    except Exception as e:
        logger.error(f"Error getting article preview: {e}")
        return {
            "title": "",
            "preview": "",
            "valid": False,
            "error": str(e)
        }
