#!/usr/bin/env python3
"""Editorial triage of the non-publication RSS inbox. No external dependencies."""
import collections
import datetime as dt
import json
import pathlib
import re
import unicodedata
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
INBOX = ROOT / "editorial/radar/inbox.json"
REPORT = ROOT / "editorial/radar/triage.json"
STOP = {"the","a","an","and","in","of","at","for","to","with","on","art","artist","new","from","is","are","by","as","this","that","how","why","its","after","over"}
HIGH = {"acquisition": 4, "acquires": 4, "museum": 2, "biennale": 3, "biennial": 3, "award": 3, "wins": 3, "auction": 3, "exhibition": 2, "opens": 2, "frieze": 2, "basel": 2, "istanbul": 3, "turkey": 3, "türkiye": 3, "record": 2}

def canonical(url):
    try:
        p = urlsplit(url)
        q = [(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith("utm_") and k.lower() not in ("fbclid","gclid")]
        return urlunsplit((p.scheme.lower(),p.netloc.lower().removeprefix("www."),p.path.rstrip("/"),urlencode(q),""))
    except ValueError:
        return url

def tokens(title):
    plain = unicodedata.normalize("NFKC", title.lower())
    return {t for t in re.findall(r"[^\W_]+", plain) if len(t)>3 and t not in STOP}

def score(item, now):
    words = tokens(item.get("title",""))
    value = min(12, sum(v for k,v in HIGH.items() if k in words))
    published = item.get("published") or ""
    try:
        days = max(0, (now-dt.datetime.fromisoformat(published.replace("Z","+00:00"))).total_seconds()/86400)
        value += 6 if days<=1 else 4 if days<=3 else 2 if days<=7 else 0
    except (ValueError, TypeError):
        pass
    if item.get("source"): value += 1
    return value

def main():
    data = json.loads(INBOX.read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc)
    seen_urls = set()
    clusters = []
    output = []
    for item in sorted(data.get("items",[]),key=lambda x:(x.get("published") or "",x.get("discovered") or ""),reverse=True):
        url = canonical(item.get("url",""))
        words = tokens(item.get("title",""))
        duplicate_of = None
        if url in seen_urls:
            duplicate_of = "same_url"
        elif len(words)>=4:
            for representative in clusters:
                overlap = len(words & representative["words"])/len(words | representative["words"])
                if overlap >= .78:
                    duplicate_of = representative["id"]
                    break
        if not duplicate_of:
            seen_urls.add(url)
            if words: clusters.append({"id":item["id"],"words":words})
        output.append({"id":item["id"],"title":item.get("title",""),"url":item.get("url",""),
                       "source":item.get("source",""),"published":item.get("published",""),
                       "priority_score":score(item,now),"possible_duplicate_of":duplicate_of,
                       "editorial_status":"needs_human_review","image_rights":"unverified",
                       "publication_approved":False})
    output.sort(key=lambda x:(x["possible_duplicate_of"] is not None,-x["priority_score"],x["title"]))
    report={"schema":1,"count":len(output),"possible_duplicates":sum(bool(x["possible_duplicate_of"]) for x in output),"items":output}
    if not REPORT.exists() or json.loads(REPORT.read_text(encoding="utf-8")) != report:
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Triage: {len(output)} records; {report['possible_duplicates']} potential duplicates; 0 automatically approved")

if __name__ == "__main__": main()
