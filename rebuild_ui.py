import re

with open("index.html", "r") as f:
    html = f.read()

docs_match = re.search(r'id="docs-markdown-content">(.*?)</div>\s*<div class="mt-12">', html, re.DOTALL)
if not docs_match:
    docs_match = re.search(r'id="docs" class="tab-content.*?>(.*?)<style>', html, re.DOTALL)
# It's injected from how-to.md, I will just read how-to.md directly and convert it using the standard approach, or keep a placeholder.
docs_content = "<!-- DOCS_PLACEHOLDER -->"

with open("new_layout.html", "r") as f:
    pass # I'll just write it as a normal string and replace.
