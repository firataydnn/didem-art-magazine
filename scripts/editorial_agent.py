#!/usr/bin/env python3
"""Editorial radar triage. AI drafts are NOT publication approvals or rights clearances."""
import datetime as dt
import json, os, pathlib, re, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
FEED=ROOT/"data/world-art-radar.json"
OUT=ROOT/"data/editorial-digest.json"
STOP=set("the and for with from that this into are was have will new art arts artist artists gallery galleries museum museums exhibition exhibitions of in to on at a an by as".split())
CATS=[
 ("TÜRKİYE",("turkey","turkish","istanbul","ankara","izmir","türkiye")),
 ("SANATÇILAR",("photographer","artist","painter","sculptor","obituary","dies","dead at")),
 ("TARTIŞMALAR",("protest","lawsuit","restitution","censor","strike","ballot","looted","stolen","unions","cuts","funding crisis")),
 ("PİYASA",("auction","sotheby","christie","sale","sold","record price","art market","jewelry","fair")),
 ("KOLEKSİYON",("acquisition","donation","collection","bequest","gift","holdings")),
 ("SERGİLER",("exhibition","retrospective","biennial","triennial","pavilion","sculpture garden","sculpture show")),
 ("KURUMLAR",("museum","moma","pompidou","louvre","documenta","guggenheim","gallery director","curator","cultural alliance")),
]
HIGH=("moma","pompidou","tate","louvre","met museum","guggenheim","documenta","venice biennale","art basel","national gallery")
IMPACT=("alliance","acquires","acquisition","donation","restitution","curator","director","grant","lawsuit","agreement","strike")
LOW=("sponsored","offers a","advertisement","must-see","things to do","own a piece","round up","podcast","halloween","guide","best of")
def tokens(s):
 words=[]
 for t in re.findall(r"[a-z0-9]{3,}",s.lower()):
  if t in STOP:continue
  if t.startswith("curator"):t="curator"
  if t.startswith("sculptur"):t="sculpture"
  if t.startswith("redesign"):t="redesign"
  words.append(t)
 return set(words)
def classify(title,default):
 s=title.lower()
 return next((c for c,terms in CATS if any(x in s for x in terms)),default if default!="DÜNYA" else "DÜNYA")
def rank(x,now):
 title=x["title"].lower()
 pub=dt.datetime.fromisoformat(x["published_at"].replace("Z","+00:00"))
 pts=max(0,round(12-max(0,(now-pub).total_seconds()/3600)/6))
 reasons=[]
 if any(x in title for x in HIGH):pts+=7;reasons.append("major_institution")
 if any(x in title for x in IMPACT):pts+=5;reasons.append("sector_change")
 if any(x in title for x in ("auction","sotheby","christie","million","art market")):pts+=4;reasons.append("market")
 if any(x in title for x in LOW):pts-=7;reasons.append("non_breaking_format")
 if x["source"] in ("The Art Newspaper","ARTnews","Artforum"):pts+=2
 return pts,reasons
def event_class(title):
 t=title.lower()
 groups=[
  ("garden",("sculpture garden","sculpture park")),
  ("alliance",("alliance","partnership","residency","collaboration")),
  ("staff",("curator","curatorial","director","appointed","team members","joins","leadership")),
  ("death",("dead","dies","murder","killed","obituary")),
  ("exhibition",("exhibition","retrospective","art show")),
  ("labour",("unions","strike","workers agreement")),
 ]
 return next((c for c,words in groups if any(w in t for w in words)),None)
def near_duplicate(a,b):
 da=dt.datetime.fromisoformat(a["published_at"]);db=dt.datetime.fromisoformat(b["published_at"])
 if abs((da-db).total_seconds())>72*3600:return False
 ca,cb=event_class(a["title"]),event_class(b["title"])
 if ca and cb and ca!=cb:return False
 aa,bb=tokens(a["title"]),tokens(b["title"])
 return bool(aa and bb and len(aa&bb)>=3 and len(aa&bb)/len(aa|bb)>=0.28)
