#!/usr/bin/env python3
"""Download curated, rights-checked artwork reproductions to local GitHub Pages assets.
Never downloads press-room photographs or unlicensed event images.
Only a positive Commons license result permits download (PD/CC0, or curated CC BY with credits).
"""
from __future__ import annotations
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "editorial" / "art-image-manifest.json"
INDEX = ROOT / "index.html"
OUT = ROOT / "assets" / "images"
UA = "AtelierArtEditorial/1.0 (https://github.com/firataydnn/didem-art-magazine; educational editorial reuse)"
API = "https://commons.wikimedia.org/w/api.php"
ALLOWED = {"public domain", "cc0", "cc0 1.0", "cc zero", "cc-zero"}
CC_ALLOWED = {"cc by 4.0", "cc by-sa 4.0"}

def request(url: str, max_size=10_000_000) -> bytes:
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "application/json,image/jpeg,image/webp,*/*"
            })
            with urllib.request.urlopen(req, timeout=35) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > max_size:
                    raise ValueError("Image exceeds download size limit")
                content = response.read(max_size + 1)
                if len(content) > max_size:
                    raise ValueError("Image exceeds download size limit")
                return content
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = exc
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"Unable to retrieve {url}: {last}")

def get_image_info(filename: str) -> dict:
    query = urllib.parse.urlencode({
        "action": "query", "format": "json", "formatversion": "2",
        "titles": "File:" + filename, "prop": "imageinfo",
        "iiprop": "url|size|extmetadata", "iiurlwidth": "1280"
    })
    data = json.loads(request(API + "?" + query, max_size=2_000_000))
    pages = data["query"]["pages"]
    if len(pages) != 1 or "missing" in pages[0]:
        raise ValueError("Commons file does not exist")
    return pages[0]["imageinfo"][0]

def approved_license(info: dict, rec: dict) -> tuple[bool, str, str]:
    meta = info.get("extmetadata") or {}
    name = html.unescape(re.sub(r"<[^>]*>", "", meta.get("LicenseShortName", {}).get("value", ""))).strip()
    license_url = meta.get("LicenseUrl", {}).get("value", "")
    if name.lower() in ALLOWED:
        return True, name, license_url
    if (name.lower() in CC_ALLOWED and rec.get("allow_cc") is True
            and rec.get("photographer") and license_url):
        return True, name, license_url
    return False, name, license_url

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads(MANIFEST.read_text(encoding="utf-8"))["items"]
    source = INDEX.read_text(encoding="utf-8")
    m = re.search(r"const data=(\[.*?\]);let cat=", source, re.DOTALL)
    if not m:
        raise RuntimeError("Article data block not found; refusing to change site")
    articles = json.loads(m.group(1))
    success = {}
    failures = []
    for rec in records:
        idx = rec["index"]
        if not (0 <= idx < len(articles)):
            failures.append([rec["slug"], "Invalid article index"])
            continue
        target = OUT / (rec["slug"] + ".jpg")
        try:
            info = get_image_info(rec["file"])
            allowed, license_name, license_url = approved_license(info, rec)
            if not allowed:
                raise ValueError(f"License not approved for automatic reuse: {license_name}")
            image_url = info.get("thumburl") or info.get("url")
            if not image_url:
                raise ValueError("Commons API returned no image URL")
            if not target.is_file() or target.stat().st_size < 1000:
                data = request(image_url)
                if not data.startswith(b"\xff\xd8\xff"):
                    raise ValueError("Download is not a JPEG")
                target.write_bytes(data)
            source_page = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(rec["file"].replace(" ", "_"))
            caption = (f'Fotoğraf: {rec["photographer"]}. {rec["work"]}. Kaynak: Wikimedia Commons. Lisans: {license_name}.'
                       if rec.get("photographer") else
                       f'{rec["artist"]}, {rec["work"]}. Kaynak: Wikimedia Commons. Lisans: {license_name}.')
            if rec.get("note"):
                caption += " " + rec["note"]
            articles[idx]["img"] = "assets/images/" + target.name
            articles[idx]["imageCredit"] = caption
            articles[idx]["imageSource"] = source_page
            articles[idx]["imageLicense"] = license_name
            articles[idx]["imageLicenseUrl"] = license_url
            articles[idx]["imageKind"] = "archive_venue" if rec.get("photographer") else "artwork"
            success[rec["slug"]] = {
                "articleIndex": idx, "localPath": "assets/images/" + target.name,
                "sourceFile": rec["file"], "sourcePage": source_page,
                "license": license_name, "licenseUrl": license_url, "credit": caption, "bytes": target.stat().st_size
            }
            print(f"OK {idx}: {target.name} ({target.stat().st_size} bytes) — {license_name}")
        except Exception as exc:
            failures.append([rec["slug"], str(exc)])
            print(f"SKIP {idx}: {rec['slug']}: {exc}", file=sys.stderr)
            # Do not keep known-broken external hotlinks on failed downloads.
            if articles[idx].get("img", "").startswith("http") and articles[idx].get("fallbackImg"):
                articles[idx]["img"] = articles[idx]["fallbackImg"]
                articles[idx]["imageCredit"] = "Geçici editoryal grafik; gerçek eser görseli henüz indirilemedi."
    # If another run already downloaded a valid local file, retain it.
    if success:
        updated = json.dumps(articles, ensure_ascii=False, separators=(",", ":"))
        source = source[:m.start(1)] + updated + source[m.end(1):]
        INDEX.write_text(source, encoding="utf-8")
    (OUT / "credits.json").write_text(
        json.dumps({"source": "Wikimedia Commons; license checked per file", "downloaded": success,
                    "failures": failures}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"RESULT: {len(success)} downloaded or verified; {len(failures)} skipped")
    # Exit nonzero only if none succeeded: make failure visible in Actions.
    return 0 if success else 2

if __name__ == "__main__":
    raise SystemExit(main())
