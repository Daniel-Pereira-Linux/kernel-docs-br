#!/usr/bin/env python3
"""Fetch and translate recent Linux/kernel news from a set of RSS feeds.

Appends new items to news.json (deduped by link, capped at 1000 items).
Each feed and each translation call is isolated in its own try/except so a
single broken feed or a translation-API hiccup never loses the items that
did succeed, and never crashes the whole script.
"""
import html
import json
import os
import socket
import sys
import time

socket.setdefaulttimeout(20)

try:
	from deep_translator import GoogleTranslator
	import feedparser
	from bs4 import BeautifulSoup
except ImportError:
	import subprocess
	subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "deep-translator", "feedparser", "beautifulsoup4"])
	from deep_translator import GoogleTranslator
	import feedparser
	from bs4 import BeautifulSoup

FEEDS = [
	{"name": "Phoronix", "url": "https://www.phoronix.com/rss.php"},
	{"name": "LWN", "url": "https://lwn.net/headlines/newrss"},
	{"name": "Planet Kernel", "url": "https://planet.kernel.org/rss20.xml"},
	{"name": "Kernel.org", "url": "https://www.kernel.org/feeds/kdist.xml"},
	{"name": "9to5Linux", "url": "https://9to5linux.com/feed"},
	# Linux.com foi descontinuado e seu feed hoje devolve páginas de erro
	# genéricas (ex: "Error 500 ... That's an error.") em vez de notícias.
]

# Heurística de segurança: se qualquer feed (atual ou futuro) começar a
# devolver uma página de erro genérica em vez de conteúdo, não publicamos.
ERROR_PAGE_MARKERS = ("that's an error", "error 500", "404 not found", "access denied")


def looks_like_error_page(title, summary):
	blob = f"{title} {summary}".lower()
	return any(marker in blob for marker in ERROR_PAGE_MARKERS)

NEWS_DB = "news.json"
MAX_ITEMS = 1000
SUMMARY_MAX_CHARS = 400
TRANSLATE_MAX_CHARS = 3000


def clean_html(raw_html):
	if not raw_html:
		return ""
	try:
		return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
	except Exception as e:
		print(f"[fetch_news] falha ao limpar HTML: {e}")
		return raw_html


def translate_text(text):
	if not text:
		return ""
	if len(text) > TRANSLATE_MAX_CHARS:
		text = text[:TRANSLATE_MAX_CHARS] + "..."

	for attempt in range(1, 3):
		try:
			result = GoogleTranslator(source="auto", target="pt").translate(text)
			# O endpoint não-oficial do Google Translate às vezes devolve uma
			# página de erro HTML/rate-limit em vez de lançar uma exceção.
			if result and not looks_like_error_page(result, ""):
				return result
			print(f"[fetch_news] tradução parece página de erro (tentativa {attempt}/2)")
		except Exception as e:
			print(f"[fetch_news] erro de tradução (tentativa {attempt}/2): {e}")
		time.sleep(1.5 * attempt)

	print("[fetch_news] desistindo da tradução, mantendo texto original")
	return text


def load_existing():
	if not os.path.exists(NEWS_DB):
		return []
	try:
		with open(NEWS_DB, "r", encoding="utf-8") as f:
			return json.load(f)
	except Exception as e:
		print(f"[fetch_news] não consegui ler news.json existente, começando do zero: {e}")
		return []


def main():
	news_items = load_existing()
	existing_urls = {item.get("link") for item in news_items}
	new_additions = 0

	for feed_info in FEEDS:
		print(f"[fetch_news] buscando {feed_info['name']}...")
		try:
			d = feedparser.parse(feed_info["url"])
			if getattr(d, "bozo", 0) and not getattr(d, "entries", None):
				print(f"[fetch_news] {feed_info['name']}: feed inválido/vazio, pulando")
				continue

			for entry in reversed(d.entries[:20]):
				link = getattr(entry, "link", "")
				if not link or link in existing_urls:
					continue

				title_en = html.unescape(getattr(entry, "title", ""))
				summary_en = getattr(entry, "summary", "") or getattr(entry, "description", "")
				summary_en = clean_html(summary_en)
				if len(summary_en) > SUMMARY_MAX_CHARS:
					summary_en = summary_en[: SUMMARY_MAX_CHARS - 3] + "..."

				date = getattr(entry, "published", "") or getattr(entry, "updated", "")

				if looks_like_error_page(title_en, summary_en):
					print(f"[fetch_news] {feed_info['name']}: item parece página de erro, ignorando: {title_en[:80]!r}")
					continue

				title_pt = translate_text(title_en)
				time.sleep(0.4)
				summary_pt = translate_text(summary_en)
				time.sleep(0.4)

				news_items.insert(0, {
					"source": feed_info["name"],
					"title_en": title_en,
					"title_pt": title_pt,
					"summary_en": summary_en,
					"summary_pt": summary_pt,
					"link": link,
					"date": date,
				})
				existing_urls.add(link)
				new_additions += 1
		except Exception as e:
			print(f"[fetch_news] erro buscando {feed_info['name']} (pulando esta fonte): {e}")

	if len(news_items) > MAX_ITEMS:
		news_items = news_items[:MAX_ITEMS]

	with open(NEWS_DB, "w", encoding="utf-8") as f:
		json.dump(news_items, f, ensure_ascii=False, indent=2)

	print(f"[fetch_news] {new_additions} novas notícias adicionadas. Total: {len(news_items)}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
