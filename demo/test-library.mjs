// Load library.html in headless Chrome, served over HTTP, at a TRUE phone width and at desktop width — and fail loudly.
//
//     node test-library.mjs                     # the draft, demo/library.html
//     LIB_URL=https://book.thonly.org/ node test-library.mjs     # the same checks on the live landing
//
// WHY. A window-size screenshot is not a phone: headless Chrome will not lay a window out narrower than ~500px, so a
// 390px screenshot is a crop of a wider page and LOOKS like sideways overflow (it did, the first time this page was
// drawn). Device-metrics emulation sets the real layout viewport. Checked at each width: no sideways overflow, no
// nested scroll container (the /build rule — on a phone the document is the only scroller), all five pairs present,
// the only link out is the one that says what it opens, and no exception. Screenshots go to SHOTS when it is set.
// Once per URL it also checks what a MACHINE reads — the JSON-LD against the page's own cards, and robots.txt,
// sitemap.xml and llms.txt beside the landing (machine(), below).

import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const DPORT = 9343, HPORT = 8767;
// The server serves the REPO ROOT, so the root-level icons and card resolve exactly as on the host; with no LIB_URL both the
// draft and the promoted landing are tested.
const URLS = process.env.LIB_URL ? [process.env.LIB_URL] : [`http://127.0.0.1:${HPORT}/demo/library.html`, `http://127.0.0.1:${HPORT}/`];
let URL_ = URLS[0];
const SHOTS = process.env.SHOTS || "";
const SCHEME = process.env.SCHEME || "";     // SCHEME=light|dark forces prefers-color-scheme (the host machine may be either)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const server = spawn("python3", ["-m", "http.server", String(HPORT), "--bind", "127.0.0.1"], { cwd: join(HERE, ".."), stdio: "ignore" });
const profile = mkdtempSync(join(tmpdir(), "lib-"));
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars",
    `--remote-debugging-port=${DPORT}`, `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });

let ws, seq = 0;
const pending = new Map(), listeners = [];
async function connect() {
    for (let i = 0; i < 60; i++) {
        try {
            const v = await (await fetch(`http://127.0.0.1:${DPORT}/json/version`)).json();
            await fetch(URL_);
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

