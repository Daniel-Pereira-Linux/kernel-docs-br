#!/usr/bin/env python3
"""Fetch the current kernel.org releases index (mainline/stable/longterm/linux-next).

Writes kernel-releases.json. Never raises: on failure it leaves the existing
file untouched and exits 0 with a warning, so a transient kernel.org outage
never blocks the rest of the sync pipeline.
"""
import json
import sys
import time
import urllib.request

URL = "https://www.kernel.org/releases.json"
OUT = "kernel-releases.json"
TIMEOUT = 20
RETRIES = 3


def fetch():
	last_err = None
	for attempt in range(1, RETRIES + 1):
		try:
			req = urllib.request.Request(URL, headers={"User-Agent": "kernelbase-sync/1.0"})
			with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
				data = json.loads(resp.read().decode("utf-8"))
			if not data.get("releases"):
				raise ValueError("resposta sem 'releases'")
			return data
		except Exception as e:  # noqa: BLE001 - deliberately broad, this must never crash the job
			last_err = e
			print(f"[fetch_kernel_releases] tentativa {attempt}/{RETRIES} falhou: {e}")
			if attempt < RETRIES:
				time.sleep(3 * attempt)
	print(f"[fetch_kernel_releases] desistindo após {RETRIES} tentativas: {last_err}")
	return None


def main():
	data = fetch()
	if data is None:
		print("[fetch_kernel_releases] mantendo kernel-releases.json existente")
		return 0
	with open(OUT, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	print(f"[fetch_kernel_releases] ok: {len(data['releases'])} releases")
	return 0


if __name__ == "__main__":
	sys.exit(main())
