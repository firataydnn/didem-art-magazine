#!/usr/bin/env python3
"""Monitor public institutional press pages; stage undated links, never misdate/publish."""
import concurrent.futures as cf
import datetime as dt
import json, pathlib, re, urllib.request, urllib.parse
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"data/official-source-watch.json"
SOURCES=[
 ("Art Basel","https://www.artbasel.com/press/releases","GLOBAL","public"),
 ("Frieze Press","https://www.frieze.com/press","GLOBAL","registration_required"),
 ("MoMA Press","https://press.moma.org/news-intro/","USA","public"),
 ("Centre Pompidou","https://www.centrepompidou.fr/fr/offre-aux-professionnels/espace-presse","FRANCE","public"),
 ("Hirshhorn / Smithsonian","https://hirshhorn.si.edu/explore/press-releases/","USA","public"),
 ("documenta","https://documenta.de/en/news","GERMANY","public"),
 ("Sotheby's","https://www.sothebys.com/en/about/services/press","GLOBAL","public"),
 ("Christie's","https://press.christies.com/section/press-releases/?lang=eng","GLOBAL","public"),
 ("İstanbul Modern","https://www.istanbulmodern.org/basin-bultenleri","TÜRKİYE","public"),
 ("La Biennale di Venezia","https://www.labiennale.org/en/news","ITALY","public"),
 ("Tate","https://www.tate.org.uk/press/press-releases","UK","public"),
]
KEYWORDS=("press","release","news","exhibition","sergi","basin","bulten","duyuru","curator","collection","auction","kultur")
class Scanner(HTMLParser):
 def __init__(self):
  super().__init__();self.title="";self.in_title=False;self.href=None;self.parts=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="title":self.in_title=True
  if tag=="a":self.href=a.get("href");self.parts=[]
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
  if tag=="a":
   if self.href:
    label=re.sub(r"\s+"," "," ".join(self.parts)).strip()
    if 15<=len(label)<=180:self.links.append((self.href,label))
   self.href=None;self.parts=[]
 def handle_data(self,data):
  if self.in_title:self.title+=data
  if self.href is not None:self.parts.append(data)
def fetch(src):
 name,url,region,access=src
 rec={"name":name,"url":url,"region":region,"access":access,"status":"failed","candidates":[]}
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"ATELIER-Art-Radar/1.0","Accept":"text/html"})
  with urllib.request.urlopen(req,timeout=15) as response:
   code=response.status
   typ=response.headers.get("Content-Type","").lower()
   if code!=200 or "html" not in typ:raise ValueError("Unexpected HTTP "+str(code)+" content-type "+typ)
   raw=response.read(300000)
  parser=Scanner();parser.feed(raw.decode("utf-8","replace"))
  base_host=urllib.parse.urlparse(url).hostname or ""
  seen=set();candidates=[]
  for href,label in parser.links:
   absolute=urllib.parse.urljoin(url,href).split("#")[0]
   parsed=urllib.parse.urlparse(absolute)
   if parsed.scheme!="https" or not parsed.hostname:continue
   if parsed.hostname!=base_host and not parsed.hostname.endswith("."+base_host):continue
   if absolute==url or absolute in seen:continue
   if not any(k in (label+" "+parsed.path).casefold() for k in KEYWORDS):continue
   seen.add(absolute)
   candidates.append({"title":label[:160],"url":absolute,
       "status":"institutional_page_link_unverified_date"})
   if len(candidates)>=10:break
  rec.update({"status":"reachable","page_title":parser.title.strip()[:130],"candidates":candidates})
 except Exception as e:
  rec["error"]=type(e).__name__+": "+str(e)[:140]
 return rec
def main():
 now=dt.datetime.now(dt.timezone.utc)
 with cf.ThreadPoolExecutor(max_workers=4) as pool:
  results=list(pool.map(fetch,SOURCES))
 payload={"schema":1,"generated_at":now.isoformat(),"notice":"Primary source page monitoring only. Page changes are not verified publication events. Restricted press rooms must not be bypassed.","sources":results}
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"official_pages":len(results),"reachable":sum(x["status"]=="reachable" for x in results),"restricted":sum(x["access"]=="registration_required" for x in results)},ensure_ascii=False))
if __name__=="__main__":main()
