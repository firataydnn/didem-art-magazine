#!/usr/bin/env python3
"""Collect RSS/Atom headlines into a non-publishing editorial inbox."""
import datetime as dt
import email.utils
import hashlib
import json
import os
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "editorial" / "radar" / "sources.json"
OUT = ROOT / "editorial" / "radar" / "inbox.json"
AGENT = "DidemArtEditorialRadar/1.0 (+https://github.com/firataydnn/didem-art-magazine)"
NS = {"a": "http://www.w3.org/2005/Atom"}

def clean(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]*>", " ", value or ""))).strip()

def parse_date(value):
    if not value:
        return ""
    try:
        return email.utils.parsedate_to_datetime(value).astimezone(dt.timezone.utc).isoformat()
    except (TypeError, ValueError):
        try:
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
        except ValueError:
            return ""

def entries(payload):
    root = ET.fromstring(payload)
    for item in root.findall(".//channel/item"):
        yield {"title": clean(item.findtext("title")), "url": (item.findtext("link") or "").strip(),
               "published": parse_date(item.findtext("pubDate")), "summary": clean(item.findtext("description"))[:500]}
    for item in root.findall("a:entry", NS):
        links = item.findall("a:link", NS)
        link = next((x.attrib.get("href", "") for x in links if x.attrib.get("rel", "alternate") == "alternate"), "")
        link = link or next((x.attrib.get("href", "") for x in links), "")
        yield {"title": clean(item.findtext("a:title", "", NS)), "url": link,
               "published": parse_date(item.findtext("a:published", "", NS) or item.findtext("a:updated", "", NS)),
               "summary": clean(item.findtext("a:summary", "", NS))[:500]}

def main():
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"items": []}
    records = {x["id"]: x for x in old.get("items", [])}
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    errors = []
    for source in sources:
        try:
            req = urllib.request.Request(source["feed"], headers={"User-Agent": AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
            with urllib.request.urlopen(req, timeout=18) as response:
                payload = response.read(2_000_001)
            if len(payload) > 2_000_000:
                raise ValueError("Feed exceeds 2 MB limit")
            count = 0
            for item in entries(payload):
                if not item["url"].startswith(("https://", "http://")) or not item["title"]:
                    continue
                key = hashlib.sha256(item["url"].split("#")[0].rstrip("/").encode()).hexdigest()[:20]
                if key in records:
                    continue
                records[key] = {"id": key, "source": source["name"], "category": source["category"],
                                **item, "discovered": now, "status": "new", "image_status": "rights_pending",
                                "publication_approved": False}
                count += 1
                if count >= 80:
                    break
        except Exception as exc:
            errors.append({"source": source["name"], "error": str(exc)[:200]})
    ordered = sorted(records.values(), key=lambda x: x["discovered"], reverse=True)[:3000]
    # Avoid modifying the tracked file on every run when there are no new records.
    output = {"schema": 1, "items": ordered}
    if output != {"schema": old.get("schema", 1), "items": old.get("items", [])}:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": len(ordered), "new": len(records)-len(old.get("items", [])), "errors": errors}, ensure_ascii=False))
    if errors:
        print("Feed failures are nonfatal; check individual source URLs.")

if __name__ == "__main__":
    main()
