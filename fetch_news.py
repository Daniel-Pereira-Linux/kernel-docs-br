import urllib.request
import json
import re
import html
import os
import sys
import subprocess

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
    except:
        pass

existing_urls = set([item.get('link') for item in news_items])
new_additions = 0

for feed_info in FEEDS:
    print(f"Fetching {feed_info['name']}...")
    try:
        d = feedparser.parse(feed_info['url'])
        # Limit to 5 entries per source to avoid translating too much per run (since it's full text now)
        for entry in reversed(d.entries[:10]):
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
                # trafilatura is incredible at extracting article text
                downloaded = trafilatura.fetch_url(link)
                if downloaded:
                    full_text_en = trafilatura.extract(downloaded) or summary_clean
                else:
                    full_text_en = summary_clean
            except Exception as e:
                full_text_en = summary_clean
                
            if feed_info['name'] == 'LWN' and ("[$]" in title_en or "consider subscribing" in full_text_en):
                print(f"Skipping paid LWN article")
                continue
                
            title_pt = translate_long_text(title_en)
            summary_pt = translate_long_text(summary_clean)
            
            # Truncate full text to prevent massive translates in a single run (e.g. giant Planet Kernel posts)
            if len(full_text_en) > 10000:
                full_text_en = full_text_en[:10000] + "...\n[Post muito longo, leia na fonte]"
            
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
