// Measure every artboard in headless Chrome and write its real height into canvas.json.
//
//     node measure.mjs
//
// WHY. The wall shows each board in an iframe of the height canvas.json records, with scrolling off.
// A guessed height clips the bottom of a screen or leaves a gap under it, and nothing reports either.
// Measured, the number cannot be wrong for long: re-run after any change to build-boards.py.
//
// It also FAILS on the two layout defects a phone-width screen hides best:
//   · sideways overflow — the document is wider than the board's design width
//   · a nested scroll container — any element whose overflow is not visible/clip (the /build rule:
//     on a phone the DOCUMENT is the only scroller; overflow:hidden counts, and breaks sticky)
//
// No dependencies: Node 22's own WebSocket speaks the DevTools protocol to Chrome directly.

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { spawn } from "node:child_process";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9339;
const canvasPath = join(HERE, "canvas.json");
const canvas = JSON.parse(readFileSync(canvasPath, "utf8"));
const only = process.argv.slice(2);

const profile = mkdtempSync(join(tmpdir(), "measure-"));
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars",
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "about:blank"],
    { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, seq = 0;
const pending = new Map(), listeners = [];

async function connect() {
    for (let i = 0; i < 50; i++) {
        try {
            const v = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
            ws = new WebSocket(v.webSocketDebuggerUrl);
            await new Promise((ok, bad) => { ws.onopen = ok; ws.onerror = bad; });
            ws.onmessage = (m) => {
                const d = JSON.parse(m.data);
                if (d.id && pending.has(d.id)) {
                    const { ok, bad } = pending.get(d.id);
                    pending.delete(d.id);
                    d.error ? bad(new Error(d.error.message)) : ok(d.result);
                } else if (d.method) listeners.forEach((f) => f(d));
            };
            return;
        } catch { await sleep(200); }
    }
    throw new Error("Chrome's DevTools endpoint never answered");
}

function send(method, params = {}, sessionId) {
    const id = ++seq;
    ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    return new Promise((ok, bad) => pending.set(id, { ok, bad }));
}

function once(method, sessionId, timeout = 20000) {
    return new Promise((ok, bad) => {
        const t = setTimeout(() => bad(new Error(`timed out waiting for ${method}`)), timeout);
        const f = (d) => {
            if (d.method === method && d.sessionId === sessionId) {
                clearTimeout(t);
                listeners.splice(listeners.indexOf(f), 1);
                ok(d.params);
            }
        };
        listeners.push(f);
    });
}

const PROBE = `document.fonts.ready.then(() => JSON.stringify({
  h: Math.ceil(document.documentElement.scrollHeight),
  sw: Math.ceil(document.documentElement.scrollWidth),
  // svg and form fields are scroll containers by their nature (UA stylesheet) and cannot host a
  // sticky page element, so they are not the defect this probe hunts.
  scrollers: [...document.querySelectorAll('*')].filter(e => {
      if (e.closest('svg') || /^(textarea|select|input)$/i.test(e.tagName)) return false;
      const s = getComputedStyle(e);
      return !/^(visible|clip)$/.test(s.overflowY) || !/^(visible|clip)$/.test(s.overflowX);
  }).map(e => e.tagName.toLowerCase() + (e.getAttribute('class') ? '.' + e.getAttribute('class').split(' ').join('.') : ''))
}))`;

let failures = 0;
try {
    await connect();
    for (const a of canvas.artboards) {
        if (only.length && !only.includes(a.file)) continue;
        const { targetId } = await send("Target.createTarget", { url: "about:blank" });
        const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
        await send("Page.enable", {}, sessionId);
        // A SHORT viewport: scrollHeight never reads less than the viewport, so a tall one would report
        // every short board as exactly the viewport's height.
        await send("Emulation.setDeviceMetricsOverride",
            { width: a.w, height: 100, deviceScaleFactor: 1, mobile: false }, sessionId);
        const loaded = once("Page.loadEventFired", sessionId);
        await send("Page.navigate", { url: "file://" + join(HERE, a.file) }, sessionId);
        await loaded;
        const r = await send("Runtime.evaluate",
            { expression: PROBE, awaitPromise: true, returnByValue: true }, sessionId);
        const m = JSON.parse(r.result.value);
        const notes = [];
        if (m.sw > a.w) { notes.push(`⛔ ${m.sw - a.w}px wider than ${a.w}`); failures++; }
        if (m.scrollers.length) { notes.push(`⛔ scroll containers: ${m.scrollers.join(", ")}`); failures++; }
        const moved = a.h !== m.h ? `${a.h} → ${m.h}` : `${m.h}`;
        a.h = m.h;
        console.log(`${a.file.padEnd(24)} ${String(a.w).padStart(4)} × ${moved.padEnd(12)} ${notes.join("  ")}`);
        await send("Target.closeTarget", { targetId });
    }
    writeFileSync(canvasPath, JSON.stringify(canvas, null, 2) + "\n");
    console.log(failures ? `\n${failures} layout defect(s) — fix before publishing.` : "\nheights written; no layout defects.");
} finally {
    try { ws?.close(); } catch {}
    chrome.kill();
    await sleep(300);
    rmSync(profile, { recursive: true, force: true });
}
process.exit(failures ? 1 : 0);
