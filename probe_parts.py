import asyncio, json, re
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright

URL = 'https://aipri.jp/verse/item/1.html'
OUT = Path('part_probe'); OUT.mkdir(exist_ok=True)
async def main():
  async with async_playwright() as pw:
    browser = await pw.chromium.launch(headless=True)
    page = await browser.new_page(viewport={'width':1280,'height':900}, locale='ja-JP')
    responses = {}
    def record(resp):
      u=resp.url
      if re.search(r'\.(?:png|jpe?g|webp)(?:\?|$)',u,re.I):
        responses[u]={'status':resp.status,'type':resp.headers.get('content-type','')}
    page.on('response', record)
    await page.goto(URL,wait_until='domcontentloaded',timeout=60000)
    await page.wait_for_timeout(2500)
    before=await page.evaluate('''() => [...document.images].map(i=>({src:i.currentSrc || i.src, alt:i.alt,outer:i.outerHTML.slice(0,500)}))''')
    (OUT/'initial_images.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
    clicked=[]
    # Find the named thumbnail image and click its nearest interactive ancestor
    candidates=page.locator('img[alt*="ポッピンハートバズリウム"]')
    n=await candidates.count()
    for j in range(min(n,4)):
      try:
        img=candidates.nth(j)
        if not await img.is_visible(): continue
        await img.click(timeout=8000)
        await page.wait_for_timeout(2200)
        clicked.append({'clicked':j,'images':await page.evaluate('''() => [...document.images].filter(i=>i.getClientRects().length).map(i=>({src:i.currentSrc||i.src,alt:i.alt,html:i.outerHTML.slice(0,500)}))'''),'text':(await page.locator('body').inner_text())[-6000:]})
        await page.screenshot(path=str(OUT/'popup.png'),full_page=False)
        break
      except Exception as e: clicked.append({'attempt':j,'error':str(e)[:500]})
    (OUT/'popup_details.json').write_text(json.dumps(clicked,ensure_ascii=False,indent=2))
    (OUT/'network_images.json').write_text(json.dumps(responses,ensure_ascii=False,indent=2))
    (OUT/'page_html_excerpt.txt').write_text((await page.content())[:500000])
    print('Thumb candidates:', n, 'captured network image requests:',len(responses), 'clicked:',len(clicked))
    await browser.close()
asyncio.run(main())
