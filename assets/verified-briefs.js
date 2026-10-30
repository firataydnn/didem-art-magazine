/* ATELIER primary-source-checked Turkish news briefs; image rights not cleared. */
(async function(){
 "use strict";
 try{
  const response=await fetch("./data/verified-briefs.json",{cache:"no-store"});
  if(!response.ok)return;
  const feed=await response.json();
  if(!Array.isArray(feed.items))return;
  const threshold=new Date(Date.now()-7*24*60*60*1000).toISOString().slice(0,10);
  const valid=feed.items.filter(item=>
   typeof item.title==="string"&&typeof item.summary==="string"&&
   typeof item.source_url==="string"&&item.source_url.startsWith("https://")&&
   item.type==="source_checked_editorial_brief"&&
   item.source_date>=threshold
  );
  if(!valid.length)return;
  const main=document.querySelector(".main");if(!main)return;
  const box=document.createElement("section");box.id="dogrulanan-haberler";
  box.style.cssText="margin:55px 0;border-top:3px solid #a34936;padding-top:18px";
  const h=document.createElement("h2");h.textContent="Kaynağından Doğrulananlar";
  h.style.cssText="font-size:clamp(35px,5vw,62px);letter-spacing:-.055em;font-weight:normal;margin:0 0 10px";
  const dek=document.createElement("p");
  dek.textContent="Resmî kurum ve birincil kaynaklara karşı kontrol edilmiş özgün Türkçe haber notları. Fotoğraf hakları kesinleşmediğinden dış kaynak görseli kullanılmıyor.";
  dek.style.cssText="font:13px/1.6 Arial,sans-serif;color:#555149;max-width:850px;margin:0 0 25px";
  const grid=document.createElement("div");
  grid.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:26px";
  for(const item of valid.slice(0,8)){
   const article=document.createElement("article");
   article.style.cssText="padding:17px 0 23px;border-top:1px solid #c7c1b6";
   const meta=document.createElement("p");
   meta.style.cssText="font:11px/1.5 Arial,sans-serif;color:#a34936;letter-spacing:1px;margin:0 0 12px";
   meta.textContent=(item.category||"SANAT")+" · "+item.source_date;
   const title=document.createElement("h3");
   title.style.cssText="font:normal clamp(25px,2.7vw,36px)/1.12 Georgia,serif;letter-spacing:-.03em;margin:0 0 16px";
   title.textContent=item.title;
   const summary=document.createElement("p");
   summary.style.cssText="font:17px/1.65 Georgia,serif;color:#403e39;margin:0 0 18px";
   summary.textContent=item.summary;
   const link=document.createElement("a");
   link.href=item.source_url;link.target="_blank";link.rel="noopener noreferrer";
   link.textContent="Birincil kaynağı oku — "+(item.source_name||"Resmî kaynak");
   link.style.cssText="font:11px/1.5 Arial,sans-serif;border-bottom:1px solid currentColor;padding-bottom:4px";
   article.append(meta,title,summary,link);grid.append(article);
  }
  box.append(h,dek,grid);
  const radar=document.getElementById("dunya-sanat-radari");
  if(radar)main.insertBefore(box,radar);else main.append(box);
 }catch(error){console.warn("Verified briefs could not be displayed",error)}
})();
