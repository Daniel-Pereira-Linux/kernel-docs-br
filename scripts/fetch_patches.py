#!/usr/bin/env python3
"""Fetch recent linux-doc pt_BR patch/thread activity from lore.kernel.org.

Writes patches.json. Never raises: on failure it leaves the existing file
untouched and exits 0 with a warning, so a lore.kernel.org hiccup never
blocks kernel-releases.json / news.json from being committed.
"""
import html
import json
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

URL = "https://lore.kernel.org/linux-doc/?q=pt_BR&x=A"
OUT = "patches.json"
TIMEOUT = 30
RETRIES = 4

NS = {
	"atom": "http://www.w3.org/2005/Atom",
	"thr": "http://purl.org/syndication/thread/1.0",
}


def fetch_raw():
	last_err = None
	for attempt in range(1, RETRIES + 1):
		try:
			req = urllib.request.Request(
				URL,
				headers={
					"User-Agent": "kernelbase-sync/1.0 (+https://kernelbase.com.br; contato: danielmaraboo@gmail.com)",
					"Accept": "application/atom+xml, application/xml;q=0.9, */*;q=0.8",
				},
			)
			with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
				return resp.read()
		except (urllib.error.URLError, TimeoutError, OSError) as e:
			last_err = e
			print(f"[fetch_patches] tentativa {attempt}/{RETRIES} falhou: {e}")
			if attempt < RETRIES:
				time.sleep(5 * attempt)
	print(f"[fetch_patches] desistindo após {RETRIES} tentativas: {last_err}")
	return None


def parse_entries(raw_bytes):
	data = raw_bytes.decode("utf-8", errors="replace")
	root = ET.fromstring(data)
	entries = []
	for entry in root.findall("atom:entry", NS):
		title_el = entry.find("atom:title", NS)
		author_el = entry.find("atom:author/atom:name", NS)
		email_el = entry.find("atom:author/atom:email", NS)
		updated_el = entry.find("atom:updated", NS)
		link_el = entry.find("atom:link", NS)
		content_el = entry.find("atom:content", NS)

		content_text = ""
		if content_el is not None:
			content_text = ET.tostring(content_el, encoding="unicode", method="text")
			content_text = html.unescape(content_text).strip()

		entries.append({
			"title": title_el.text if title_el is not None else "",
			"author": author_el.text if author_el is not None else "",
			"email": email_el.text if email_el is not None else "",
			"updated": updated_el.text if updated_el is not None else "",
			"link": link_el.get("href", "") if link_el is not None else "",
			"content": content_text,
		})
	return entries


def main():
	raw = fetch_raw()
	if raw is None:
		print("[fetch_patches] mantendo patches.json existente")
		return 0

	try:
		entries = parse_entries(raw)
	except ET.ParseError as e:
		print(f"[fetch_patches] resposta não é um XML/Atom válido, mantendo patches.json existente: {e}")
		return 0

	if not entries:
		print("[fetch_patches] feed retornou 0 entradas, mantendo patches.json existente (evita sobrescrever com vazio)")
		return 0

	with open(OUT, "w", encoding="utf-8") as f:
		json.dump(entries, f, ensure_ascii=False, indent=2)
	print(f"[fetch_patches] ok: {len(entries)} entradas")
	return 0


if __name__ == "__main__":
	sys.exit(main())