async function at(width) {
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
    if (SCHEME) await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: SCHEME }] }, sessionId);
    const ev = async (expr) => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }, sessionId)).result.value;
    await send("Page.navigate", { url: URL_ }, sessionId);
    for (let i = 0; i < 60 && !(await ev(`document.readyState === "complete" && document.fonts.status === "loaded"`)); i++) await sleep(100);
    console.log(`\n${URL_.replace(/^https?:\/\/[^/]+/, "")} · ${width}px`);
    const sw = await ev(`document.documentElement.scrollWidth`);
    check(sw <= width, `no sideways overflow (document ${sw}px wide)`);
    // measure.mjs's predicate, verbatim in effect: svg and form fields are scroll containers by the UA stylesheet and
    // cannot host a sticky page element, so they are not the defect hunted (the first run flagged the five glyphs).
    const scrollers = await ev(`[...document.querySelectorAll('*')].filter(e => {
        if (e.closest('svg') || /^(textarea|select|input)$/i.test(e.tagName)) return false;
        const s = getComputedStyle(e);
        return !/^(visible|clip)$/.test(s.overflowY) || !/^(visible|clip)$/.test(s.overflowX);
    }).map(e => e.tagName.toLowerCase() + (e.getAttribute('class') ? '.' + e.getAttribute('class') : ''))`);
    check(scrollers.length === 0, `no nested scroll container (${scrollers.join(", ") || "NONE"})`);
    const img = await ev(`(() => { const i = document.querySelector('img.lib-portrait'); return i ? [i.complete && i.naturalWidth > 0, i.alt] : [false, ""]; })()`);
    check(img[0] && /AI-enhanced/.test(img[1]), `the portrait loads, and its alt carries the disclosure ("${img[1]}")`);
    const covers = await ev(`document.querySelectorAll('svg.bookcover').length`);
    check(covers === 5, `a cover for each book (${covers})`);
    const pairs = await ev(`document.querySelectorAll('section.pair').length`);
    check(pairs === 5, `five pairs, each received beside given (${pairs})`);
    // every card links to its book's public record, and the link says so
    const recs = await ev(`[...document.querySelectorAll('a.give')].map(a => [a.href, /Read the record/.test(a.textContent)])`);
    check(recs.length === 5 && recs.every(([h, said]) => /^https:\/\/github\.com\/thonly\/[a-z-]+$/.test(h) && said),
          `five records linked, each saying what it opens (${recs.map(([h]) => h.split("/").pop()).join(", ")})`);
    // the share button sits at the right of the header bar
    const bar = await ev(`(() => { const t = document.querySelector('.top').getBoundingClientRect(), h = document.querySelector('.top .home').getBoundingClientRect(), b = document.querySelector('.top .share')?.getBoundingClientRect(); return b ? [Math.round(t.right - b.right), Math.round(b.left - h.right)] : null; })()`);
    check(bar && bar[0] <= 1 && bar[1] > 20, `share button right of "Books by Thon Ly", space between (${bar ? "right gap " + bar[0] + "px, between " + bar[1] + "px" : "missing"})`);
    // both paths: the system share sheet where it exists, and the fallback that tells the reader what happened
    const sheet = await ev(`(() => { window.__shared = null; navigator.share = (d) => { window.__shared = d; return Promise.resolve(); };
        document.getElementById('share').click(); return window.__shared && window.__shared.url; })()`);
    check(!!sheet, `share sheet path hands over the URL (${sheet})`);
    const told = await ev(`(async () => { delete navigator.share; Object.defineProperty(navigator, 'share', { value: undefined, configurable: true });
        document.getElementById('share').click(); await new Promise(r => setTimeout(r, 300)); return document.getElementById('share-said').textContent; })()`);
    check(/Link copied|Copy this link: http/.test(told), `fallback says what happened, with no dialog ("${told}")`);
    // the cover: beside the text on a wide screen, above it on a phone, large enough for its title to read
    const cov = await ev(`(() => { const c = document.querySelector('a.give .bookcover').getBoundingClientRect(), h = document.querySelector('a.give h2').getBoundingClientRect(); return [Math.round(c.width), Math.round(c.right), Math.round(h.left), Math.round(c.bottom), Math.round(h.top)]; })()`);
    const [cw, cr, hl, cb, ht] = cov;
    check(cw >= 160, `cover ${cw}px wide: its title reads (≥160)`);
    check(width < 760 ? cb <= ht : cr <= hl, width < 760 ? `one column: the cover sits above the title (${cb} ≤ ${ht})` : `two columns: the cover sits beside the title (${cr} ≤ ${hl})`);
    const pending_ = await ev(`/coming soon|in preparation|forthcoming|in progress/i.test(document.body.innerText)`);
    check(!pending_, `named, never pending: no status words anywhere`);
    // the icons resolve and the preview card is an absolute URL (a relative og:image yields a card with no image)
    const icons = await ev(`Promise.all([...document.querySelectorAll('link[rel~=icon], link[rel=apple-touch-icon]')].map(l => fetch(l.href).then(r => l.getAttribute('href') + ' ' + r.status)))`);
    check(icons.length === 3 && icons.every((t) => / 200$/.test(t)), `three icons resolve (${icons.join(", ")})`);
    const og = await ev(`document.querySelector('meta[property="og:image"]')?.content || ""`);
    check(/^https:\/\/book\.thonly\.org\/og\.png$/.test(og), `the preview card is an absolute URL (${og})`);
    if (width === 390) await machine(ev);
    check(errors.length === 0, `no exceptions or console errors (${errors.join(" | ") || "none"})`);
    if (SHOTS) {
        const h = await ev(`document.documentElement.scrollHeight`);
        await send("Emulation.setDeviceMetricsOverride", { width, height: h, deviceScaleFactor: 1, mobile: width < 500 }, sessionId);
        await sleep(300);
        const { data } = await send("Page.captureScreenshot", { format: "png" }, sessionId);
        writeFileSync(join(SHOTS, `library-${width}${SCHEME ? "-" + SCHEME : ""}.png`), Buffer.from(data, "base64"));
    }
    await send("Target.closeTarget", { targetId });
}

