#!/usr/bin/env python3
"""Build a local SQLite editorial data warehouse from tracked RSS data.
Never publishes content. Database output is a GitHub Actions artifact only."""
import json
import pathlib
import sqlite3
import sys
from urllib.parse import urlsplit
ROOT=pathlib.Path(__file__).resolve().parents[1]
def build(target):
    target=pathlib.Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript((ROOT/"database/schema.sql").read_text(encoding="utf-8"))
    sources=json.loads((ROOT/"editorial/radar/sources.json").read_text(encoding="utf-8"))
    for source in sources:
        conn.execute("INSERT INTO sources(id,name,category,feed_url) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,category=excluded.category,feed_url=excluded.feed_url",(source["name"],source["name"],source.get("category"),source.get("feed")))
    rows=json.loads((ROOT/"editorial/radar/triage.json").read_text(encoding="utf-8")).get("items",[])
    for item in rows:
        if not item.get("id") or not item.get("url","").startswith(("https://","http://")): continue
        conn.execute("""INSERT INTO intake(id,source_id,title,url,published_at,priority,possible_duplicate_of)
        VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET priority=excluded.priority,possible_duplicate_of=excluded.possible_duplicate_of""",
        (item["id"],item.get("source") if any(s["name"]==item.get("source") for s in sources) else None,item.get("title",""),item["url"],item.get("published"),item.get("priority_score",0),item.get("possible_duplicate_of")))
    conn.commit()
    print(json.dumps({"sources":conn.execute("SELECT count(*) FROM sources").fetchone()[0],"intake":conn.execute("SELECT count(*) FROM intake").fetchone()[0],"approved_stories":conn.execute("SELECT count(*) FROM stories WHERE status IN ('approved','published')").fetchone()[0]}))
    conn.close()
if __name__=="__main__":build(sys.argv[1] if len(sys.argv)>1 else "/tmp/didem-art-editorial.sqlite")
