#!/usr/bin/env python3
"""ATELIER KULİS source radar. Links for editors only; never auto-approves rumors."""
import datetime as dt
import json
import pathlib
import re
from urllib.parse import urlparse

ROOT=pathlib.Path(__file__).resolve().parents[1]
FEED=ROOT/"data"/"world-art-radar.json"
OUT=ROOT/"data"/"kulis-leads.json"

RULES=[
 ("KOLEKSİYONERLER",("collector","collectors","collection","kardashian","celebrity","koons","di caprio","di caprio","mugrabi","nahmad","billionaire")),
 ("MÜZAYEDE MASASI",("auction","sotheby","christie","hammer","sold for","estimated","record price","monet","painting sold","estimate","resale","price drop")),
 ("GALERİ KULİSİ",("gallery","galleries","dealer","dealers","roster","represents","representation","director","leadership","ceo","closes","closing","shutters","resigns","restructure")),
 ("FUAR KORİDORU",("art basel","frieze","fair","fairs","booth","pavilion","refund","compensat","cancelled","closing early")),
 ("SANAT & GÜÇ",("market","donation","funding","lawsuit","settlement","legal battle","leadership","controversy","museum board","institutional","deal","residency")),
]
SKIP=("murder","killed","dead body","sexual assault","rape","suicide","domestic","police charge","must-see","destinations","gallery guide","things to see","shows to see","exhibition to open","seven shows","weekly roundup")
PREFER=("art basel","sotheby","christie","gallery","kardashian","collector","auction","gagosian","frieze","koons")
def route(title):
 t=title.casefold()
 if any(word in t for word in SKIP):return None
 if "national gallery" in t and not any(w in t for w in ("director","resign","auction","sale","funding","lawsuit")):return None
 for category,words in RULES:
  if any(word in t for word in words):return category
 return None

def main():
 now=dt.datetime.now(dt.timezone.utc)
 raw=json.loads(FEED.read_text(encoding="utf-8"))
 picks=[];seen=set()
 for lead in raw.get("items",[]):
  title=lead.get("title");url=lead.get("url");source=lead.get("source");published=lead.get("published_at")
  if not all(isinstance(x,str) for x in (title,url,source,published)):continue
  try:
   parsed=urlparse(url)
   published_dt=dt.datetime.fromisoformat(published.replace("Z","+00:00"))
  except ValueError:continue
  if parsed.scheme!="https" or not parsed.netloc or not parsed.hostname:continue
  if not published_dt.tzinfo:continue
  if published_dt>now+dt.timedelta(hours=2) or published_dt<now-dt.timedelta(days=7):continue
  if url in seen:continue
  category=route(title)
  if category is None:continue
  seen.add(url)
  t=title.casefold()
  importance=(3 if any(w in t for w in PREFER) else 0)+(2 if source in ("Artnet","ARTnews","The Art Newspaper") else 0)
  importance+=max(0,7-int((now-published_dt).total_seconds()/86400))
  picks.append({"title":title[:220],"url":url,"source":source,"published_at":published,
   "category":category,"priority":importance,"editorial_status":"source_link_requires_review",
   "source_verified":False,"article_approved":False,"image_rights":"not_cleared",
   "note":"Publisher headline only. Not an independently checked art gossip report."})
 picks.sort(key=lambda x:(x["priority"],x["published_at"]),reverse=True)
 data={"schema":1,"generated_at":now.isoformat(),"source_generated_at":raw.get("generated_at"),
  "notice":"Kulis aday bağlantıları. Metin, iddia, alıntı ve fotoğraf henüz ATELIER tarafından doğrulanmadı. Otomatik haber yayınlamaz.",
  "items":picks[:36]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"input":len(raw.get("items",[])),"kulis_candidates":len(data["items"])},ensure_ascii=False))
if __name__=="__main__":main()
