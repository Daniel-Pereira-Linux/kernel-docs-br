import urllib.request
import xml.etree.ElementTree as ET
import json
import re
import html
import os
import sys

# Ensure dependencies
import subprocess
def install_deps():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator", "feedparser", "beautifulsoup4"])

try:
    from deep_translator import GoogleTranslator
    import feedparser
    from bs4 import BeautifulSoup
except ImportError:
    install_deps()
    from deep_translator import GoogleTranslator
    import feedparser
    from bs4 import BeautifulSoup

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator='\n\n')

def translate_long_text(text):
    if not text:
        return ""
    try:
        translator = GoogleTranslator(source='en', target='pt')
        # Google Translate API has a 5000 character limit per request.
        # We split by paragraphs.
        paragraphs = text.split('\n')
        translated_paragraphs = []
        chunk = ""
        for p in paragraphs:
            if len(chunk) + len(p) < 4500:
                chunk += p + "\n"
            else:
                if chunk.strip():
                    translated_paragraphs.append(translator.translate(chunk))
                chunk = p + "\n"
        if chunk.strip():
            translated_paragraphs.append(translator.translate(chunk))
            
        return "\n".join(translated_paragraphs)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def scrape_lwn_article(url):
    print(f"Scraping {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        html_content = resp.read().decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Check if it's subscriber only
        if "Please consider subscribing" in html_content or "requires a subscription" in html_content:
            return None # Locked
            
        article_div = soup.find("div", class_="ArticleText")
        if not article_div:
            return None
            
        # Remove script tags or unwanted elements
        for script in article_div(["script", "style"]):
            script.extract()
            
        return article_div.get_text(separator='\n').strip()
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

# Load existing news to avoid duplicates and act as a database
news_db_path = "news.json"
news_items = []
if os.path.exists(news_db_path):
    try:
        with open(news_db_path, "r", encoding="utf-8") as f:
            news_items = json.load(f)
    except Exception as e:
        print("Could not load existing news.json:", e)

# Track existing URLs
existing_urls = set([item.get('link') for item in news_items])

feed_url = "https://lwn.net/headlines/newrss"
print(f"Fetching LWN RSS...")
try:
    d = feedparser.parse(feed_url)
    new_entries = []
    
    # Process oldest first so they are appended in chronological order,
    # or process newest and insert at beginning.
    # d.entries are usually newest first. Let's reverse them.
    for entry in reversed(d.entries):
        link = entry.link if hasattr(entry, 'link') else ""
        if not link or link in existing_urls:
            continue
            
        title_en = html.unescape(entry.title) if hasattr(entry, 'title') else ""
        
        # Filter out obvious paid articles that start with [$]
        if title_en.startswith("[$]"):
            print(f"Skipping paid article: {title_en}")
            continue

        date = ""
        if hasattr(entry, 'published'):
            date = entry.published
        elif hasattr(entry, 'updated'):
            date = entry.updated
            
        print(f"Found new article: {title_en}")
        
        full_text_en = scrape_lwn_article(link)
        if not full_text_en:
            print(f"Could not extract full text or is paid, skipping: {link}")
            continue
            
        # Translate
        title_pt = translate_long_text(title_en)
        full_text_pt = translate_long_text(full_text_en)
        
        new_item = {
            "source": "LWN",
            "title_en": title_en,
            "title_pt": title_pt,
            "content_en": full_text_en,
            "content_pt": full_text_pt,
            "link": link,
            "date": date
        }
        
        # Prepend new item (newest at top)
        news_items.insert(0, new_item)
        existing_urls.add(link)

    # Save to news.json
    with open(news_db_path, "w", encoding="utf-8") as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)

    print(f"Added {len(news_items) - len(existing_urls) + len(new_entries)} new articles. Total: {len(news_items)}")
except Exception as e:
    print(f"Error fetching LWN: {e}")
