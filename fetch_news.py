import urllib.request
import xml.etree.ElementTree as ET
import json
import re
import html
import subprocess
import sys

# Ensure dependencies are installed
def install_deps():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator", "feedparser", "beautifulsoup4"])

try:
    from deep_translator import GoogleTranslator
    import feedparser
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing dependencies...")
    install_deps()
    from deep_translator import GoogleTranslator
    import feedparser
    from bs4 import BeautifulSoup

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

def translate_text(text):
    if not text:
        return ""
    try:
        # Translate up to 4000 chars
        if len(text) > 4000:
            text = text[:4000] + "..."
        translator = GoogleTranslator(source='auto', target='pt')
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

FEEDS = [
    {"name": "Phoronix", "url": "https://www.phoronix.com/rss.php"},
    {"name": "LWN", "url": "https://lwn.net/headlines/newrss"},
    {"name": "Planet Kernel", "url": "https://planet.kernel.org/rss20.xml"}
]

news_items = []

for feed_info in FEEDS:
    print(f"Fetching {feed_info['name']}...")
    try:
        d = feedparser.parse(feed_info['url'])
        # Get up to 15 latest items from each feed
        for entry in d.entries[:15]:
            title_en = html.unescape(entry.title) if hasattr(entry, 'title') else ""
            
            summary_en = ""
            if hasattr(entry, 'summary'):
                summary_en = entry.summary
            elif hasattr(entry, 'description'):
                summary_en = entry.description
            
            summary_en = clean_html(summary_en).strip()
            
            # Truncate summary if it's too long (Planet Kernel can be huge)
            if len(summary_en) > 300:
                summary_en = summary_en[:297] + "..."

            link = entry.link if hasattr(entry, 'link') else ""
            
            # We will try to find a date
            date = ""
            if hasattr(entry, 'published'):
                date = entry.published
            elif hasattr(entry, 'updated'):
                date = entry.updated

            # Translate!
            title_pt = translate_text(title_en)
            summary_pt = translate_text(summary_en)

            news_items.append({
                "source": feed_info['name'],
                "title_en": title_en,
                "title_pt": title_pt,
                "summary_en": summary_en,
                "summary_pt": summary_pt,
                "link": link,
                "date": date
            })
    except Exception as e:
        print(f"Error fetching {feed_info['name']}: {e}")

# Save to news.json
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(news_items, f, ensure_ascii=False, indent=2)

print(f"Generated news.json with {len(news_items)} news items.")
