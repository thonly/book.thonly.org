// Load the landing in English (/) and Khmer (/km/) in headless Chrome, served over HTTP from the repo root, at a TRUE
// phone width and at desktop width — and fail loudly.
//
//     node scripts/test-site.mjs                                  # the local files (run scripts/build-site.py first)
//     SITE_URL=https://book.thonly.org node scripts/test-site.mjs # the same checks on the live host
//     SCHEME=light|dark · SHOTS=<dir>                             # force the system theme · save full-page screenshots
//
// Ported 2026-11-26 from demo/test-library.mjs (the landing's checks before the cut-over), then taught both languages,
// the footer's two toggles and the language redirect.
//
// WHY DEVICE EMULATION. A window-size screenshot is not a phone: headless Chrome will not lay a window out narrower than
// ~500px, so a 390px screenshot is a crop of a wider page and LOOKS like sideways overflow. Device-metrics emulation sets
// the real layout viewport.
// ⚠️ WHY THE TIME ZONE AND LOCALE ARE PINNED. "/" redirects a Khmer reader to /km/ before first paint, and the time zone
// is the last tiebreak. On a machine set to Phnom Penh an unpinned run of "/" would silently test the Khmer page. Every
// page check runs as an English browser in Los Angeles with empty storage; the redirect has its own cases.

import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const DPORT = 9344, HPORT = 8768;
const BASE = (process.env.SITE_URL || `http://127.0.0.1:${HPORT}`).replace(/\/$/, "");
const SHOTS = process.env.SHOTS || "";
const SCHEME = process.env.SCHEME || "";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// What each page must say, in its own language.
const LANG = {
    en: { path: "/", home: "Books by Thon Ly", alt: /AI-enhanced/, record: /Read the record/, told: /Link copied|Copy this link: http/,
          el: ["Air", "Earth", "Water", "Fire", "Space"] },
    km: { path: "/km/", home: "សៀវភៅរបស់ លី​ ស៊ីវ​ ថូង", alt: /កែលម្អដោយ AI/, record: /អានកំណត់ត្រា/,
          told: /បានចម្លងតំណ|ចម្លងតំណនេះ៖ http/, el: ["ខ្យល់", "ដី", "ទឹក", "ភ្លើង", "អាកាស"] },
};
const DRAFT_KM = "[ ភាសាខ្មែរនេះជាសេចក្តីព្រាងរបស់យើង រង់ចាំការពិនិត្យពីអ្នកភាសាខ្មែរ ]";
// Each page's five titles, in its own language (founder 2026-11-26: "translate the titles too").
const TITLES = {
    en: ["The Calculus of Moments", "The River That Reverses", "The Seventh of January", "Silicon Simile", "Two Singularities"],
    km: ["គណិតនៃខណៈ", "ទន្លេដែលហូរបញ្ច្រាស", "ថ្ងៃទីប្រាំពីរ ខែមករា", "ឧបមាស៊ីលីកុន", "ឯកវចនភាពពីរ"],
};
// English the Khmer page KEEPS on purpose: people's names, "AI", the toggle's EN, the hosts, and the words the share
// card's picture shows (its alt text describes that English image).
const KEPT = ["Stephen Mitchell", "Liz Greene", "Miss Aquarius", "The Library", "book.thonly.org", "thonly.org", "AI", "EN"];
const PENDING = /coming soon|in preparation|forthcoming|in progress|ឆាប់ៗ|កំពុងរៀបចំ|នឹងមកដល់|នឹងចេញ/i;

const server = SITE_URL_SET() ? null
    : spawn("python3", ["-m", "http.server", String(HPORT), "--bind", "127.0.0.1"], { cwd: join(HERE, ".."), stdio: "ignore" });
