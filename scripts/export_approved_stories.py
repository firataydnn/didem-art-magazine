#!/usr/bin/env python3
"""Export only explicitly approved, image-cleared newspaper stories as JSON."""
import json, pathlib, sqlite3, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def export(db_path,out_path):
    conn=sqlite3.connect(db_path)
    conn.row_factory=sqlite3.Row
    rows=conn.execute("""SELECT s.id,s.title,s.slug,s.body,s.category,s.published_at,s.approved_at,
    a.source_url AS image,a.credit AS image_credit,a.alt AS image_alt
    FROM stories s JOIN assets a ON a.story_id=s.id
    WHERE s.status IN ('approved','published') AND s.approved_at IS NOT NULL
    AND a.rights_status='verified' AND length(trim(coalesce(a.license,'')))>0
    AND length(trim(coalesce(a.credit,'')))>0 AND length(trim(coalesce(s.body,'')))>=500
    AND s.slug IS NOT NULL AND length(trim(coalesce(a.source_url,'')))>0
    GROUP BY s.id ORDER BY coalesce(s.published_at,s.approved_at) DESC""").fetchall()
    stories=[dict(row) for row in rows]
    output=pathlib.Path(out_path);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({"schema":1,"count":len(stories),"stories":stories},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Approved stories exported:",len(stories))
if __name__=="__main__":export(sys.argv[1],sys.argv[2])