def ai_review(item,key):
 meta={k:item.get(k) for k in ("title","source","published_at","url")}
 prompt=("You are a conservative Turkish art journalism research assistant. Using ONLY the headline "
 "and metadata below, return a JSON object with headline_tr, summary_tr (one short sentence "
 "attributed to the source, no extra claims), category, image_relevance, fact_risks. "
 "This is an UNAPPROVED draft. Never assume copyright or editorial permission. "
 "If an image is provided, judge apparent topic match only, not authenticity or rights. Metadata: "
 +json.dumps(meta,ensure_ascii=False))
 content=[{"type":"input_text","text":prompt}]
 url=item.get("candidate_image_url")
 if isinstance(url,str) and url.startswith("https://"):content.append({"type":"input_image","image_url":url})
 body={"model":os.getenv("ATELIER_EDITORIAL_MODEL","gpt-4.1-mini"),
       "input":[{"role":"user","content":content}],"max_output_tokens":400}
 req=urllib.request.Request("https://api.openai.com/v1/responses",
     data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(req,timeout=45) as resp:data=json.load(resp)
 result="".join(p.get("text","") for o in data.get("output",[]) for p in o.get("content",[]) if p.get("type")=="output_text").strip()
 parsed=json.loads(result)
 if not isinstance(parsed.get("headline_tr"),str) or not isinstance(parsed.get("summary_tr"),str):raise ValueError("Invalid AI answer")
 return {"title_tr_draft":parsed["headline_tr"][:190],"summary_tr_draft":parsed["summary_tr"][:350],
         "suggested_category":parsed.get("category"),"image_relevance":parsed.get("image_relevance","unclear"),
         "fact_risks":parsed.get("fact_risks",[]),"review_status":"ai_draft_unverified",
         "image_license":"not_verified"}
def main():
 feed=json.loads(FEED.read_text())
 now=dt.datetime.now(dt.timezone.utc)
 old={}
 if OUT.exists():
  try:old={x["url"]:x for x in json.loads(OUT.read_text()).get("items",[])}
  except (ValueError,KeyError):pass
 items=[]
 for x in feed.get("items",[]):
  if not all(isinstance(x.get(k),str) for k in ("title","url","published_at","source")):continue
  if not x["url"].startswith("https://"):continue
  try:points,reasons=rank(x,now)
  except ValueError:continue
  item={**x,"category":classify(x["title"],x.get("category","DÜNYA")),
        "score":points,"ranking_reasons":reasons,"editorial_status":"source_link_only",
        "fact_check":"needs_independent_review","image_rights":"not_verified"}
  if isinstance(old.get(x["url"],{}).get("ai_review"),dict):item["ai_review"]=old[x["url"]]["ai_review"]
  items.append(item)
 items.sort(key=lambda x:(x["score"],x["published_at"]),reverse=True)
 leads=[];duplicates=[]
 for item in items:
  match=next((l for l in leads if near_duplicate(item,l)),None)
  if match:duplicates.append({"url":item["url"],"possible_duplicate_of":match["url"]});continue
  leads.append(item)
 key=os.environ.get("OPENAI_API_KEY","").strip()
 max_ai=max(0,min(12,int(os.environ.get("ATELIER_AI_MAX_ITEMS","8"))))
 done=0;errors=0
 if key:
  for item in leads:
   if done>=max_ai:break
   if "ai_review" in item:continue
   try:item["ai_review"]=ai_review(item,key);done+=1
   except Exception as exc:item["ai_review_error"]=type(exc).__name__;errors+=1
 counts={}
 for x in leads:counts[x["category"]]=counts.get(x["category"],0)+1
 result={"schema":1,"generated_at":now.isoformat(),"source_generated_at":feed.get("generated_at"),
  "input_count":len(items),"curated_link_count":len(leads),"possible_duplicate_count":len(duplicates),
  "possible_duplicates":duplicates,"categories":counts,
  "ai":{"configured":bool(key),"new_drafts":done,"errors":errors},
  "notice":"Ranked source links and unapproved research drafts only. Images are not licensed.",
  "items":leads[:70]}
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"input":len(items),"curated":len(leads),"duplicates":len(duplicates),"ai_drafts":done,"ai_errors":errors},ensure_ascii=False))
if __name__=="__main__":main()