function SITE_URL_SET() { return !!process.env.SITE_URL; }
const profile = mkdtempSync(join(tmpdir(), "site-"));
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--lang=en-US",
    `--remote-debugging-port=${DPORT}`, `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });

let ws, seq = 0;
const pending = new Map(), listeners = [];
async function connect() {
    for (let i = 0; i < 60; i++) {
        try {
            const v = await (await fetch(`http://127.0.0.1:${DPORT}/json/version`)).json();
            await fetch(BASE + "/");
            ws = new WebSocket(v.webSocketDebuggerUrl);
            await new Promise((ok, bad) => { ws.onopen = ok; ws.onerror = bad; });
            ws.onmessage = (m) => {
                const d = JSON.parse(m.data);
                if (d.id && pending.has(d.id)) {
                    const { ok, bad } = pending.get(d.id); pending.delete(d.id);
                    d.error ? bad(new Error(d.error.message)) : ok(d.result);
                } else if (d.method) listeners.forEach((f) => f(d));
            };
            return;
        } catch { await sleep(200); }
    }
    throw new Error("Chrome or the HTTP server never answered");
}
function send(method, params = {}, sessionId) {
    const id = ++seq;
    ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    return new Promise((ok, bad) => pending.set(id, { ok, bad }));
}

const failures = [];
const check = (ok, what) => { if (!ok) failures.push(what); console.log(`${ok ? "  ✓" : "  ⛔"} ${what}`); };

// A fresh tab as a given browser: width, locale, time zone. Storage is shared by every tab of this profile, so each
// caller says what storage holds before it navigates.
async function tab(width, { locale = "en-US", tz = "America/Los_Angeles" } = {}) {
    const { targetId } = await send("Target.createTarget", { url: "about:blank" });
    const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
    const errors = [];
    listeners.push((d) => {
        if (d.sessionId !== sessionId) return;
        if (d.method === "Runtime.exceptionThrown") errors.push(d.params.exceptionDetails.text);
        if (d.method === "Log.entryAdded" && d.params.entry.level === "error" && !/fonts\.g/.test(d.params.entry.url || "")) errors.push(`${d.params.entry.text} ${d.params.entry.url || ""}`);
    });
    await send("Runtime.enable", {}, sessionId);
    await send("Log.enable", {}, sessionId);
    await send("Page.enable", {}, sessionId);
    await send("Emulation.setDeviceMetricsOverride", { width, height: 844, deviceScaleFactor: 1, mobile: width < 500 }, sessionId);
    await send("Emulation.setTimezoneOverride", { timezoneId: tz }, sessionId);
    await send("Emulation.setLocaleOverride", { locale }, sessionId);
    await send("Emulation.setUserAgentOverride", { userAgent: (await send("Browser.getVersion")).userAgent.replace("HeadlessChrome", "Chrome"),
        acceptLanguage: locale, platform: "MacIntel" }, sessionId);
    if (SCHEME) await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: SCHEME }] }, sessionId);
    const ev = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }, sessionId)).result.value;
    const go = async (url) => {
        await send("Page.navigate", { url }, sessionId);
        await sleep(150);
        for (let i = 0; i < 80 && !(await ev(`document.readyState === "complete" && document.fonts.status === "loaded"`).catch(() => false)); i++) await sleep(100);
    };
    const close = () => send("Target.closeTarget", { targetId });
    return { sessionId, ev, go, close, errors };
}

// Storage is per origin: open the origin, set it, and only then navigate where the case starts.
async function withStorage(t, entries) {
    await t.go(BASE + "/robots.txt");
    await t.ev(`localStorage.clear(); ${Object.entries(entries).map(([k, v]) => `localStorage.setItem(${JSON.stringify(k)}, ${JSON.stringify(v)});`).join(" ")} true`);
}

