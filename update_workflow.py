with open(".github/workflows/fetch-patches.yml", "r") as f:
    yaml = f.read()

yaml = yaml.replace("pip install feedparser deep-translator beautifulsoup4 trafilatura --break-system-packages", "python3 -m venv venv && ./venv/bin/pip install feedparser deep-translator beautifulsoup4 trafilatura")
yaml = yaml.replace("python3 fetch_news.py", "./venv/bin/python fetch_news.py")

with open(".github/workflows/fetch-patches.yml", "w") as f:
    f.write(yaml)