// What a machine reads, checked against what the page SHOWS (once per URL). The landing carries schema.org JSON-LD and has
// robots.txt, sitemap.xml and llms.txt beside it, all written by build-library.py --landing from the same five pairs; the
// draft carries no markup at all (it is unlisted, and must not tell a machine about itself).
const PENDING = /coming soon|in preparation|forthcoming|in progress/i;
async function machine(ev) {
    const ld = await ev(`[...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)`);
    if (new URL(URL_).pathname !== "/") { check(ld.length === 0, `the draft tells machines nothing: no JSON-LD (${ld.length})`); return; }
    let data = null;
    try { data = JSON.parse(ld[0]); } catch {}
    check(ld.length === 1 && !!data, `one JSON-LD block, and it parses (${ld.length})`);
    const items = data?.mainEntity?.itemListElement || [];
    const dom = await ev(`[...document.querySelectorAll('section.pair')].map(s => [s.querySelector('h2').textContent, s.querySelector('a.give')?.href, s.querySelector('.el span').textContent])`);
    check(items.length === 5 && items.every((it, i) => it.position === i + 1 && it.name === dom[i]?.[2] && it.item?.["@type"] === "Book"
            && it.item.name === dom[i]?.[0] && it.item.subjectOf?.url === dom[i]?.[1]),
          `the markup names the page's five books, in its order, each with its record (${items.map((it) => it.item?.name).join(" · ")})`);
    const roles = (b) => [].concat(b?.contributor || []).map((r) => `${r.roleName}:${r.contributor?.name}`);
    check(items.length === 5 && items.every(({ item: b }) => roles(b).includes("foreword:Thon Ly")
            && (b.author?.name === "Miss Aquarius" || roles(b).includes("compiler:Miss Aquarius"))),
          `each book credits Miss Aquarius (author or compiler) and Thon Ly (foreword)`);
    check(!PENDING.test(ld[0] || "") && !/creativeWorkStatus/.test(ld[0] || ""), `named, never pending: no status in the markup`);
    const get = async (p) => { const r = await fetch(new URL(p, URL_)); return [r.status, await r.text()]; };
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
          `robots.txt: everyone else, link previews included, is blocked from nothing, and the sitemap is named (${rs})`);
    const named = ai.flatMap((x) => x.agents);
    const MUST = ["gptbot", "oai-searchbot", "claudebot", "claude-searchbot", "perplexitybot", "google-extended", "ccbot"];
    check(MUST.every((a) => named.includes(a)) && ai.every((x) => x.rules.length === 1 && x.rules[0] === "disallow:/demo/"),
          `robots.txt: the named AI crawlers are kept out of /demo/ and nothing else (${named.length} named)`);
    const [ss, sm] = await get("/sitemap.xml");
    const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
    check(ss === 200 && locs.includes("https://book.thonly.org/") && locs.every((l) => l.startsWith("https://book.thonly.org/") && !l.includes("/demo/")),
          `sitemap.xml lists the landing, nothing off this host, never /demo/ (${locs.join(", ") || ss})`);
    const [ls, llms] = await get("/llms.txt");
    check(ls === 200 && /^# /.test(llms) && dom.length === 5 && dom.every(([t, h]) => llms.includes(`[${t}](${h})`)),
          `llms.txt names all five books, each linked to its record (${ls})`);
    check(!/&[a-z]+;|&#\d+;|<[a-z]/i.test(llms) && !PENDING.test(llms), `llms.txt is plain text: no HTML, no entities, no status words`);
}

try {
    await connect();
    for (const u of URLS) { URL_ = u; for (const w of [390, 1280]) await at(w); }
} catch (e) { failures.push(String(e)); console.log(`  ⛔ ${e}`); }
finally { try { ws?.close(); } catch {} chrome.kill(); server.kill(); }
console.log(failures.length ? `\n${failures.length} check(s) FAILED` : "\nall checks passed");
process.exit(failures.length ? 1 : 0);