async function page(lang, width) {
    const L = LANG[lang];
    const t = await tab(width);
    await withStorage(t, {});
    await t.go(BASE + L.path);
    const { ev } = t;
    console.log(`\n${L.path} · ${width}px`);
    const here = await ev(`location.pathname`);
    check(here === L.path, `stays on ${L.path} as an English browser in Los Angeles with nothing stored (${here})`);
    check((await ev(`document.documentElement.lang`)) === lang, `html lang="${lang}"`);
    const sw = await ev(`document.documentElement.scrollWidth`);
    check(sw <= width, `no sideways overflow (document ${sw}px wide)`);
    const scrollers = await ev(`[...document.querySelectorAll('*')].filter(e => {
        if (e.closest('svg') || /^(textarea|select|input)$/i.test(e.tagName)) return false;
        const s = getComputedStyle(e);
        return !/^(visible|clip)$/.test(s.overflowY) || !/^(visible|clip)$/.test(s.overflowX);
    }).map(e => e.tagName.toLowerCase() + (e.getAttribute('class') ? '.' + e.getAttribute('class') : ''))`);
    check(scrollers.length === 0, `no nested scroll container (${scrollers.join(", ") || "NONE"})`);
    check((await ev(`document.querySelector('.top .home').textContent`)) === L.home, `the header names the site in this language`);
    const img = await ev(`(() => { const i = document.querySelector('img.lib-portrait'); return i ? [i.complete && i.naturalWidth > 0, i.alt] : [false, ""]; })()`);
    check(img[0] && L.alt.test(img[1]), `the portrait loads, and its alt carries the disclosure ("${img[1]}")`);
    check((await ev(`document.querySelectorAll('svg.bookcover').length`)) === 5, `a cover for each book`);
    const els = await ev(`[...document.querySelectorAll('section.pair .el span')].map(s => s.textContent)`);
    check(JSON.stringify(els) === JSON.stringify(L.el), `five pairs in the order received (${els.join(" · ")})`);
    const titles = await ev(`[...document.querySelectorAll('a.give h2')].map(h => [h.textContent, h.closest('[lang]').lang])`);
    check(JSON.stringify(titles.map(([x]) => x)) === JSON.stringify(TITLES[lang]) && titles.every(([, l]) => l === lang),
          `the five titles in this page's language (${titles.map(([x]) => x).join(" · ")})`);
    const drawn = await ev(`[...document.querySelectorAll('svg.bookcover')].map(c => [c.getAttribute('aria-label'), [...c.querySelectorAll('text')].map(t => t.textContent).join(' ')])`);
    check(drawn.length === 5 && drawn.every(([label, text], i) => label.includes(TITLES[lang][i]) && text.replace(/\s/g, "").includes(TITLES[lang][i].replace(/\s/g, ""))),
          `each cover draws and names its title in this page's language`);
    const recs = await ev(`[...document.querySelectorAll('a.give')].map(a => [a.href, a.querySelector('.go').textContent])`);
    check(recs.length === 5 && recs.every(([h, said]) => /^https:\/\/github\.com\/thonly\/[a-z-]+$/.test(h) && L.record.test(said)),
          `five records linked, each saying what it opens`);
    const bar = await ev(`(() => { const t = document.querySelector('.top').getBoundingClientRect(), h = document.querySelector('.top .home').getBoundingClientRect(), b = document.querySelector('.top .share')?.getBoundingClientRect(); return b ? [Math.round(t.right - b.right), Math.round(b.left - h.right)] : null; })()`);
    check(bar && bar[0] <= 1 && bar[1] > 20, `share button right of the site's name, space between (${bar ? "right gap " + bar[0] + "px, between " + bar[1] + "px" : "missing"})`);
    const sheet = await ev(`(() => { window.__shared = null; navigator.share = (d) => { window.__shared = d; return Promise.resolve(); };
        document.getElementById('share').click(); return window.__shared && [window.__shared.url, window.__shared.title]; })()`);
    check(!!sheet && sheet[0] === BASE.replace(/^http:\/\/127\.0\.0\.1:\d+/, "https://book.thonly.org") + L.path && sheet[1] === L.home,
          `share sheet hands over this page's canonical URL and its name (${sheet})`);
    const told = await ev(`(async () => { Object.defineProperty(navigator, 'share', { value: undefined, configurable: true });
        document.getElementById('share').click(); await new Promise(r => setTimeout(r, 300)); return document.getElementById('share-said').textContent; })()`);
    check(L.told.test(told), `fallback says what happened in this language, with no dialog ("${told}")`);
    const cov = await ev(`(() => { const c = document.querySelector('a.give .bookcover').getBoundingClientRect(), h = document.querySelector('a.give h2').getBoundingClientRect(); return [Math.round(c.width), Math.round(c.right), Math.round(h.left), Math.round(c.bottom), Math.round(h.top)]; })()`);
    const [cw, cr, hl, cb, ht] = cov;
    check(cw >= 160, `cover ${cw}px wide: its title reads (≥160)`);
    check(width < 760 ? cb <= ht : cr <= hl, width < 760 ? `one column: the cover sits above the title` : `two columns: the cover sits beside the title`);
    check(!PENDING.test(await ev(`document.body.innerText`)), `named, never pending: no status words anywhere`);
    const icons = await ev(`Promise.all([...document.querySelectorAll('link[rel~=icon], link[rel=apple-touch-icon]')].map(l => fetch(l.href).then(r => l.getAttribute('href') + ' ' + r.status)))`);
    check(icons.length === 3 && icons.every((x) => / 200$/.test(x)), `three icons resolve (${icons.join(", ")})`);
    const og = await ev(`document.querySelector('meta[property="og:image"]')?.content || ""`);
    check(/^https:\/\/book\.thonly\.org\/og\.png$/.test(og), `the preview card is an absolute URL`);
    const alts = await ev(`[...document.querySelectorAll('link[rel=alternate][hreflang]')].map(l => l.hreflang + ' ' + l.href).join(' | ')`);
    check(alts === "en https://book.thonly.org/ | km https://book.thonly.org/km/ | x-default https://book.thonly.org/",
          `hreflang names both pages, English the default`);
    check((await ev(`document.querySelector('link[rel=canonical]').href`)) === "https://book.thonly.org" + L.path, `canonical is this page`);

    // ---- the footer's two toggles: one line, space between
    const ft = await ev(`(() => { const f = document.querySelector('footer.foot'), cs = getComputedStyle(f), r = f.getBoundingClientRect();
        const l = document.querySelector('.foot-tools nav.seg').getBoundingClientRect(), t = document.querySelector('.foot-tools [role=group].seg').getBoundingClientRect();
        const left = r.left + parseFloat(cs.paddingLeft), right = r.right - parseFloat(cs.paddingRight);
        return [Math.round(l.left - left), Math.round(right - t.right), Math.round(Math.abs((l.top + l.bottom) / 2 - (t.top + t.bottom) / 2)), Math.round(t.left - l.right), Math.round(l.height), Math.round(t.height)]; })()`);
    check(ft[0] <= 1 && ft[1] <= 1 && ft[2] <= 2 && ft[3] > 12 && ft[4] < 44 && ft[5] < 44,
          `footer: language left, theme right, one line, space between (left ${ft[0]}px · right ${ft[1]}px · centers ${ft[2]}px apart · ${ft[3]}px between · heights ${ft[4]}/${ft[5]})`);
    const cur = await ev(`[...document.querySelectorAll('a[data-lang]')].map(a => a.dataset.lang + ':' + (a.getAttribute('aria-current') || '-')).join(' ')`);
    check(cur === (lang === "en" ? "en:true km:-" : "en:- km:true"), `the language toggle marks this page current (${cur})`);
    const theme = await ev(`(async () => {
        const out = [], btn = (c) => document.querySelector('[data-theme-choice="' + c + '"]');
        const state = () => [document.documentElement.getAttribute('data-theme') || 'none', localStorage.getItem('book-theme') || 'none',
            getComputedStyle(document.body).backgroundColor, [...document.querySelectorAll('[data-theme-choice]')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.dataset.themeChoice).join()];
        out.push(state()); btn('dark').click(); out.push(state()); btn('light').click(); out.push(state()); btn('auto').click(); out.push(state());
        return out; })()`);
    const [t0, td, tl, ta] = theme;
    check(t0[0] === "none" && t0[3] === "auto", `theme: Auto pressed and no override on a first visit (${t0.join(" · ")})`);
    check(td[0] === "dark" && td[1] === "dark" && td[2] === "rgb(15, 14, 20)" && td[3] === "dark", `theme: Dark paints the dark ground and is stored (${td.join(" · ")})`);
    check(tl[0] === "light" && tl[1] === "light" && tl[2] === "rgb(252, 251, 254)" && tl[3] === "light", `theme: Light paints the light ground and is stored (${tl.join(" · ")})`);
    check(ta[0] === "none" && ta[1] === "none" && ta[3] === "auto", `theme: Auto clears the override and the stored choice (${ta.join(" · ")})`);

    // ---- the Khmer page: its own type, its draft mark, and no English but what it keeps on purpose
    if (lang === "km") {
        check(await ev(`document.fonts.check('16px "Noto Sans Khmer"', 'ក') && document.fonts.check('16px "Noto Serif Khmer"', 'ក')`),
              `the Khmer faces are loaded (Noto Sans Khmer, Noto Serif Khmer)`);
        const ls = await ev(`['.top .home', '.pair .el', '.lab', '.share', '.give .sub'].map(s => { const c = getComputedStyle(document.querySelector(s)); return s + '=' + c.letterSpacing + '/' + c.textTransform + '/' + c.fontStyle; })`);
        check(ls.every((x) => /=normal\/none\/normal$/.test(x)), `Khmer labels: no letter-spacing, no case change, no italic (${ls.join(" · ")})`);
        check((await ev(`document.querySelector('footer .km-draft')?.textContent`)) === DRAFT_KM, `the estate's draft line is in the footer, byte for byte`);
        check(await ev(`/Khmer: OUR DRAFT/.test(document.head.innerHTML) || [...document.head.childNodes].some(n => n.nodeType === 8 && /Khmer: OUR DRAFT/.test(n.data))`),
              `the head says the Khmer is our draft`);
        const english = await ev(`(() => {
            const kept = ${JSON.stringify(KEPT)}.sort((a, b) => b.length - a.length);
            const strip = (s) => { s = s.replace(/https?:\\/\\/\\S+/g, ' '); for (const k of kept) s = s.split(k).join(' '); return s; };
            const out = [];
            const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            for (let n; (n = w.nextNode());) {
                const p = n.parentElement;
                if (!p || p.closest('script,style') || (p.closest('svg') && !p.closest('text'))) continue;
                const left = strip(n.data).match(/[A-Za-z]{2,}/g); if (left) out.push(n.data.trim().slice(0, 60));
            }
            for (const e of document.querySelectorAll('[alt],[aria-label],[title]')) for (const a of ['alt', 'aria-label', 'title']) {
                const v = e.getAttribute(a); if (v && strip(v).match(/[A-Za-z]{2,}/)) out.push(a + '=' + v.slice(0, 60));
            }
            for (const m of document.querySelectorAll('meta[name=description],meta[property^="og:"]:not([property="og:url"]):not([property="og:image"]):not([property="og:type"]):not([property^="og:locale"])')) {
                const v = m.content; if (v && strip(v).match(/[A-Za-z]{2,}/) && !/^\\d+$/.test(v)) out.push(m.getAttribute('property') || m.name);
            }
            if (strip(document.title).match(/[A-Za-z]{2,}/)) out.push('title');
            return out; })()`);
        check(english.length === 0, `no English left on the Khmer page but the names it keeps (${english.join(" | ") || "none"})`);
        const ph = await ev(`[...document.querySelectorAll('svg.bookcover text')].filter(t => /PLACEHOLDER|គំនូរ/.test(t.textContent)).map(t => t.textContent)`);
        check(ph.length === 5 && ph.every((x) => x === "[ គំនូរបណ្តោះអាសន្ន ]"), `each cover's placeholder label is in Khmer`);
    } else {
        check((await ev(`document.querySelector('.km-draft')`)) === null, `the English page carries no Khmer draft line`);
    }
    if (width === 390) await machine(ev, lang);
    check(t.errors.length === 0, `no exceptions or console errors (${t.errors.join(" | ") || "none"})`);
    if (SHOTS) {
        const h = await ev(`document.documentElement.scrollHeight`);
        await send("Emulation.setDeviceMetricsOverride", { width, height: h, deviceScaleFactor: 1, mobile: width < 500 }, t.sessionId);
        await sleep(300);
        const { data } = await send("Page.captureScreenshot", { format: "png" }, t.sessionId);
        writeFileSync(join(SHOTS, `site-${lang}-${width}${SCHEME ? "-" + SCHEME : ""}.png`), Buffer.from(data, "base64"));
    }
    await t.close();
}

