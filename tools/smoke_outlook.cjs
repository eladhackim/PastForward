const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('node:fs');
const output=process.env.PASTFORWARD_SMOKE_OUTPUT || '/tmp/pastforward-outlook-smoke';
const base=process.env.PASTFORWARD_TEST_URL || 'http://127.0.0.1:4183/';
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 fs.mkdirSync(output,{recursive:true});
 const evidence=[];
 try{
 for(const width of [320,390,1440]) for(const theme of ['light','dark']){
  const page=await browser.newPage({viewport:{width,height:900},colorScheme:theme,reducedMotion:'reduce'});
  const errors=[],paid=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/**',route=>{if(/ask|checkout/.test(route.request().url()))paid.push(route.request().url());return route.fulfill({status:200,contentType:'application/json',body:'{}'});});
  await page.goto(new URL('#outlook',base).href,{waitUntil:'networkidle'});
  await page.locator('[data-forecast-year="2026"]').waitFor();
  for(const year of [2026,2027,2028,2029,2030]){
   await page.locator(`[data-forecast-year="${year}"]`).click();
   assert.equal(await page.locator(`[data-forecast-year="${year}"]`).getAttribute('aria-pressed'),'true');
   assert.ok(await page.locator('.outlook-card').count()>=2);
   assert.equal(await page.locator('.outlook-source[href^="https://"]').count(),await page.locator('.outlook-card').count());
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  }
  await page.locator('[data-forecast-topic="money"]').click();
  await page.getByRole('heading',{name:'No published scenario for this selection'}).waitFor();
  await page.getByRole('button',{name:'Show all topics',exact:true}).click();
  assert.ok(await page.locator('.outlook-card').count()>0);
  const detail=page.locator('.outlook-card details').first();await detail.locator('summary').click();assert.equal(await detail.getAttribute('open'),'');
  await page.screenshot({path:`${output}/2030-detail-${width}-${theme}.png`});
  await page.locator('#dBody').evaluate(el=>el.scrollTop=0);
  await page.screenshot({path:`${output}/2030-${width}-${theme}.png`});
  await page.getByRole('button',{name:'Explore your historical lifeline'}).click();
  await page.getByLabel('The year you were born').fill('1990');
  assert.ok(await page.locator('.flist li').count()>0);
  await page.keyboard.press('Escape');await page.locator('.outlook').waitFor();
  await page.keyboard.press('Escape');await page.locator('#deepWrap').waitFor({state:'hidden'});
  await page.screenshot({path:`${output}/home-${width}-${theme}.png`,fullPage:true});
  await page.locator('#outlookYears button').first().click();await page.locator('.outlook').waitFor();
  await page.keyboard.press('Escape');await page.locator('#deepWrap').waitFor({state:'hidden'});
  await page.getByRole('button',{name:'Full story',exact:true}).click();await page.locator('#deepWrap.open').waitFor();
  assert.deepEqual(errors,[]);assert.deepEqual(paid,[]);
  evidence.push({width,theme,years:[2026,2027,2028,2029,2030],emptyState:true,sourceLinks:true,lifeline:true,back:true,legacyStory:true,paidRequests:paid.length,errors});
  await page.close();
 }
 // Clock rollover: old editorial content must not masquerade as a current forecast.
 const page=await browser.newPage();await page.clock.install({time:new Date('2031-02-01T12:00:00Z')});
 await page.route('**/api/**',r=>r.fulfill({status:200,body:'{}'}));
 await page.goto(new URL('#outlook',base).href);await page.locator('.outlook-date.overdue').waitFor();
 assert.equal(await page.locator('[data-forecast-year]').filter({hasText:'This year'}).count(),0);
 assert.equal(await page.locator('#outlookTitle').innerText(),'Explore past outlooks');
 evidence.push({staleDate:'2031-02-01',archivalLabel:true});await page.close();
 fs.writeFileSync(`${output}/results.json`,JSON.stringify(evidence,null,2));
 console.log(JSON.stringify(evidence));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
