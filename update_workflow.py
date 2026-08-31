with open(".github/workflows/fetch-patches.yml", "r") as f:
    yaml = f.read()

# Replace the old python script inside the workflow
import re
new_script = """      - name: Fetch and translate news
        run: |
          pip install feedparser deep-translator beautifulsoup4
          python3 fetch_news.py

      - name: Commit and push"""

# I will just write a simpler approach: replace the run block of news fetch
yaml = re.sub(r'      - name: Fetch and translate news.*?      - name: Commit and push', new_script, yaml, flags=re.DOTALL)

with open(".github/workflows/fetch-patches.yml", "w") as f:
    f.write(yaml)
print("Updated workflow to just run fetch_news.py")