// The language choice: stored choice → the browser's language → the Phnom Penh time zone as the last tiebreak; only "/"
// redirects; the toggle stores the choice. The first case is the control (nothing should move).
async function redirects() {
    console.log(`\nthe language choice · 390px`);
    const CASES = [
        ["/", {}, {}, "/", "English browser, Los Angeles, nothing stored → stays on / (the control)"],
        ["/", {}, { locale: "km-KH" }, "/km/", "Khmer browser → /km/"],
        ["/", {}, { tz: "Asia/Phnom_Penh" }, "/km/", "English browser in Phnom Penh, nothing stored → /km/ (the last tiebreak)"],
        ["/", { "book-lang": "en" }, { tz: "Asia/Phnom_Penh", locale: "km-KH" }, "/", "stored English beats a Khmer browser in Phnom Penh"],
        ["/", { "book-lang": "km" }, {}, "/km/", "stored Khmer → /km/"],
        ["/km/", { "book-lang": "en" }, {}, "/km/", "/km/ opened by link never redirects"],
        ["/index.html", {}, { locale: "km-KH" }, "/km/", "/index.html is the root too"],
    ];
    for (const [from, store, who, to, what] of CASES) {
        const t = await tab(390, who);
        await withStorage(t, store);
        await t.go(BASE + from);
        const at = await t.ev(`location.pathname`);
        check(at === to, `${what} (${at})`);
        await t.close();
    }
    const t = await tab(390);
    await withStorage(t, {});
    await t.go(BASE + "/km/");
    await t.ev(`document.querySelector('a[data-lang="en"]').click(); true`);
    await sleep(600);
    for (let i = 0; i < 40 && (await t.ev(`document.readyState`).catch(() => "")) !== "complete"; i++) await sleep(100);
    const [at, stored] = await t.ev(`[location.pathname, localStorage.getItem('book-lang')]`);
    check(at === "/" && stored === "en", `the toggle's EN goes to / and stores the choice (${at}, ${stored})`);
    await withStorage(t, { "book-theme": "dark" });
    await t.go(BASE + "/km/");
    const early = await t.ev(`[document.documentElement.getAttribute('data-theme'), document.querySelector('[data-theme-choice="dark"]').getAttribute('aria-pressed')]`);
    check(early[0] === "dark" && early[1] === "true", `a stored theme is applied on load and shown pressed (${early})`);
    await t.close();
}

