import urllib.request
import json
import re
import html
import os
import sys
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
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=' ').strip()

def translate_text(text):
    if not text:
        return ""
    try:
        if len(text) > 3000:
            text = text[:3000] + "..."
        translator = GoogleTranslator(source='auto', target='pt')
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Strict filter for Kernel news
KERNEL_KEYWORDS = [
    "kernel", "linus torvalds", "torvalds", "merge window", "mainline",
    "linux 7.", "linux 6.", "linux 5.", "kbuild", "kconfig", "kvm", "ebpf",
    "bpf", "vfs", "cgroup", "scheduler", "drm subsystem", "linux patches",
    "lore.kernel.org"
]

def is_kernel_related(title, summary, source):
    # Kernel.org releases are always 100% kernel
    if source.lower() == "kernel.org":
        return True
        
    text = (title + " " + summary).lower()
    
    for kw in KERNEL_KEYWORDS:
        if kw in text:
            return True
    
    # Catch releases like 7.3-rc1 or just rc1, rc2...
    if re.search(r'\brc[1-9]\b', text):
        return True
        
    return False

FEEDS = [
    {"name": "Phoronix", "url": "https://www.phoronix.com/rss.php"},
    {"name": "LWN", "url": "https://lwn.net/headlines/newrss"},
    {"name": "Planet Kernel", "url": "https://planet.kernel.org/rss20.xml"},
    {"name": "Kernel.org", "url": "https://www.kernel.org/feeds/kdist.xml"}
]

news_db_path = "news.json"
news_items = []
if os.path.exists(news_db_path):
    try:
        with open(news_db_path, "r", encoding="utf-8") as f:
            news_items = json.load(f)
    except Exception as e:
        print("Could not load existing news.json:", e)

existing_urls = set([item.get('link') for item in news_items])
new_additions = 0

for feed_info in FEEDS:
    print(f"Fetching {feed_info['name']}...")
    try:
        d = feedparser.parse(feed_info['url'])
        for entry in reversed(d.entries[:30]):
            link = entry.link if hasattr(entry, 'link') else ""
            if not link or link in existing_urls:
                continue
                
            title_en = html.unescape(entry.title) if hasattr(entry, 'title') else ""
            
            summary_en = ""
            if hasattr(entry, 'summary'):
                summary_en = entry.summary
            elif hasattr(entry, 'description'):
                summary_en = entry.description
            
            summary_en = clean_html(summary_en)
            if len(summary_en) > 400:
                summary_en = summary_en[:397] + "..."
                
            # STRICT FILTER
            if not is_kernel_related(title_en, summary_en, feed_info['name']):
                print(f"Ignorado (Não é sobre o kernel): {title_en}")
                continue
                
            date = ""
            if hasattr(entry, 'published'):
                date = entry.published
            elif hasattr(entry, 'updated'):
                date = entry.updated
                
            print(f"Translating: {title_en}")
            
            title_pt = translate_text(title_en)
            summary_pt = translate_text(summary_en)
            
            new_item = {
                "source": feed_info['name'],
                "title_en": title_en,
                "title_pt": title_pt,
                "summary_en": summary_en,
                "summary_pt": summary_pt,
                "link": link,
                "date": date
            }
            
            news_items.insert(0, new_item)
            existing_urls.add(link)
            new_additions += 1
            
    except Exception as e:
        print(f"Error fetching {feed_info['name']}: {e}")

if len(news_items) > 1000:
    news_items = news_items[:1000]

with open(news_db_path, "w", encoding="utf-8") as f:
    json.dump(news_items, f, ensure_ascii=False, indent=2)

print(f"Added {new_additions} new kernel articles. Total: {len(news_items)}")
