// Drive walkthrough.html in headless Chrome, served over HTTP, at phone and desktop width — and fail loudly.
//
//     node test-walkthrough.mjs
//
// WHY. A prototype is all script, so a silent error costs everything: the page renders and nothing works. Parsing
// proves it is JavaScript; only running it proves it WORKS. This walks every screen and both paths, and checks the
// defects that have shipped before on the estate's demo sites: a [hidden] leak, a nested scroller on a phone, a Back
// button that leaves the site, and an exception nobody saw.
//
// Served by `python3 -m http.server`, never file:// — the environment that DELIVERS is the one that tells the truth.

import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const DPORT = 9341, HPORT = 8765;
// WALK_BASE=https://book.thonly.org/demo/walkthrough.html node test-walkthrough.mjs  → the same checks on the live host
const BASE = process.env.WALK_BASE || `http://127.0.0.1:${HPORT}/walkthrough.html`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const server = spawn("python3", ["-m", "http.server", String(HPORT), "--bind", "127.0.0.1"], { cwd: HERE, stdio: "ignore" });
const profile = mkdtempSync(join(tmpdir(), "walk-"));
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars",
    `--remote-debugging-port=${DPORT}`, `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });

let ws, seq = 0;
const pending = new Map(), listeners = [];
async function connect() {
    for (let i = 0; i < 60; i++) {
        try {
            const v = await (await fetch(`http://127.0.0.1:${DPORT}/json/version`)).json();
            await fetch(BASE);                                   // the HTTP server is up too
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

async function page(width) {
    const { targetId } = await send("Target.createTarget", { url: "about:blank" });
    const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
    const errors = [];
    listeners.push((d) => {
        if (d.sessionId !== sessionId) return;
        if (d.method === "Runtime.exceptionThrown") errors.push(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text);
        if (d.method === "Log.entryAdded" && d.params.entry.level === "error" && !/fonts\.g/.test(d.params.entry.url || "")) errors.push(`${d.params.entry.text} ${d.params.entry.url || ""}`);
    });
    await send("Runtime.enable", {}, sessionId);
    await send("Log.enable", {}, sessionId);
    await send("Page.enable", {}, sessionId);
    await send("Emulation.setDeviceMetricsOverride", { width, height: 844, deviceScaleFactor: 1, mobile: width < 500 }, sessionId);
    const ev = async (expr) => {
        const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }, sessionId);
        if (r.exceptionDetails) throw new Error(`in page: ${r.exceptionDetails.exception?.description || r.exceptionDetails.text}`);
        return r.result.value;
    };
    // ⚠️ WAIT FOR THE APP, NEVER FOR A CLOCK. A fixed delay passed until an image made the load slower, and then the
    // first two screens read as "none visible" — the page was fine; the test had looked too early.
    const go = async (url) => {
        await send("Page.navigate", { url }, sessionId);
        if (!url.includes("walkthrough.html")) { await sleep(200); return; }   // about:blank has no app to wait for
        for (let i = 0; i < 60; i++) {
            const ready = await ev(`!!document.querySelector('.screen:not([hidden])')`).catch(() => false);
            if (ready) return;
            await sleep(100);
        }
        throw new Error(`the app never became ready at ${url}`);
    };
    return { targetId, ev, go, errors };
}

const SCREENS = ["library", "book", "story", "story/1", "story/4", "debate", "debate/2", "objection/O-07", "method",
    "evidence", "record", "thanks", "sent", "copy", "copydone"];

const VISIBLE = `(() => [...document.querySelectorAll('.screen')].filter(s => !s.hidden && s.getClientRects().length)
    .map(s => s.dataset.screen))()`;
const SCROLLERS = `(() => [...document.querySelectorAll('*')].filter(e => {
    if (e.closest('svg') || /^(textarea|select|input)$/i.test(e.tagName)) return false;
    const s = getComputedStyle(e);
    return !/^(visible|clip)$/.test(s.overflowY) || !/^(visible|clip)$/.test(s.overflowX);
  }).map(e => e.tagName.toLowerCase() + (e.getAttribute('class') ? '.' + e.getAttribute('class').split(' ').join('.') : '')))()`;

