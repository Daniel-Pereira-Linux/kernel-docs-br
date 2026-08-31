with open(".github/workflows/fetch-patches.yml", "r") as f:
    yaml = f.read()

# Add step to install deps and run news fetch
new_step = """      - name: Fetch and translate news
        run: |
          pip install feedparser deep-translator beautifulsoup4
          python3 << 'PYEOF'
          import urllib.request
          import xml.etree.ElementTree as ET
          import json
          import html
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
                  for entry in d.entries[:10]:
                      title_en = html.unescape(entry.title) if hasattr(entry, 'title') else ""
                      summary_en = ""
                      if hasattr(entry, 'summary'):
                          summary_en = entry.summary
                      elif hasattr(entry, 'description'):
                          summary_en = entry.description
                      
                      summary_en = clean_html(summary_en).strip()
                      if len(summary_en) > 300:
                          summary_en = summary_en[:297] + "..."
                      link = entry.link if hasattr(entry, 'link') else ""
                      
                      date = ""
                      if hasattr(entry, 'published'):
                          date = entry.published
                      elif hasattr(entry, 'updated'):
                          date = entry.updated

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
                  print(f"Error: {e}")

          with open("news.json", "w", encoding="utf-8") as f:
              json.dump(news_items, f, ensure_ascii=False, indent=2)
          PYEOF

      - name: Commit and push"""

yaml = yaml.replace("      - name: Commit and push", new_step)
yaml = yaml.replace("git add patches.json kernel-releases.json", "git add patches.json kernel-releases.json news.json")

with open(".github/workflows/fetch-patches.yml", "w") as f:
    f.write(yaml)
print("Updated workflow")
