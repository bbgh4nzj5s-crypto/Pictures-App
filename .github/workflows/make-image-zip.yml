#!/usr/bin/env python3
"""Download official coordinate thumbnail images into a local ZIP.
Run in GitHub Actions; image files are NOT committed to a repository.
"""
import argparse
import html
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from zipfile import ZipFile, ZIP_DEFLATED

BASE = 'https://aipri.jp'
UA = 'Mozilla/5.0 (compatible; PersonalImageArchive/1.0)'

def get(url):
    with urlopen(Request(url, headers={'User-Agent': UA}), timeout=35) as r:
        return r.read()

def find_urls(page, dan):
    content = html.unescape(get(page).decode('utf-8', errors='replace')).replace('\\/', '/')
    # Handles both relative and absolute links and lazy-loaded HTML images.
    pattern = re.compile(r'(?:(?:https?:)?//aipri\.jp)?/?verse/item/img/' + dan + r'/[A-Za-z0-9_-]+_thumb\.(?:webp|png|jpg|jpeg)', re.I)
    found = set()
    for raw in pattern.findall(content):
        if raw.startswith('//'):
            raw = 'https:' + raw
        elif not raw.startswith('http'):
            raw = urljoin(BASE + '/', raw.lstrip('/'))
        found.add(raw)
    # Fallback for alternate placement or different future markup.
    if not found:
        pat2 = re.compile(r'(?P<url>(?:https?://aipri\.jp)?/?[^\s"\'<>]*' + dan + r'[^\s"\'<>]*_thumb\.(?:webp|png|jpg|jpeg))',re.I)
        for raw in pat2.findall(content):
            if raw.startswith('http'):
                found.add(raw)
            else:
                found.add(urljoin(page, raw))
    return sorted(found)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dans', default='oa1,oa2,oa3,oa4')
    args = p.parse_args()
    dans = [x.strip().lower() for x in args.dans.split(',') if x.strip()]
    out = Path('aipri_images_' + '-'.join(dans) + '.zip')
    success, failed = [], []
    with ZipFile(out, 'w', ZIP_DEFLATED, compresslevel=6) as z:
        for dan in dans:
            page = f'{BASE}/verse/item/{dan}.html'
            print(f'Checking {page}', flush=True)
            try:
                urls = find_urls(page, dan)
            except Exception as e:
                print(f'ERROR: {dan}: {e}', flush=True)
                failed.append((dan, str(e)))
                continue
            print(f'Found {len(urls)} thumbnails for {dan}', flush=True)
            for i, url in enumerate(urls, 1):
                filename = Path(urlparse(url).path).name
                try:
                    data = get(url)
                    if len(data) < 100:
                        raise RuntimeError('Unexpectedly small file')
                    # Unique code-bearing filenames at ZIP root for app filename matching.
                    z.writestr(filename, data)
                    success.append(filename)
                    if i % 20 == 0:
                        print(f'  {dan}: {i}/{len(urls)}', flush=True)
                    time.sleep(.04)
                except Exception as e:
                    print(f'  FAILED {filename}: {e}', flush=True)
                    failed.append((url, str(e)))
        z.writestr('_download_report.txt', 'Downloaded: '+str(len(success))+'\nFailed: '+str(len(failed))+'\n' + '\n'.join(f'{u}\t{e}' for u,e in failed))
    print(f'Created {out} with {len(success)} images; {len(failed)} failures', flush=True)
    if not success:
        raise SystemExit('No images retrieved; check official page structure or network access')

if __name__ == '__main__':
    main()