try {
    await connect();
    for (const width of [390, 1280]) {
        console.log(`\n── ${width}px`);
        const p = await page(width);
        await p.go(BASE);

        for (const s of SCREENS) {
            await p.ev(`location.hash = '#/${s}'`); await sleep(120);
            const vis = await p.ev(VISIBLE);
            const title = await p.ev(`document.getElementById('bar-title').textContent`);
            check(vis.length === 1 && vis[0] === s && title.length > 0, `#/${s} — exactly one screen shows (${vis.join(",") || "none"}), bar "${title}"`);
        }

        const wide = await p.ev(`document.documentElement.scrollWidth`);
        check(wide <= width, `no sideways overflow (${wide}px)`);
        const scrollers = await p.ev(SCROLLERS);
        if (width < 500) check(scrollers.length === 0, `phone: the document is the only scroller (${scrollers.join(", ") || "none"})`);
        else check(scrollers.length === 1 && scrollers[0] === "div.scroll", `desktop: only the phone frame scrolls (${scrollers.join(", ")})`);
        const panel = await p.ev(`getComputedStyle(document.querySelector('.panel')).display`);
        const strip = await p.ev(`getComputedStyle(document.querySelector('.strip')).display`);
        check(width < 500 ? panel === "none" && strip !== "none" : panel !== "none" && strip === "none",
            `panel ${panel} · strip ${strip}`);

        // a note: Send waits for words, then the name is used
        await p.ev(`location.hash = '#/thanks'`); await sleep(120);
        check(await p.ev(`document.getElementById('send').disabled`) === true, "Send is disabled on an empty note");
        await p.ev(`(() => { const n = document.getElementById('note'); n.value = 'Thank you for the library.';
            n.dispatchEvent(new Event('input', {bubbles:true})); document.getElementById('name').value = 'Sam'; })()`);
        check(await p.ev(`document.getElementById('send').disabled`) === false, "Send is enabled once there are words");
        await p.ev(`document.getElementById('note-form').requestSubmit()`); await sleep(150);
        check(await p.ev(`location.hash`) === "#/sent", "sending opens Note received");
        check(await p.ev(`document.getElementById('sent-title').textContent`) === "Thank you, Sam.", "the note used the name given");
        await p.ev(`location.hash = '#/thanks'`); await sleep(120);
        await p.ev(`document.getElementById('stripe').click()`);
        check(await p.ev(`!document.getElementById('stripe-note').hidden`), "Stripe says plainly nothing is charged");

        // a printed copy: the total moves with the destination
        await p.ev(`location.hash = '#/copy'`); await sleep(120);
        const us = await p.ev(`document.getElementById('c-total').textContent`);
        await p.ev(`(() => { const c = document.getElementById('country'); c.value = 'KH'; c.dispatchEvent(new Event('change')); })()`);
        const kh = await p.ev(`document.getElementById('c-total').textContent`);
        check(us !== kh && /\d/.test(us) && /\d/.test(kh), `the total moves with the destination (${us} → ${kh})`);

        // debate → : lands on the quote and marks it
        await p.ev(`location.hash = '#/debate/2?q=crit'`); await sleep(250);
        const landed = await p.ev(`(() => { const e = document.getElementById('q-crit'); const r = e.getBoundingClientRect();
            return { flash: e.classList.contains('flash'), top: Math.round(r.top) }; })()`);
        check(landed.flash && landed.top > 0 && landed.top < 844, `"debate →" lands on the quote (top ${landed.top}, marked ${landed.flash})`);

        // Back never leaves the site, even when the page opened on an inner screen
        await p.go("about:blank");                          // a FRESH load: a hash-only navigation keeps the page and its history
        await p.go(BASE + "#/story/4");
        await p.ev(`document.getElementById('back').click()`); await sleep(200);
        const after = await p.ev(`location.href`);
        check(after.endsWith("walkthrough.html#/library"), `Back from a page opened on an inner screen stays on the site (${after.split("/").pop()})`);
        await p.ev(`location.hash = '#/book'`); await sleep(100);
        await p.ev(`location.hash = '#/story'`); await sleep(100);
        await p.ev(`document.getElementById('back').click()`); await sleep(250);
        check(await p.ev(`location.hash`) === "#/book", "Back returns to the previous screen");

        check(p.errors.length === 0, `no exceptions or console errors (${p.errors.join(" | ") || "none"})`);
        await send("Target.closeTarget", { targetId: p.targetId });
    }
} finally {
    try { ws?.close(); } catch {}
    chrome.kill(); server.kill();
    await sleep(300);
    rmSync(profile, { recursive: true, force: true });
}
console.log(failures.length ? `\n${failures.length} FAILURE(S)` : "\nall checks passed");
process.exit(failures.length ? 1 : 0);
