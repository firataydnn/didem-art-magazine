/* Didem Art Magazine — media belongs to relevant page sections, never to an unrelated news photo.
   Every new image is a Higgsfield-generated conceptual editorial illustration. */
(function(){
"use strict";
const urls={"hero":"https://d8j0ntlcm91z4.cloudfront.net/user_36k5oKNr2EbFij24yVgRJr0W1Gv/hf_20261023_175940_51b01d09-735b-4bd3-9b49-00a77e5b0ec0.png","exhibitions":"https://d8j0ntlcm91z4.cloudfront.net/user_36k5oKNr2EbFij24yVgRJr0W1Gv/hf_20261023_175940_ddf007a2-6122-4dd5-aa61-f0cb3c15b91e.png","market":"https://d8j0ntlcm91z4.cloudfront.net/user_36k5oKNr2EbFij24yVgRJr0W1Gv/hf_20261023_175941_246bd65f-9044-4879-991a-9bf7e59b0385.png","istanbul":"https://d8j0ntlcm91z4.cloudfront.net/user_36k5oKNr2EbFij24yVgRJr0W1Gv/hf_20261023_175940_3f3baa64-98f8-4644-846e-94954d47659a.png"};
const categories={"GÜNCEL":"hero","PİYASA":"market","SANATÇI":"exhibitions","ESER ATLASI":"exhibitions","SANAT TARİHİ":"exhibitions","REHBER":"exhibitions","DOSYA":"hero","DEDİKODU":"istanbul"};
const credit="Temsilî editoryal görsel · Higgsfield AI · Gerçek haber veya eser fotoğrafı değildir.";
const st=document.createElement("style");st.textContent="\n/* Art Magazine editorial visuals, 2026-10-23. Concept images are not documentary photographs. */\n.am-visual-category{isolation:isolate;background:#efe9de;position:relative;overflow:hidden}\n.am-visual-category:after{display:none!important}\n.am-visual-category>.am-visual-art{position:absolute;inset:0 0 0 48%;z-index:-1;overflow:hidden;pointer-events:none}\n.am-visual-category>.am-visual-art img{width:100%;height:100%;object-fit:cover;filter:saturate(.78);display:block}\n.am-visual-category:before{content:'';position:absolute;z-index:0;inset:0;background:linear-gradient(90deg,#f4f1ea 0%,#f4f1ea 37%,rgba(244,241,234,.92) 53%,rgba(244,241,234,.15) 75%);pointer-events:none}\n.am-visual-category>:not(.am-visual-art):not(.am-visual-credit){position:relative;z-index:2;max-width:71%}\n.am-visual-category>.am-visual-credit{position:absolute;z-index:3;right:16px;bottom:13px;max-width:230px;text-align:right;font:10px/1.4 Arial,sans-serif;letter-spacing:.04em;color:white;background:rgba(25,24,22,.76);padding:8px 10px}\n.am-banner-credit{display:block;font:10px/1.5 Arial,sans-serif;opacity:.87;margin:12px 0 0}\n.am-aside-visual{background-position:right center!important;background-size:cover!important;position:relative;isolation:isolate}\n.am-aside-visual>*{position:relative;z-index:1}\n.am-aside-visual .am-banner-credit{max-width:300px}\n@media(max-width:900px){\n .am-visual-category{padding-bottom:260px!important}\n .am-visual-category>.am-visual-art{inset:auto 0 0 0;height:260px}\n .am-visual-category:before{background:linear-gradient(180deg,#f4f1ea 0%,#f4f1ea 48%,rgba(244,241,234,0) 74%)}\n .am-visual-category>:not(.am-visual-art):not(.am-visual-credit){max-width:100%}\n .am-visual-category>.am-visual-credit{right:10px;bottom:10px}\n}\n";document.head.append(st);
const cache={};
function preload(type,ok){
 const image=new Image();image.onload=()=>{cache[type]=true;ok(urls[type])};image.onerror=()=>{cache[type]=false};image.src=urls[type];
}
function addCredit(node,kind){
 if(node.querySelector(".am-banner-credit"))return;
 const c=document.createElement("small");c.className="am-banner-credit";c.textContent=credit;c.setAttribute("data-art-magazine-credit",kind);node.append(c);
}
function decorateCategory(){
 const host=document.getElementById("category-feature");
 const hero=host&&host.querySelector(".category-hero");
 if(!hero||hero.classList.contains("am-visual-category"))return;
 const active=document.querySelector(".nav button.active[data-cat]");
 const type=categories[active&&active.dataset.cat]||"hero";
 if(!cache[type])return;
 const art=document.createElement("div");art.className="am-visual-art";
 const image=document.createElement("img");image.src=urls[type];image.alt="Higgsfield üretimi temsili sanat dünyası görseli";image.loading="lazy";image.decoding="async";
 art.append(image);
 const label=document.createElement("small");label.className="am-visual-credit";label.textContent=credit;
 hero.classList.add("am-visual-category");
 hero.insertBefore(art,hero.firstChild);hero.append(label);
}
function decorateBanner(){
 const banner=document.querySelector(".main > .banner");
 if(banner&&cache.hero){
   banner.style.backgroundImage='linear-gradient(90deg,rgba(20,19,17,.89),rgba(20,19,17,.38)),url("'+urls.hero+'")';
   banner.style.backgroundPosition="center";
   banner.style.backgroundSize="cover";
   addCredit(banner,"homepage");
   const small=banner.querySelector("small:first-child");
   if(small)small.textContent="ART MAGAZINE / EDİTORYAL KAPAK";
 }
 const edit=document.querySelector(".main > .edit");
 if(edit&&cache.istanbul&&!edit.classList.contains("am-aside-visual")){
   edit.classList.add("am-aside-visual");
   edit.style.backgroundImage='linear-gradient(90deg,#442a34 0%,rgba(68,42,52,.98) 44%,rgba(68,42,52,.68) 70%,rgba(68,42,52,.20)),url("'+urls.istanbul+'")';
   addCredit(edit,"turkiye");
 }
}
const target=document.getElementById("category-feature");
if(target){const observer=new MutationObserver(decorateCategory);observer.observe(target,{childList:true});}
for(const type of Object.keys(urls))preload(type,()=>{decorateCategory();decorateBanner()});
decorateCategory();decorateBanner();
})();