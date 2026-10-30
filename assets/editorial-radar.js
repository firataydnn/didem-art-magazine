/* ATELIER global newsroom: sourced links, never auto-approved reporting or imagery. */
(async function(){
  "use strict";
  const tries=["./data/editorial-digest.json","./data/world-art-radar.json"];
  let feed=null;
  for(const path of tries){
    try{
      const r=await fetch(path,{cache:"no-store"});
      if(!r.ok)continue;
      const candidate=await r.json();
      if(Array.isArray(candidate.items)&&candidate.items.length){feed=candidate;break}
    }catch(e){console.warn("Radar feed unavailable:",path)}
  }
  if(!feed)return;
  const main=document.querySelector(".main");
  if(!main)return;
  const safeDate=s=>typeof s==="string"&&/^\d{4}-\d\d-\d\d/.test(s)?s.slice(0,10):"";
  const root=document.createElement("section");root.id="dunya-sanat-radari";
  root.style.cssText="margin:68px 0 44px;padding-top:22px;border-top:3px solid #24231f";
  const header=document.createElement("div");
  header.style.cssText="display:flex;justify-content:space-between;align-items:end;gap:14px;flex-wrap:wrap";
  const h=document.createElement("h2");h.textContent="Dünya Sanat Radarı";
  h.style.cssText="font-size:clamp(35px,5vw,68px);line-height:1.05;letter-spacing:-.06em;font-weight:normal;margin:0";
  const side=document.createElement("span");
  side.style.cssText="font:11px Arial,sans-serif;letter-spacing:1px;color:#806f61";
  side.textContent=(feed.items.length)+" KAYNAK BAĞLANTISI";
  header.append(h,side);
  const standfirst=document.createElement("p");
  standfirst.style.cssText="font:14px/1.7 Arial,sans-serif;color:#555149;max-width:830px;margin:16px 0 25px";
  standfirst.textContent="Dünyadan sanat haberleri. Başlıklar orijinal yayıncılara aittir; bağlantılar kaynaklara gider. Bu akış editoryal inceleme aşamasındadır. Otomatik içerik, doğrulanmış haber metni veya lisanslı fotoğraf yerine geçmez.";
  const filters=document.createElement("div");
  filters.setAttribute("role","group");filters.setAttribute("aria-label","Sanat radarı kategorileri");
  filters.style.cssText="display:flex;flex-wrap:wrap;gap:7px;padding:4px 0 24px;border-bottom:1px solid #c7c1b6";
  const grid=document.createElement("div");
  grid.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,265px),1fr));gap:27px 24px;padding-top:25px";
  const items=feed.items.filter(item=>item&&typeof item.title==="string"&&typeof item.url==="string"&&/^https:\/\/[^/\s]+\//.test(item.url)&&item.source);
  const allowed=["DÜNYA","SERGİLER","PİYASA","KOLEKSİYON","SANATÇILAR","TARTIŞMALAR","TÜRKİYE"];
  const categories=["TÜMÜ",...allowed.filter(c=>items.some(x=>x.category===c))];
  let selected="TÜMÜ";
  function render(){
    grid.replaceChildren();
    const visible=items.filter(x=>selected==="TÜMÜ"||x.category===selected).slice(0,21);
    if(!visible.length){const p=document.createElement("p");p.textContent="Bu kategoride henüz kaynak bulunmuyor.";grid.append(p)}
    visible.forEach((item,i)=>{
      const article=document.createElement("article");
      article.style.cssText="padding:16px 0 20px;border-top:1px solid #c7c1b6;min-width:0";
      const meta=document.createElement("p");meta.style.cssText="font:10px/1.5 Arial,sans-serif;color:#ad4935;letter-spacing:1px;text-transform:uppercase;margin:0 0 12px";
      meta.textContent=(item.category||"DÜNYA")+" / "+item.source+" / "+safeDate(item.published_at);
      const a=document.createElement("a");a.href=item.url;a.target="_blank";a.rel="noopener noreferrer nofollow";
      a.textContent=item.title;
      a.style.cssText="font:normal clamp(20px,2.25vw,28px)/1.2 Georgia,serif;letter-spacing:-.025em;overflow-wrap:anywhere";
      const note=document.createElement("p");note.style.cssText="font:11px/1.55 Arial,sans-serif;color:#716a61;margin:12px 0 0";
      note.textContent="Kaynağa git ↗ · Haber doğrulaması ve görsel hakları inceleme bekliyor";
      article.append(meta,a,note);grid.append(article)
    });
  }
  categories.forEach(cat=>{
    const b=document.createElement("button");b.type="button";b.textContent=cat;
    b.style.cssText="background:transparent;border:1px solid #c7c1b6;padding:8px 12px;font:11px Arial,sans-serif;cursor:pointer";
    b.setAttribute("aria-pressed",String(cat===selected));
    b.addEventListener("click",()=>{
      selected=cat;
      filters.querySelectorAll("button").forEach(k=>{const active=k===b;k.setAttribute("aria-pressed",String(active));k.style.background=active?"#24231f":"transparent";k.style.color=active?"#fff":"#24231f"});
      render()
    });
    if(cat===selected){b.style.background="#24231f";b.style.color="#fff"}
    filters.append(b)
  });
  root.append(header,standfirst,filters,grid);
  main.append(root);render();
})();
