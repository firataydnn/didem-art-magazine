#!/usr/bin/env python3
"""ATELIER source radar. Python stdlib only; produces attributed links, not fabricated articles."""
import datetime as dt, email.utils, html, json, pathlib, re, urllib.request, xml.etree.ElementTree as ET
from urllib.parse import urlparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"world-art-radar.json"
SOURCES=[
 ("The Art Newspaper","https://www.theartnewspaper.com/rss.xml","DÜNYA"),
 ("ARTnews","https://www.artnews.com/feed/","DÜNYA"),
 ("Artnet","https://news.artnet.com/feed","DÜNYA"),
 ("Artforum","https://www.artforum.com/feed/","DÜNYA"),
 ("Frieze","https://www.frieze.com/feed","SERGİLER"),
 ("Hyperallergic","https://hyperallergic.com/feed/","DÜNYA"),
 ("Culture Type","https://www.culturetype.com/feed/","SANATÇILAR"),
 ("MoMA Press","https://press.moma.org/feed/","SERGİLER"),
 ("Monopol","https://www.monopol-magazin.de/rss.xml","DÜNYA"),
 ("Mousse Magazine","https://moussemagazine.it/feed/","DÜNYA"),
 ("Ocula","https://ocula.com/magazine/feed/","DÜNYA"),
 ("Argonotlar","https://argonotlar.com/feed/","TÜRKİYE"),
 ("ArtDog Istanbul","https://artdogistanbul.com/feed/","TÜRKİYE"),
 ("Sanatatak","https://www.sanatatak.com/feed/","TÜRKİYE"),
 ("Studio International","https://www.studiointernational.com/index.php/rss/","DÜNYA"),
 ("ArtAsiaPacific","https://artasiapacific.com/rss","DÜNYA"),
 ("Designboom Art","https://www.designboom.com/art/feed/","SERGİLER"),
]
def clean(s):
 s=re.sub(r"<[^>]*>"," ",html.unescape(s or ""))
 return re.sub(r"\s+"," ",s).strip()
def child(node, names):
 for el in node:
  if el.tag.split("}")[-1].lower() in names:
   return (el.text or "").strip()
 return ""
def date(s):
 try:
  d=email.utils.parsedate_to_datetime(s)
  return d.astimezone(dt.timezone.utc).isoformat()
 except Exception:
  try:return dt.datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(dt.timezone.utc).isoformat()
  except Exception:return None
def classify(title, source, fallback):
 """Transparent provisional routing, not an AI editorial verdict."""
 if fallback=="TÜRKİYE":return "TÜRKİYE"
 t=title.casefold()
 groups=[
  ("PİYASA",("auction","sotheby","christie","sale","sold","record price","art market","müzayede")),
  ("SERGİLER",("exhibition","retrospective","biennial","triennial","museum show","sergi")),
  ("KOLEKSİYON",("acquisition","donation","collection","bequest","gift to museum")),
  ("SANATÇILAR",("artist","painter","sculptor","photographer","sanatçı")),
  ("TARTIŞMALAR",("protest","lawsuit","restitution","censorship","controversy","looted")),
 ]
 for category,terms in groups:
  if any(term in t for term in terms):return category
 return fallback

def image_candidate(entry):
 for el in entry.iter():
  tag=el.tag.split("}")[-1].lower()
  if tag in ("thumbnail","content","enclosure"):
   url=el.attrib.get("url","")
   mime=el.attrib.get("type","")
   if url.startswith("https://") and (tag=="thumbnail" or mime.startswith("image/") or any(url.lower().split("?")[0].endswith("."+ext) for ext in ("jpg","jpeg","png","webp"))):
    return url[:500]
 return None

def source_domain_matches(source_url, article_url):
 """Prevent an RSS entry from redirecting the newspaper to an unrelated host."""
 feed_host=(urlparse(source_url).hostname or "").lower().removeprefix("www.")
 article_host=(urlparse(article_url).hostname or "").lower().removeprefix("www.")
 return bool(feed_host and article_host and (article_host==feed_host or article_host.endswith("."+feed_host)))

def main():
 now=dt.datetime.now(dt.timezone.utc)
 existing={}
 if OUT.exists():
  try:existing={x["url"]:x for x in json.loads(OUT.read_text()).get("items",[])}
  except Exception:pass
 items=[];status=[]
 for name,url,category in SOURCES:
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"ATELIER-Art-Radar/1.0 (+editorial research; contact via publication site)","Accept":"application/rss+xml,application/atom+xml,application/xml,text/xml"})
   with urllib.request.urlopen(req,timeout=15) as response:
    if response.status!=200:raise ValueError("HTTP "+str(response.status))
    payload=response.read(1500000)
   root=ET.fromstring(payload)
   entries=[e for e in root.iter() if e.tag.split("}")[-1] in ("item","entry")]
   count=0
   for entry in entries[:50]:
    title=clean(child(entry,{"title"}))
    link=child(entry,{"link"})
    if not link:
     for el in entry:
      if el.tag.split("}")[-1]=="link" and el.attrib.get("href"):
       link=el.attrib["href"];break
    published=date(child(entry,{"pubdate","published","updated","date"}))
    if not title or not link.startswith("https://") or not published:continue
    if name=="Sanatatak" and not any(word in title.casefold() for word in (
      "sanat","sergi","heykel","resim","galeri","müze","mimar","koleksiyon","fotoğraf","bienal","art ","lee ufan"
    )):continue
    when=dt.datetime.fromisoformat(published)
    if when>now+dt.timedelta(hours=2) or when<now-dt.timedelta(days=7):continue
    if not source_domain_matches(url,link):continue
    key=link.split("#")[0]
    previous=existing.get(key,{})
    items.append({"title":title[:220],"url":key,"source":name,"category":classify(title,name,category),"category_status":"provisional_keyword",
      "published_at":published,"fetched_at":now.isoformat(),"image_status":"not_verified",
      "editorial_status":"source_link_only","candidate_image_url":image_candidate(entry),
      "first_seen_at":previous.get("first_seen_at",now.isoformat())})
    count+=1
   status.append({"source":name,"state":"ok","count":count})
  except Exception as e:
   status.append({"source":name,"state":"failed","reason":str(e)[:180]})
 active_sources={name for name,_,_ in SOURCES}
 for item in existing.values():
  try:
   if item.get("source") in active_sources and dt.datetime.fromisoformat(item["published_at"])>=now-dt.timedelta(days=7):items.append(item)
  except Exception:pass
 unique={}
 for item in items:
  key=item["url"]
  if key not in unique or item["fetched_at"]>unique[key]["fetched_at"]:unique[key]=item
 sorted_items=sorted(unique.values(),key=lambda x:x["published_at"],reverse=True)[:180]
 if not any(x["state"]=="ok" and x["count"]>0 for x in status):
  raise RuntimeError("No source produced a current dated story; retaining the last known good radar data")
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps({"schema":1,"generated_at":now.isoformat(),"notice":"Source links, not independently verified editorial articles. Images are not licensed.","sources":status,"items":sorted_items},ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"items":len(sorted_items),"sources":status},ensure_ascii=False))
if __name__=="__main__":main()