// What a machine reads, checked against what the page SHOWS (once per page).
async function machine(ev, lang) {
    const ld = await ev(`[...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)`);
    let data = null;
    try { data = JSON.parse(ld[0]); } catch {}
    check(ld.length === 1 && !!data, `one JSON-LD block, and it parses`);
    check(data?.inLanguage === lang && data?.url === "https://book.thonly.org" + LANG[lang].path, `the markup says this page's language and URL (${data?.inLanguage}, ${data?.url})`);
    const items = data?.mainEntity?.itemListElement || [];
    const dom = await ev(`[...document.querySelectorAll('section.pair')].map(s => [s.querySelector('h2').textContent, s.querySelector('a.give')?.href, s.querySelector('.el span').textContent])`);
    check(items.length === 5 && items.every((it, i) => it.position === i + 1 && it.name === dom[i]?.[2] && it.item?.["@type"] === "Book"
            && it.item.name === TITLES.en[i] && (lang === "en" ? !it.item.alternateName : it.item.alternateName === dom[i]?.[0])
            && it.item.inLanguage === "en" && it.item.subjectOf?.url === dom[i]?.[1]),
          `the markup names the page's five books, in its order, each an English edition with its record (and its Khmer name on /km/)`);
    const roles = (b) => [].concat(b?.contributor || []).map((r) => `${r.roleName}:${r.contributor?.name}`);
    check(items.length === 5 && items.every(({ item: b }) => roles(b).includes("foreword:Thon Ly")
            && (b.author?.name === "Miss Aquarius" || roles(b).includes("compiler:Miss Aquarius"))),
          `each book credits Miss Aquarius (author or compiler) and Thon Ly (foreword)`);
    check(!PENDING.test(ld[0] || "") && !/creativeWorkStatus/.test(ld[0] || ""), `named, never pending: no status in the markup`);
    if (lang !== "en") return;
    const get = async (p) => { const r = await fetch(BASE + p); return [r.status, await r.text()]; };
    const [rs, robots] = await get("/robots.txt");
    const groups = [];
    let g = null, ua = false;
    for (const raw of robots.split("\n")) {
        const line = raw.replace(/#.*/, "").trim(), i = line.indexOf(":");
        if (i < 0) continue;
        const key = line.slice(0, i).trim().toLowerCase(), val = line.slice(i + 1).trim();
        if (key === "user-agent") { if (!ua) groups.push((g = { agents: [], rules: [] })); g.agents.push(val.toLowerCase()); ua = true; }
        else { ua = false; if (g && /^(allow|disallow)$/.test(key)) g.rules.push(`${key}:${val}`); }
    }
    const star = groups.find((x) => x.agents.includes("*")), ai = groups.filter((x) => !x.agents.includes("*"));
    check(rs === 200 && /^Sitemap: https:\/\/book\.thonly\.org\/sitemap\.xml$/m.test(robots) && !!star && !star.rules.some((r) => /^disallow:\S/.test(r)),
          `robots.txt: everyone else, link previews included, is blocked from nothing, and the sitemap is named`);
    const named = ai.flatMap((x) => x.agents);
    const MUST = ["gptbot", "oai-searchbot", "claudebot", "claude-searchbot", "perplexitybot", "google-extended", "ccbot"];
    check(MUST.every((a) => named.includes(a)) && ai.every((x) => x.rules.length === 1 && x.rules[0] === "disallow:/demo/"),
          `robots.txt: the named AI crawlers are kept out of /demo/ and nothing else (${named.length} named)`);
    const [ss, sm] = await get("/sitemap.xml");
    const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
    check(ss === 200 && locs.join(" ") === "https://book.thonly.org/ https://book.thonly.org/km/",
          `sitemap.xml lists both pages and nothing else (${locs.join(", ") || ss})`);
    const [ls, llms] = await get("/llms.txt");
    check(ls === 200 && /^# /.test(llms) && dom.length === 5 && dom.every(([x, h]) => llms.includes(`[${x}](${h})`)) && llms.includes("(https://book.thonly.org/km/)"),
          `llms.txt names all five books with their records, and the Khmer page`);
    check(!/&[a-z]+;|&#\d+;|<[a-z]/i.test(llms) && !PENDING.test(llms), `llms.txt is plain text: no HTML, no entities, no status words`);
}

try {
    await connect();
    for (const lang of ["en", "km"]) for (const w of [390, 1280]) await page(lang, w);
    await redirects();
} catch (e) { failures.push(String(e)); console.log(`  ⛔ ${e}`); }
finally { try { ws?.close(); } catch {} chrome.kill(); server?.kill(); }
console.log(failures.length ? `\n${failures.length} check(s) FAILED` : "\nall checks passed");
process.exit(failures.length ? 1 : 0);
