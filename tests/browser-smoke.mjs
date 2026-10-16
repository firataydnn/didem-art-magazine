import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const base='http://127.0.0.1:8765/';
const out='test-results';
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true});
const errors=[];
let passed=0;
async function check(label,fn){try{await fn();passed++;console.log('PASS',label)}catch(e){console.error('FAIL',label,e);throw e}}
async function contextFor(viewport){return browser.newContext({viewport,reducedMotion:'reduce',locale:'tr-TR'})}
try{
 const desktop=await contextFor({width:1440,height:900});
 const page=await desktop.newPage();
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(base,{waitUntil:'networkidle'});
 await check('33 articles render',async()=>assert.equal(await page.locator('#grid article.card').count(),33));
 await check('first six editorial card images are eagerly loaded',async()=>{
   const images=page.locator('#grid article.card img');
   for(let i=0;i<6;i++){
     const state=await images.nth(i).evaluate(img=>({loading:img.loading,ready:img.complete&&img.naturalWidth>0}));
     assert.equal(state.loading,'eager');
     assert.ok(state.ready,'Editorial image '+i+' is blank')
   }
 });
 await check('featured images all distinct and load from same origin',async()=>{
   const sources=new Set();
   for(let i=0;i<10;i++){
     await page.locator('#slide-dots button').nth(i).click();
     const result=await page.locator('#slide-img').evaluate(img=>({src:img.currentSrc,ok:img.complete&&img.naturalWidth>0}));
     assert.ok(result.src.includes('/assets/images/'),result.src);
     assert.ok(result.ok,'slide '+(i+1)+' did not load');
     sources.add(result.src)
   }
   assert.equal(sources.size,10)
 });
 await check('search returns matching articles and clear restores all',async()=>{
   await page.locator('#q').fill('Hokusai');
   assert.ok(await page.locator('#grid article.card').count()>=1);
   assert.ok(await page.locator('#grid article.card').count()<33);
   await page.locator('#search-clear').click();
   assert.equal(await page.locator('#grid article.card').count(),33)
 });
 await check('category navigation and all reset',async()=>{
   await page.locator('button[data-cat="SANATÇI"]').click();
   await page.waitForTimeout(100);
   assert.ok(page.url().includes('kategori/'));
   const count=await page.locator('#grid article.card').count();
   assert.ok(count>0&&count<33);
   await page.locator('button[data-cat="TÜMÜ"]').click();
   assert.equal(await page.locator('#grid article.card').count(),33)
 });
 await check('article opens, shareable URL and Escape close',async()=>{
   await page.locator('#grid .card button.more').first().click();
   await page.waitForTimeout(100);
   assert.ok(page.url().includes('#/yazi/'));
   assert.equal(await page.locator('#overlay.on').count(),1);
   assert.equal(await page.locator('#post h2').count(),1);
   assert.equal(await page.locator('#post .longform-cover img').count(),1);
   await page.keyboard.press('Escape');
   await page.waitForTimeout(100);
   assert.equal(await page.locator('#overlay.on').count(),0)
 });
 await check('direct article URL loads',async()=>{
   await page.goto(base+'#/yazi/yildizli-gece-gokyuzunun-hafizasi',{waitUntil:'domcontentloaded'});
   await page.waitForTimeout(100);
   assert.equal(await page.locator('#overlay.on').count(),1);
   assert.ok((await page.locator('#post h2').innerText()).includes('Yıldızlı Gece'));
   await page.locator('#overlay .close').click();
   await page.waitForTimeout(100);
   assert.equal(await page.locator('#overlay.on').count(),0)
 });
 await check('dedikodu feature selects correct category',async()=>{
   await page.locator('button[data-cat="TÜMÜ"]').click();
   await page.locator('button:has-text("Dedikodu bölümünü keşfet")').click();
   await page.waitForTimeout(100);
   assert.equal(await page.locator('#grid article.card').count(),1);
   assert.ok((await page.locator('#grid h3').first().innerText()).includes('Sanat kulisleri'))
 });
 await check('article opened from category returns to the same category',async()=>{
   await page.locator('button[data-cat="SANATÇI"]').click();
   await page.waitForTimeout(100);
   await page.locator('#grid .card button.more').first().click();
   await page.waitForTimeout(100);
   assert.ok(page.url().includes('#/yazi/'));
   await page.locator('#overlay .close').click();
   await page.waitForTimeout(150);
   assert.ok(decodeURIComponent(page.url()).includes('kategori/SANATÇI'));
   assert.equal(await page.locator('#overlay.on').count(),0);
   await page.locator('button[data-cat="TÜMÜ"]').click()
 });
 await check('ticker stories open intended article',async()=>{
   await page.locator('[data-open-article="12"]').click();
   await page.waitForTimeout(100);
   assert.ok((await page.locator('#post h2').innerText()).includes('Büyük Dalga'));
   await page.keyboard.press('Escape')
 });
 await check('editorial policy and licensing pages load from footer',async()=>{
   const policy=page.locator('footer a[href="yayin-ilkeleri.html"]');
   const rights=page.locator('footer a[href="gorsel-haklari.html"]');
   assert.equal(await policy.count(),1);
   assert.equal(await rights.count(),1);
   const p=await desktop.newPage();
   await p.goto(base+'yayin-ilkeleri.html',{waitUntil:'domcontentloaded'});
   assert.ok((await p.locator('h1').innerText()).includes('Yayın ilkeleri'));
   await p.goto(base+'gorsel-haklari.html',{waitUntil:'networkidle'});
   assert.ok((await p.locator('h1').innerText()).includes('Görsel hakları'));
   assert.equal(await p.locator('#assets tr').count(),20);
   const rightsDepth=await p.evaluate(()=>document.documentElement.scrollHeight/innerHeight);
   assert.ok(rightsDepth>=5,'image rights page under five screens: '+rightsDepth);
   await p.goto(base+'yayin-ilkeleri.html',{waitUntil:'domcontentloaded'});
   assert.equal(await p.locator('section.standard').count(),11);
   const policyDepth=await p.evaluate(()=>document.documentElement.scrollHeight/innerHeight);
   assert.ok(policyDepth>=5,'editorial policy page under five screens: '+policyDepth);
   await p.close()
 });
 await check('editorial AI banner is hosted locally',async()=>{
   const style=await page.locator('aside.banner').getAttribute('style');
   assert.ok(style.includes('assets/images/atelier-original-ai-banner.png'));
   const response=await page.request.get(base+'assets/images/atelier-original-ai-banner.png');
   assert.equal(response.status(),200);
   assert.ok((await response.body()).length>1000)
 });
 await check('all 33 articles have five unique chapters and five-screen reading depth',async()=>{
   const result=await page.evaluate(()=>{
     const report=[];
     for(let i=0;i<data.length;i++){
       showPost(i);
       const chapters=document.querySelectorAll('#post .reader-chapter');
       const titles=Array.from(chapters,el=>el.querySelector('h3')?.textContent||'');
       report.push({i,chapters:chapters.length,unique:new Set(titles).size,ratio:overlay.scrollHeight/overlay.clientHeight});
     }
     hidePost();
     return report
   });
   assert.equal(result.length,33);
   for(const x of result){assert.equal(x.chapters,5,'chapter count '+x.i);assert.equal(x.unique,5,'unique chapter titles '+x.i);assert.ok(x.ratio>=5,'not five screens '+JSON.stringify(x))}
 });
 await check('all eight category pages have four substantial editorial features and five-screen depth',async()=>{
   const report=await page.evaluate(()=>{
     const result=[];
     for(const name of ['GÜNCEL','PİYASA','SANATÇI','ESER ATLASI','SANAT TARİHİ','REHBER','DOSYA','DEDİKODU']){
       cat=name;render();
       result.push({name,features:document.querySelectorAll('#category-feature .category-chapter').length,ratio:document.documentElement.scrollHeight/innerHeight});
     }
     cat='TÜMÜ';render();return result
   });
   for(const x of report){assert.equal(x.features,4,'category chapters '+x.name);assert.ok(x.ratio>=5,'category shorter than five screens '+JSON.stringify(x))}
 });
 await check('no uncaught browser JS errors',async()=>assert.deepEqual(errors,[]));
 await page.goto(base,{waitUntil:'networkidle'});
 await page.evaluate(()=>{window.scrollTo(0,0);showSlide(0)});
 await page.screenshot({path:path.join(out,'atelier-desktop.png'),fullPage:true});
 await page.locator('button[data-cat="SANATÇI"]').click();
 await page.waitForTimeout(100);
 await page.evaluate(()=>window.scrollTo(0,0));
 await page.screenshot({path:path.join(out,'atelier-category-desktop.png')});
 await page.locator('button[data-cat="TÜMÜ"]').click();
 await page.locator('#grid .card button.more').nth(10).click();
 await page.waitForTimeout(100);
 await page.screenshot({path:path.join(out,'atelier-reader-desktop.png')});
 await page.locator('#chapter-10-1').scrollIntoViewIfNeeded();
 await page.screenshot({path:path.join(out,'atelier-chapter-desktop.png')});
 await page.keyboard.press('Escape');
 await desktop.close();
 const mobile=await contextFor({width:390,height:844});
 const mp=await mobile.newPage();
 mp.on('pageerror',e=>errors.push(String(e)));
 await mp.goto(base,{waitUntil:'networkidle'});
 await check('mobile navigation and article cards fit viewport',async()=>{
   const width=await mp.evaluate(()=>({scroll:document.documentElement.scrollWidth,inner:innerWidth}));
   assert.ok(width.scroll<=width.inner+2,JSON.stringify(width));
   assert.equal(await mp.locator('#grid article.card').count(),33)
 });
 await check('all 33 long-form articles and eight category landings exceed five mobile screens',async()=>{
   const result=await mp.evaluate(()=>{
     const articles=[];
     for(let i=0;i<data.length;i++){showPost(i);articles.push({i,ratio:overlay.scrollHeight/overlay.clientHeight})}
     hidePost();
     const categories=[];
     for(const name of Object.keys(CATEGORY_EDITORIAL)){cat=name;render();categories.push({name,ratio:document.documentElement.scrollHeight/innerHeight})}
     cat='TÜMÜ';render();return {articles,categories}
   });
   for(const x of result.articles)assert.ok(x.ratio>=5,'mobile article under five screens '+JSON.stringify(x));
   for(const x of result.categories)assert.ok(x.ratio>=5,'mobile category under five screens '+JSON.stringify(x))
 });
 await check('mobile modal opens, closes and fits viewport',async()=>{
   await mp.locator('#grid article.card button.more').first().click();
   await mp.waitForTimeout(100);
   assert.equal(await mp.locator('#overlay.on').count(),1);
   await mp.locator('#overlay .close').click();
   await mp.locator('#overlay').evaluate(el=>new Promise((resolve,reject)=>{if(!el.classList.contains('on'))return resolve();const start=Date.now();const id=setInterval(()=>{if(!el.classList.contains('on')){clearInterval(id);resolve()}else if(Date.now()-start>3000){clearInterval(id);reject(new Error('Mobile modal did not close'))}},30)}));
   assert.equal(await mp.locator('#overlay.on').count(),0)
 });
 await check('tablet and narrow desktop layouts avoid horizontal overflow',async()=>{
   for(const width of [768,820,1024]){
     await mp.setViewportSize({width,height:900});
     await mp.waitForTimeout(40);
     const measure=await mp.evaluate(()=>({scroll:document.documentElement.scrollWidth,inner:innerWidth}));
     assert.ok(measure.scroll<=measure.inner+2,'horizontal overflow at '+width+': '+JSON.stringify(measure))
   }
   await mp.setViewportSize({width:390,height:844})
 });
 await mp.goto(base,{waitUntil:'networkidle'});
 await mp.evaluate(()=>window.scrollTo(0,0));
 await mp.screenshot({path:path.join(out,'atelier-mobile.png'),fullPage:true});
 await mp.locator('#grid .card button.more').nth(10).click();
 await mp.waitForTimeout(100);
 await mp.screenshot({path:path.join(out,'atelier-reader-mobile.png')});
 await mp.keyboard.press('Escape');
 await mobile.close();
 assert.deepEqual(errors,[]);
 console.log('ALL '+passed+' BROWSER CHECKS PASSED');
}finally{await browser.close()}
