#!/usr/bin/env python3
"""Run the user's browser-based aipri-pack.js in headless Chromium, per series."""
import argparse
import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

IDS = ['oa4','oa3','oa2','oa1','ring6','ring5','ring4','ring3','ring2','ring1','6','5','4','3','2','1','special']
SOURCE = Path(__file__).with_name('aipri-pack.js')
OUT = Path('aipri-packs')

def get_script(id):
    src = SOURCE.read_text(encoding='utf-8-sig')
    src, n = re.subn(r'const ONLY\s*=\s*\[\s*\];', f"const ONLY = ['{id}'];", src, count=1)
    if n != 1:
        raise RuntimeError('Cannot find ONLY = [] in original JS; format changed')
    src, n = re.subn(
        r'function download\(name, text\)\s*\{.*?\n  \}',
        'function download(name, text) { window.__aipriPackResult = {name, text}; }',
        src, count=1, flags=re.S,
    )
    if n != 1:
        raise RuntimeError('Cannot find download function in original JS; format changed')
    return src

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pages',default='1',help='Comma separated page IDs, or all')
    args=ap.parse_args()
    if args.pages.strip().lower() == 'all':
        requested=IDS
    else:
        requested=list(dict.fromkeys(x.strip().lower() for x in args.pages.split(',') if x.strip()))
    invalid=[x for x in requested if x not in IDS]
    if not requested or invalid:
        raise SystemExit(f'Invalid page IDs: {invalid}; available: {IDS}')
    OUT.mkdir(exist_ok=True)
    report=[]
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True)
        ctx=await browser.new_context(accept_downloads=False,locale='ja-JP')
        page=await ctx.new_page()
        page.set_default_timeout(90000)
        page.on('console', lambda m: print('[browser]',m.text,flush=True) if m.type in ('log','warning','error') else None)
        for id in requested:
            url=f'https://aipri.jp/verse/item/{id}.html'
            print('Opening',url,flush=True)
            try:
                resp=await page.goto(url,wait_until='domcontentloaded',timeout=90000)
                if not resp or resp.status >= 400:
                    raise RuntimeError(f'Page HTTP {resp.status if resp else "no response"}')
                await page.evaluate('window.__aipriPackResult = null')
                # Evaluate source unchanged in behavior except replacing browser downloads with an in-memory result.
                await page.evaluate(get_script(id))
                result=await page.evaluate('window.__aipriPackResult')
                if not result:
                    raise RuntimeError('No pack produced; check selector or page structure')
                obj=json.loads(result['text'])
                if obj.get('page') != id or not obj.get('sets'):
                    raise RuntimeError('Pack returned incorrect page or empty sets')
                filename=f'aipri-pack-{id}.json'
                (OUT/filename).write_text(result['text'],encoding='utf-8')
                failures=sum(not bool(s.get('img')) for s in obj['sets']) + sum(not bool(p.get('img')) for s in obj['sets'] for p in s['parts'])
                part_count=sum(len(s['parts']) for s in obj['sets'])
                print(f'OK: {filename}, {len(obj["sets"])} coordinates, {part_count} parts, {failures} missing images',flush=True)
                report.append({'page':id,'status':'ok','coordinates':len(obj['sets']),'parts':part_count,'missing_images':failures})
            except Exception as e:
                print('FAILED',id,str(e),flush=True)
                report.append({'page':id,'status':'failed','error':str(e)})
        await browser.close()
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if not any(item['status']=='ok' for item in report):
        raise SystemExit('No usable JSON packs created. Check workflow logs and report.json.')

if __name__=='__main__':
    asyncio.run(main())
