// アイプリ コーデ画像パック作成スクリプト(パソコンのブラウザ用)
// 使い方:
//  1. PCのChromeで https://aipri.jp/verse/item/oa4.html などアイプリバースのコーデアイテムページを開く
//  2. F12 → 「Console」タブを開き、このファイルの中身を全部貼り付けて Enter
//     (貼り付けできないときは「allow pasting」と入力して Enter してから貼り付け)
//  3. 弾ごとに aipri-pack-◯◯.json が自動でダウンロードされる(複数ダウンロードの許可を聞かれたら「許可」)
//  4. できたJSONファイルをスマホに共有し、アプリの「設定」→「コーデ画像パックの取り込み」で選ぶ
// 個人利用のための取得です。実行中はサイトに負担をかけないよう、ゆっくり取得します。

(async () => {
  const ONLY = []; // 例: ['oa4','oa3'] のように書くとその弾だけ。空なら全部
  const PAGES = [['oa4','おねがい4だん'],['oa3','おねがい3だん'],['oa2','おねがい2だん'],['oa1','おねがい1だん'],
    ['ring6','リング6だん'],['ring5','リング5だん'],['ring4','リング4だん'],['ring3','リング3だん'],['ring2','リング2だん'],['ring1','リング1だん'],
    ['6','ひみつのアイプリ6だん'],['5','ひみつのアイプリ5だん'],['4','ひみつのアイプリ4だん'],['3','ひみつのアイプリ3だん'],['2','ひみつのアイプリ2だん'],['1','ひみつのアイプリ1だん'],
    ['special','スペシャルコーデアイテム']];
  const TYPE = { 'ワンピ':'O', 'トップス':'T', 'ボトムス':'B', 'シューズ':'S', 'アクセ':'A' };
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  async function shrink(url, max) {
    for (let i = 0; i < 2; i++) {
      try {
        const r = await fetch(url);
        if (!r.ok) throw 0;
        const bmp = await createImageBitmap(await r.blob());
        const s = Math.min(1, max / Math.max(bmp.width, bmp.height));
        const c = document.createElement('canvas');
        c.width = Math.max(1, Math.round(bmp.width * s)); c.height = Math.max(1, Math.round(bmp.height * s));
        const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height);
        x.drawImage(bmp, 0, 0, c.width, c.height);
        return c.toDataURL('image/jpeg', 0.8);
      } catch (e) { await sleep(300); }
    }
    return '';
  }
  async function pool(tasks, n) {
    let i = 0;
    await Promise.all(Array.from({ length: n }, async () => {
      while (i < tasks.length) { const t = tasks[i++]; await t(); await sleep(60); }
    }));
  }
  function codeOf(file) {
    const m = /(OAF?\d-\d{3}|V\d-\d{3})/i.exec(file);
    return m ? m[1].toUpperCase() : file.replace(/(_thumb)?\.\w+$/, '').replace(/F$/, '');
  }
  function parsePage(html, pageUrl) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const head = {};
    doc.querySelectorAll('.tagList__item a[data-show]').forEach(a => { head[a.dataset.show] = a.textContent.trim(); });
    const seen = new Set(), sets = [];
    doc.querySelectorAll('a[data-modal="item"]').forEach(a => {
      const d = a.dataset, file = (d.img || '').split('/').pop();
      const code = codeOf(file), key = code + '|' + d.name;
      if (seen.has(key)) return; seen.add(key);
      const parts = [];
      for (let k = 1; d['term' + k]; k++) {
        const t = TYPE[d['term' + k]]; if (!t) continue;
        parts.push({ t, id: d['id' + k] || '', point: +d['point' + k] || 0, url: new URL(d['img' + k], pageUrl).href });
      }
      sets.push({ code, name: d.name, g: head[d.group] || '', url: d.img ? new URL(d.img, pageUrl).href : '', parts });
    });
    return sets;
  }
  function download(name, text) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
    a.download = name; document.body.appendChild(a); a.click(); a.remove();
  }

  const targets = PAGES.filter(p => !ONLY.length || ONLY.includes(p[0]));
  for (const [id, ser] of targets) {
    const pageUrl = new URL('/verse/item/' + id + '.html', location.href).href;
    let html;
    try { const r = await fetch(pageUrl); if (!r.ok) throw 0; html = await r.text(); }
    catch (e) { console.warn('取得できませんでした: ' + id); continue; }
    const sets = parsePage(html, pageUrl);
    if (!sets.length) { console.warn('コーデが見つかりません: ' + id); continue; }
    let done = 0, total = sets.reduce((n, s) => n + 1 + s.parts.length, 0);
    const tasks = [];
    sets.forEach(s => {
      tasks.push(async () => { s.img = s.url ? await shrink(s.url, 200) : ''; delete s.url; done++; });
      s.parts.forEach(p => tasks.push(async () => { p.img = await shrink(p.url, 160); delete p.url; done++; }));
    });
    const timer = setInterval(() => console.log(ser + ': ' + done + '/' + total), 3000);
    await pool(tasks, 4);
    clearInterval(timer);
    const miss = sets.reduce((n, s) => n + (s.img ? 0 : 1) + s.parts.filter(p => !p.img).length, 0);
    download('aipri-pack-' + id + '.json', JSON.stringify({ v: 1, page: id, ser, sets }));
    console.log('完了: ' + ser + '(' + sets.length + 'コーデ' + (miss ? '、画像取得失敗 ' + miss + '件' : '') + ')');
    await sleep(800);
  }
  console.log('すべて完了しました。ダウンロードされた aipri-pack-*.json をスマホに共有してください。');
})();
