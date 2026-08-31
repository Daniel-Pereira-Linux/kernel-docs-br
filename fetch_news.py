import urllib.request
import json
import re
import html
import os
import sys
import subprocess
import time

def install_deps():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator", "feedparser", "beautifulsoup4", "trafilatura"])

try:
    from deep_translator import GoogleTranslator
    import feedparser
    from bs4 import BeautifulSoup
    import trafilatura
except ImportError:
    install_deps()
    from deep_translator import GoogleTranslator
    import feedparser
    from bs4 import BeautifulSoup
    import trafilatura

def clean_html(raw_html):
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=' ').strip()

def translate_long_text(text):
    if not text:
        return ""
    try:
        translator = GoogleTranslator(source='auto', target='pt')
        paragraphs = text.split('\n')
        translated_paragraphs = []
        chunk = ""
        for p in paragraphs:
            if not p.strip():
                continue
            if len(chunk) + len(p) < 2000:
                chunk += p + "\n"
            else:
                if chunk.strip():
                    translated_paragraphs.append(translator.translate(chunk))
                    time.sleep(1)
                chunk = p + "\n"
        if chunk.strip():
            translated_paragraphs.append(translator.translate(chunk))
            time.sleep(1)
            
        translated = "\n".join(translated_paragraphs)
        if "Error 500 (Server Error)" in translated:
            return text 
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

KERNEL_KEYWORDS = [
    "kernel", "linus torvalds", "torvalds", "merge window", "mainline",
    "linux 7.", "linux 6.", "linux 5.", "kbuild", "kconfig", "kvm", "ebpf",
    "bpf", "vfs", "cgroup", "scheduler", "drm subsystem", "linux patches",
    "lore.kernel.org"
]

def is_kernel_related(title, summary, source):
    if source.lower() == "kernel.org":
        return True
    text = (title + " " + summary).lower()
    for kw in KERNEL_KEYWORDS:
        if kw in text:
            return True
    if re.search(r'\brc[1-9]\b', text):
        return True
    return False

# Phoronix only as requested!
FEEDS = [
    {"name": "Phoronix", "url": "https://www.phoronix.com/rss.php"},
]

news_db_path = "news.json"
news_items = []
if os.path.exists(news_db_path):
    try:
        with open(news_db_path, "r", encoding="utf-8") as f:
            news_items = json.load(f)
    except:
        pass

# Filter out old items from LWN/Planet/Kernel.org AND anything with Error 500
news_items = [item for item in news_items if item.get('source', '').lower() == 'phoronix' and "Error 500" not in (item.get('content_pt', '') or '') and "Error 500" not in (item.get('summary_pt', '') or '')]

existing_urls = set([item.get('link') for item in news_items])
new_additions = 0

for feed_info in FEEDS:
    print(f"Fetching {feed_info['name']}...")
    try:
        d = feedparser.parse(feed_info['url'])
        # Increase limit since we only have one feed now
        for entry in reversed(d.entries[:15]):
            link = entry.link if hasattr(entry, 'link') else ""
            if not link or link in existing_urls:
                continue
                
            title_en = html.unescape(entry.title) if hasattr(entry, 'title') else ""
            
            summary_en = ""
            if hasattr(entry, 'summary'):
                summary_en = entry.summary
            elif hasattr(entry, 'description'):
                summary_en = entry.description
            
            summary_clean = clean_html(summary_en)
            if len(summary_clean) > 400:
                summary_clean = summary_clean[:397] + "..."
                
            if not is_kernel_related(title_en, summary_clean, feed_info['name']):
                continue
                
            date = getattr(entry, 'published', getattr(entry, 'updated', ""))
            
            print(f"Fetching full text for: {title_en}")
            full_text_en = ""
            try:
                downloaded = trafilatura.fetch_url(link)
                if downloaded:
                    full_text_en = trafilatura.extract(downloaded) or summary_clean
                else:
                    full_text_en = summary_clean
            except Exception as e:
                full_text_en = summary_clean
                
            title_pt = translate_long_text(title_en)
            summary_pt = translate_long_text(summary_clean)
            
            if len(full_text_en) > 10000:
                full_text_en = full_text_en[:10000] + "...\n[Restante do artigo muito longo]"
            
            full_text_pt = translate_long_text(full_text_en)
            
            new_item = {
                "source": feed_info['name'],
                "title_en": title_en,
                "title_pt": title_pt,
                "summary_en": summary_clean,
                "summary_pt": summary_pt,
                "content_en": full_text_en,
                "content_pt": full_text_pt,
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
