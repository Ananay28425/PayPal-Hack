// Purpose: check the generated source receipt opens and exposes its evidence.
const {createRequire}=require('node:module');
const assert=require('node:assert/strict');
const req=createRequire('C:/Users/anany/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/receipt-check.cjs');
const {chromium}=req('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Users/anany/AppData/Local/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-win64/chrome-headless-shell.exe',args:['--no-sandbox']});
 try{
 const page=await browser.newPage({viewport:{width:1000,height:900}});
 await page.goto('file:///C:/Users/anany/.codex/visualizations/2026/10/22/01a16531-3a9e-7e10-b819-461801d3b80f/paypal-original-concepts-sources-preview.html');
 const frame=page.frameLocator('iframe');
 const sources=frame.getByRole('button',{name:/Sources/}).first();
 await sources.waitFor({timeout:15000});
 await sources.click();
 await frame.getByText('All ten sponsors have documented capabilities for distinct roles',{exact:true}).first().waitFor({timeout:10000});
 await frame.getByRole('button',{name:'All ten sponsors have documented capabilities for distinct roles',exact:true}).click();
 await frame.locator('p.receipt-card-title').filter({hasText:'All ten sponsors have documented capabilities for distinct roles'}).waitFor({timeout:10000});
 await page.screenshot({path:'C:/Users/anany/.codex/visualizations/2026/10/22/01a16531-3a9e-7e10-b819-461801d3b80f/paypal-original-concepts-sources-qa.png'});
 const fs=require('node:fs');
 const data=JSON.parse(fs.readFileSync('E:/PROGRAMMING-2/PayPal-Hack/research/sponsor-integration-v2.json','utf8'));
 assert.equal(data.sponsors.length,10);
 assert.equal(new Set(data.sponsors.map(x=>x.name)).size,10);
 assert.ok(data.sponsors.every(x=>x.status.includes('not executed')));
 console.log(JSON.stringify({receiptExpanded:true,sponsors:10,implementationStatus:'proposed',screenshot:'paypal-original-concepts-sources-qa.png'}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});

