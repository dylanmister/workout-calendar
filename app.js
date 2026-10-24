/* The White Lotus Training Arc: plain JavaScript, no backend. All progress lives in localStorage. */
(() => {
  "use strict";

  const STORE_KEY = "wlta-v1";
  const APP_ID = "white-lotus-training-arc";
  const DAY_MS = 864e5;
  const ELEMENTS = { earth: "Earth", water: "Water", fire: "Fire", air: "Air" };
  const SHORT_FOCUS = { earth: "Legs", water: "Back", fire: "Push", air: "Rest" };
  const LOADING = ["Brewing a pot of jasmine tea…", "Consulting the Pai Sho masters…", "Aligning the four elements…",
    "Sokka is drawing the map. It has a lot of arrows.", "Rebuilding the cabbage cart…"];

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const rand = (a, b) => Math.round(a + Math.random() * (b - a));
  const icon = (id, cls = "icon") => `<svg class="${cls}" aria-hidden="true"><use href="#${id}"/></svg>`;
  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
  const reducedMotion = () => window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  let D = null; // program data
  let S = null; // saved state
  let H = null; // humor strings
  let todayOverride = null;
  let calCache = null;
  let lastRenderedToday = null;
  const openLogs = new Set();

  // ------------------------------------------------------------------ dates (UTC day numbers, local "today")
  const toNum = (iso) => { const [y, m, d] = iso.split("-").map(Number); return Math.round(Date.UTC(y, m - 1, d) / DAY_MS); };
  const toISO = (n) => new Date(n * DAY_MS).toISOString().slice(0, 10);
  const localISO = (dt = new Date()) => `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
  const todayISO = () => todayOverride || localISO();
  const todayNum = () => toNum(todayISO());
  const fmt = (iso, opts) => new Date(toNum(iso) * DAY_MS).toLocaleDateString(undefined, { timeZone: "UTC", ...opts });
  const fmtLong = (iso) => fmt(iso, { weekday: "long", month: "long", day: "numeric", year: "numeric" });
  const fmtShort = (iso) => fmt(iso, { weekday: "short", month: "short", day: "numeric" });
  const fmtMed = (iso) => fmt(iso, { month: "short", day: "numeric", year: "numeric" });

  // ------------------------------------------------------------------ state
  const blankState = () => ({ v: 1, checks: {}, done: {}, logs: {}, notes: {}, supps: {}, shifts: [], settings: { unit: "lb" } });
  const isObj = (x) => x && typeof x === "object" && !Array.isArray(x);
  const total = () => D.days.length;

  function sanitize(o) {
    if (!isObj(o)) return null;
    if (!("checks" in o || "logs" in o || "shifts" in o || "done" in o)) return null;
    const out = blankState();
    const day = (k) => { const n = Number(k); return Number.isInteger(n) && n >= 1 && n <= total() ? n : 0; };
    const KEY = /^\d{1,2}\.\d{1,2}$/;
    const DATE = /^\d{4}-\d{2}-\d{2}$/;
    for (const [d, m] of Object.entries(isObj(o.checks) ? o.checks : {})) {
      const n = day(d);
      if (!n || !isObj(m)) continue;
      const keys = Object.keys(m).filter((k) => KEY.test(k) && m[k]);
      if (keys.length) out.checks[n] = Object.fromEntries(keys.map((k) => [k, 1]));
    }
    for (const [d, v] of Object.entries(isObj(o.done) ? o.done : {})) {
      const n = day(d);
      if (n) out.done[n] = typeof v === "string" ? v.slice(0, 40) : new Date().toISOString();
    }
    for (const [d, m] of Object.entries(isObj(o.logs) ? o.logs : {})) {
      const n = day(d);
      if (!n || !isObj(m)) continue;
      for (const [k, rec] of Object.entries(m)) {
        if (!KEY.test(k) || !isObj(rec) || typeof rec.ex !== "string" || !Array.isArray(rec.s)) continue;
        const s = rec.s.slice(0, 12).map((x) => (Array.isArray(x) ? [String(x[0] ?? "").slice(0, 8), String(x[1] ?? "").slice(0, 8)] : ["", ""]));
        if (!s.some((x) => x[0] || x[1])) continue;
        (out.logs[n] ||= {})[k] = { ex: rec.ex.slice(0, 60), u: rec.u === "kg" ? "kg" : "lb", s, t: Number(rec.t) || 0 };
      }
    }
    for (const [d, v] of Object.entries(isObj(o.notes) ? o.notes : {})) {
      const n = day(d);
      if (n && typeof v === "string" && v.trim()) out.notes[n] = v.slice(0, 4000);
    }
    for (const [iso, v] of Object.entries(isObj(o.supps) ? o.supps : {})) { // keyed by calendar date: supplements are daily, so a pushed workout doesn't carry them along
      if (!v || !DATE.test(iso)) continue;
      const dn = toNum(iso);
      if (toISO(dn) === iso && dn >= startNum() && dn < startNum() + total() + 400) out.supps[iso] = 1;
    }
    if (Array.isArray(o.shifts)) out.shifts = o.shifts.map(Number).filter((n) => Number.isInteger(n) && n >= 1 && n <= total()).slice(0, 400);
    if (isObj(o.settings) && (o.settings.unit === "kg" || o.settings.unit === "lb")) out.settings.unit = o.settings.unit;
    return out;
  }

  function reconcile(st) { // "done" always mirrors a fully checked day
    for (const n of Object.keys(st.done)) if (checkedCount(+n, st) < D.totals[n]) delete st.done[n];
    for (const n of Object.keys(st.checks)) if (checkedCount(+n, st) >= D.totals[n] && !st.done[n]) st.done[n] = new Date().toISOString();
    return st;
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (raw) { const s = sanitize(JSON.parse(raw)); if (s) return reconcile(s); }
    } catch (e) { console.warn("[WLTA] could not read saved state", e); }
    return blankState();
  }

  let saveTimer = null;
  let storageWarned = false;
  function save(now = false, cloud = true) {
    clearTimeout(saveTimer);
    const write = () => {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(S)); storageWarned = false; } catch (e) {
        if (!storageWarned) toast("This browser blocked saving. Use Export to keep a backup of your progress.");
        storageWarned = true;
      }
    };
    if (now) write(); else saveTimer = setTimeout(write, 250);
    if (cloud) syncSoon();
  }

  // ------------------------------------------------------------------ cloud sync (Convex)
  // Progress is saved here first (so the app works offline), then synced to Convex under a private sync code.
  // Each save names the cloud revision it started from; if another device saved first, the two copies are merged.
  let CONVEX_URL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) ? "http://127.0.0.1:3210" : "";
  const SYNC_KEY = "wlta-sync";
  const CODE_RE = /^lotus(-[a-z2-7]{4}){4}$/;
  const sync = { code: "", rev: 0, dirty: false, off: false, at: 0 };
  let syncState = "idle", syncError = "", syncBusy = false, syncAgain = false, syncTimer = null, changeSeq = 0, refreshPending = false;

  const syncOn = () => !!(CONVEX_URL && sync.code && !sync.off);
  const saveSync = () => { try { localStorage.setItem(SYNC_KEY, JSON.stringify(sync)); } catch (e) { /* storage blocked: sync still works this session */ } };
  function newCode() { // 16 random base32 characters: 80 bits, far too many to guess
    const abc = "abcdefghijklmnopqrstuvwxyz234567";
    const s = [...crypto.getRandomValues(new Uint8Array(16))].map((b) => abc[b & 31]).join("");
    return `lotus-${s.slice(0, 4)}-${s.slice(4, 8)}-${s.slice(8, 12)}-${s.slice(12)}`;
  }
  function normalizeCode(input) { // forgiving about case, spaces, dashes and 0/1/8 look-alikes (even in "L0TUS")
    let s = String(input).toLowerCase().replace(/0/g, "o").replace(/1/g, "l").replace(/8/g, "b").replace(/[^a-z2-7]/g, "");
    if (s.length === 21 && s.startsWith("lotus")) s = s.slice(5);
    return s.length === 16 ? `lotus-${s.slice(0, 4)}-${s.slice(4, 8)}-${s.slice(8, 12)}-${s.slice(12)}` : "";
  }
  function loadSync() {
    if (!CONVEX_URL) return;
    try { const s = JSON.parse(localStorage.getItem(SYNC_KEY)); if (isObj(s)) Object.assign(sync, s); } catch (e) { /* nothing saved yet */ }
    if (window.WLTA_ACCOUNT) {
      if (!sync.account) Object.assign(sync, { code:"lotus-aaaa-aaaa-aaaa-aaaa", rev:0, dirty:!!(Object.keys(S.checks).length || Object.keys(S.logs).length || Object.keys(S.notes).length || Object.keys(S.supps).length || S.shifts.length), at:0 });
      Object.assign(sync, {account:true,off:false});saveSync();return;
    }
    if (!CODE_RE.test(sync.code)) sync.code = "";
    if (!sync.code && !sync.off) { Object.assign(sync, { code: newCode(), rev: 0, dirty: true }); saveSync(); }
  }

  async function convex(kind, path, args) { // Convex's HTTP API: POST /api/query or /api/mutation
    if (window.WLTA_ACCOUNT) {
      const response=await fetch('/api/progress',kind==='query'?{cache:'no-store'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({baseRev:args.baseRev,state:args.state})});
      const result=await response.json();
      if(response.status===401){location.reload();throw new Error('Please sign in again.');}
      if(!response.ok)throw new Error(result.error||'Cloud progress is unavailable.');
      return result;
    }
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 12000);
    try {
      const r = await fetch(`${CONVEX_URL}/api/${kind}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, args, format: "json" }), signal: ctl.signal,
      });
      const j = await r.json().catch(() => ({}));
      if (j.status === "success") return j.value;
      throw Object.assign(new Error(typeof j.errorData === "string" ? j.errorData : (j.errorMessage || `HTTP ${r.status}`).split("\n")[0]), { server: true });
    } finally { clearTimeout(timer); }
  }

  function mergeStates(mine, theirs) { // keeps the work from both copies; where both changed the same thing, this device wins
    const m = JSON.parse(JSON.stringify(mine));
    for (const [n, keys] of Object.entries(theirs.checks)) m.checks[n] = { ...keys, ...m.checks[n] };
    for (const [n, items] of Object.entries(theirs.logs)) {
      const day = (m.logs[n] ||= {});
      for (const [k, rec] of Object.entries(items)) if (!day[k] || rec.t > day[k].t) day[k] = rec;
    }
    for (const [n, text] of Object.entries(theirs.notes)) m.notes[n] ||= text;
    for (const iso of Object.keys(theirs.supps)) m.supps[iso] = 1;
    for (const [n, at] of Object.entries(theirs.done)) m.done[n] ||= at;
    if (theirs.shifts.length > m.shifts.length) m.shifts = [...theirs.shifts];
    return m;
  }
  function takeRemote(json, merge) {
    let r = null;
    try { r = sanitize(JSON.parse(json)); } catch (e) { /* unreadable copy: keep ours */ }
    if (!r) return;
    S = reconcile(merge ? mergeStates(S, r) : r);
    calCache = null;
    save(true, false);
    refreshView();
  }
  function refreshView() { // show another device's changes without yanking the page away mid-edit
    const a = document.activeElement;
    if ((a && a.matches("#view input, #view textarea")) || !$("#lightbox").hidden || !$("#celebrate").hidden || !$("#modal").hidden) { refreshPending = true; return; }
    refreshPending = false;
    const y = scrollY;
    route();
    scrollTo(0, y);
  }

  async function pull() {
    const code = sync.code;
    const remote = await convex("query", "progress:get", { code });
    if (code !== sync.code) return; // switched codes mid-request
    if (!remote) { sync.dirty = true; return; } // nothing under this code yet: upload ours
    if (remote.rev === sync.rev) return;
    const merge = sync.dirty || remote.rev < sync.rev;
    sync.rev = remote.rev;
    takeRemote(remote.state, merge);
    if (merge) sync.dirty = true;
    saveSync();
  }
  async function push() {
    for (let tries = 0; tries < 5; tries++) {
      const code = sync.code, seq = changeSeq;
      const res = await convex("mutation", "progress:save", { code, baseRev: sync.rev, state: JSON.stringify(S) });
      if (code !== sync.code) return;
      sync.rev = res.rev;
      if (res.ok) { if (seq === changeSeq) sync.dirty = false; saveSync(); return; }
      takeRemote(res.state, true); // another device saved first: fold its work into ours and try again
    }
    throw new Error("Other devices keep saving at the same moment. Trying again soon.");
  }
  async function syncNow() {
    clearTimeout(syncTimer);
    if (!syncOn()) return;
    if (syncBusy) { syncAgain = true; return; }
    syncBusy = true;
    setSyncState("syncing");
    try {
      do {
        syncAgain = false;
        if (!sync.dirty) await pull();
        if (sync.dirty) await push();
      } while (syncAgain);
      sync.at = Date.now();
      saveSync();
      setSyncState("synced");
    } catch (e) {
      setSyncState(e.server ? "error" : "offline", e.message);
      if (sync.dirty) syncTimer = setTimeout(syncNow, 30000); // keep trying while changes are waiting
    } finally {
      syncBusy = false;
    }
  }
  function syncSoon() { // every local change lands here
    changeSeq++;
    if (!syncOn()) return;
    sync.dirty = true;
    saveSync();
    clearTimeout(syncTimer);
    syncTimer = setTimeout(syncNow, 1200);
  }
  function startSync() {
    if (!CONVEX_URL) return;
    const nudge = () => { if (sync.dirty || Date.now() - sync.at > 5000) syncNow(); };
    document.addEventListener("visibilitychange", nudge); // pull when the app comes back, push as it goes away
    window.addEventListener("focus", nudge);
    window.addEventListener("online", nudge);
    document.addEventListener("focusout", () => { if (refreshPending) setTimeout(refreshView, 0); });
    setInterval(() => { if (document.visibilityState === "visible") nudge(); }, 10000);
    syncNow();
  }

  function setSyncState(state, error = "") {
    syncState = state;
    syncError = error;
    const el = $("#sync-status");
    if (el) el.textContent = syncStatusText();
  }
  function syncStatusText() {
    if (!syncOn()) return "Off on this device. Progress is saved here only.";
    if (syncState === "syncing") return "Syncing…";
    if (syncState === "offline") return sync.dirty ? "Offline. Your changes are safe here and will sync when you're back online." : "Offline. Will sync when you're back online.";
    if (syncState === "error") return `Couldn't sync: ${syncError}`;
    if (!sync.at) return "Not synced yet.";
    const min = Math.round((Date.now() - sync.at) / 60000);
    return `Synced ${min < 1 ? "just now" : min < 90 ? `${min} min ago` : new Date(sync.at).toLocaleString()}.`;
  }
  async function linkCode(input) {
    const code = normalizeCode(input);
    if (!code) { toast("That doesn't look like a sync code. It starts with LOTUS and has 16 letters and digits after it."); return; }
    if (code === sync.code && !sync.off) { toast("This device already uses that code."); return; }
    let remote;
    try { remote = await convex("query", "progress:get", { code }); } catch (e) {
      toast(e.server ? `Couldn't check that code: ${e.message}` : "You're offline. Connect and try again.");
      return;
    }
    if (!remote) { toast("Nothing is saved under that code. Check it and try again."); return; }
    const ok = await confirmModal({ title: "Link this device?", body: `This device will sync with ${code.toUpperCase()}. Progress already on this device is merged in, so nothing is lost.`, ok: "Link device" });
    if (!ok) return;
    Object.assign(sync, { code, rev: remote.rev, off: false, dirty: true });
    saveSync();
    takeRemote(remote.state, true);
    toast("Linked. This device now shares that progress.");
    syncNow();
  }
  function setSyncOff(off) {
    sync.off = off;
    if (!off) { if (!sync.code) Object.assign(sync, { code: newCode(), rev: 0 }); sync.dirty = true; }
    saveSync();
    renderMore();
    if (off) toast("Sync is off on this device. The cloud copy is kept."); else syncNow();
  }
  async function copyCode() {
    try { await navigator.clipboard.writeText(sync.code.toUpperCase()); toast("Sync code copied."); } catch (e) {
      getSelection().selectAllChildren($("#sync-code"));
      toast("Select the code and copy it.");
    }
  }
  async function awaitSyncThenSignOut() {
    await syncNow();
    const deadline=Date.now()+15000;
    while(syncBusy&&Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,100));
    if(sync.dirty){toast('Your latest changes have not reached the cloud yet. Please wait for sync before signing out.');return;}
    await window.WLTA_SIGN_OUT();
  }

  // ------------------------------------------------------------------ schedule with shifts
  const startNum = () => toNum(D.program.start);
  const shiftsBefore = (n) => S.shifts.reduce((c, s) => c + (s <= n ? 1 : 0), 0);
  const dateNumOf = (n) => startNum() + (n - 1) + shiftsBefore(n);
  const dateOf = (n) => toISO(dateNumOf(n));
  const endNum = () => dateNumOf(total());
  function calMap() {
    if (!calCache) { calCache = new Map(); for (let n = 1; n <= total(); n++) calCache.set(dateNumOf(n), n); }
    return calCache;
  }
  function entryAt(dn) {
    if (dn < startNum() || dn > endNum()) return null;
    const n = calMap().get(dn);
    return n ? { type: "w", n } : { type: "gap" };
  }
  function nextWorkoutFrom(dn) { for (let d = dn; d <= endNum(); d++) { const n = calMap().get(d); if (n) return n; } return null; }
  function todayInfo() {
    const tn = todayNum();
    if (tn < startNum()) return { state: "before", daysTo: startNum() - tn };
    if (tn > endNum()) return { state: "after" };
    const e = entryAt(tn);
    return e.type === "w" ? { state: "workout", n: e.n } : { state: "gap", next: nextWorkoutFrom(tn) };
  }
  const phaseOf = (id) => D.program.phases.find((p) => p.id === id);

  // ------------------------------------------------------------------ progress helpers
  const checkedCount = (n, st = S) => (st.checks[n] ? Object.keys(st.checks[n]).length : 0);
  const isDone = (n) => !!S.done[n];
  const doneCount = () => Object.keys(S.done).length;
  function streakInfo() {
    const tn = todayNum();
    const last = Math.min(tn, endNum());
    let run = 0, best = 0;
    for (let d = startNum(); d <= last; d++) {
      const n = calMap().get(d);
      if (!n) continue; // pushed rest days neither count nor break
      if (isDone(n)) { run++; best = Math.max(best, run); } else if (d !== tn) run = 0;
    }
    return { current: run, best };
  }
  function streakLine(cur) {
    let line = H.streak[0][1];
    for (const [min, txt] of H.streak) if (cur >= min) line = txt;
    return line;
  }
  function lastLog(exId, beforeN) {
    let best = null;
    for (const [dn, items] of Object.entries(S.logs)) {
      const d = Number(dn);
      if (d >= beforeN) continue;
      for (const rec of Object.values(items)) {
        if (rec.ex === exId && rec.s.some((x) => x[0] || x[1]) && (!best || d > best.day)) best = { ...rec, day: d };
      }
    }
    return best;
  }
  function setsText(rec) {
    const parts = rec.s.filter((x) => x[0] || x[1]).map(([w, r]) => (w ? `${w}×${r || "?"}` : `${r} reps`));
    const hasW = rec.s.some((x) => x[0]);
    return parts.join(" · ") + (hasW ? ` ${rec.u}` : "");
  }

  // ------------------------------------------------------------------ toast & modal
  let toastTimer = null;
  function toast(msg, opt = {}) {
    const t = $("#toast");
    t.innerHTML = `<span>${esc(msg)}</span>${opt.undo ? `<button type="button" data-action="undo">Undo</button>` : ""}`;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), opt.undo ? 6500 : 3400);
  }
  function confirmModal({ title, body, ok = "Confirm", danger = false }) {
    return new Promise((resolve) => {
      const m = $("#modal");
      m.innerHTML = `<div class="modal-card"><h2 id="modal-title">${esc(title)}</h2><p>${esc(body)}</p>
        <div class="btn-row"><button type="button" class="btn" data-m="no">Cancel</button>
        <button type="button" class="btn ${danger ? "btn-danger" : "btn-primary"}" data-m="yes">${esc(ok)}</button></div></div>`;
      m.hidden = false;
      const finish = (v) => { m.hidden = true; m.innerHTML = ""; m.removeEventListener("click", onClick); document.removeEventListener("keydown", onKey); resolve(v); };
      const onClick = (e) => { const b = e.target.closest("[data-m]"); if (b) finish(b.dataset.m === "yes"); else if (e.target === m) finish(false); };
      const onKey = (e) => { if (e.key === "Escape") finish(false); };
      m.addEventListener("click", onClick);
      document.addEventListener("keydown", onKey);
      $('[data-m="yes"]', m).focus();
    });
  }

  // ------------------------------------------------------------------ element scenes (decorative, animated in CSS)
  const SCENES = {
    earth: `<svg viewBox="0 0 200 150" preserveAspectRatio="xMaxYMax meet"><path class="mountain m2" d="M30 150 110 46l38 54 22-28 50 78z"/><path class="mountain" d="M70 150l58-70 40 46 22-24 40 48z"/>
      <polygon class="rock" points="118,34 140,28 152,44 138,58 116,52"/><polygon class="rock r2" points="160,10 176,6 186,20 174,30 158,25"/>
      <polygon class="rock r3" points="90,64 104,60 110,72 98,80 88,75"/><path class="grass" d="M58 148q4-10 8 0M150 148q4-12 8 0M176 148q3-8 6 0"/></svg>`,
    water: `<svg viewBox="0 0 200 150" preserveAspectRatio="xMaxYMax meet"><path class="drop" d="M150 22c5 7 8 11 8 15a8 8 0 0 1-16 0c0-4 3-8 8-15z"/>
      <path class="wave w2" d="M0 92q20-16 40 0t40 0 40 0 40 0 40 0 40 0 40 0"/><path class="wave" d="M0 112q20-16 40 0t40 0 40 0 40 0 40 0 40 0 40 0"/>
      <path class="wave w3" d="M0 132q20-16 40 0t40 0 40 0 40 0 40 0 40 0 40 0"/></svg>`,
    fire: `<svg viewBox="0 0 200 150" preserveAspectRatio="xMaxYMax meet"><path class="flame f1" d="M128 150c-34-24-28-58-8-86 3 20 13 25 18 9 22 26 38 55 18 77z"/>
      <path class="flame f2" d="M134 150c-20-18-16-42-4-60 3 14 10 18 14 6 12 18 18 40 6 54z"/><path class="flame f3" d="M140 150c-10-12-8-26 0-36 3 9 8 11 10 4 7 12 8 24 1 32z"/>
      <circle class="ember" cx="128" cy="58" r="2.6"/><circle class="ember e2" cx="152" cy="76" r="2.2"/><circle class="ember e3" cx="112" cy="86" r="2"/></svg>`,
    air: `<svg viewBox="0 0 200 150" preserveAspectRatio="xMaxYMax meet"><path class="swirl" d="M150 58c0-7 11-7 11 1 0 11-19 12-19-2 0-17 27-18 27 3 0 22-34 23-34-2"/>
      <path class="swirl s2" d="M104 98c0-5 8-5 8 1 0 8-14 9-14-1 0-13 20-13 20 2"/><path class="swirl s3" d="M176 112c0-4 6-4 6 1 0 6-10 7-10-1 0-9 15-10 15 1"/>
      <path class="breeze" d="M70 128h58q12 0 12-10"/><path class="breeze" d="M96 140h70" style="animation-delay:-2s"/></svg>`,
  };

  // ------------------------------------------------------------------ rendering: shared bits
  const view = () => $("#view");
  function setView(html, { el = null, top = true, title = null } = {}) {
    const v = view();
    v.innerHTML = html;
    document.body.dataset.el = el || "";
    if (title) document.title = `${title} · The White Lotus Training Arc`;
    if (top) window.scrollTo(0, 0);
  }
  function setNav(name) { $$("[data-nav]").forEach((a) => { if (a.dataset.nav === name) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); }); }

  function locChip(loc) {
    const id = loc === "Sand" ? "i-sand" : loc === "Gym" ? "i-gym" : "i-sand";
    return `<span class="chip">${icon(id)}${esc(loc)}</span>`;
  }
  function doseHTML(it) {
    if (it.sets) {
      let s = `<b>${it.sets} × ${esc(it.reps)}</b>`;
      if (it.load) s += ` · ${esc(it.load)}`;
      if (it.rest) s += it.rest.startsWith("→") ? ` · then ${esc(it.rest.slice(1).trim())}` : ` · rest ${esc(it.rest)}`;
      return s;
    }
    return `<b>${esc(it.dose)}</b>`;
  }
  function scrollCard(n, el) {
    const m = D.content.daily[n - 1];
    const q = D.content.quotes[m.quote];
    return `<section class="scroll" aria-label="Daily wisdom">
      <div class="quote"><span class="portrait" data-el="${el}">${icon(`el-${el}`)}</span>
        <div><p class="quote-text">“${esc(q.text)}”</p><div class="quote-who">${esc(q.character)}</div>
        <div class="quote-tone">${q.tone === "wise" ? "Words of wisdom" : "Words of… something"}</div></div></div>
    </section>`;
  }

  function itemHTML(n, bi, ii, it, kind) {
    const ex = D.ex[it.id];
    const key = `${bi}.${ii}`;
    const checked = !!(S.checks[n] && S.checks[n][key]);
    const loggable = !!it.log;
    const rec = S.logs[n] && S.logs[n][key];
    const small = kind === "warmup" || kind === "cooldown";
    const notes = [it.note, it.ramp ? "Ramp up with 3–4 lighter sets first." : ""].filter(Boolean).join(" ");
    const open = openLogs.has(`${n}:${key}`);
    return `<li class="ex${checked ? " done" : ""}${small ? " small-item" : ""}" data-key="${key}">
      <button type="button" class="ex-img" data-action="img" data-id="${esc(it.id)}" aria-label="View larger image of ${esc(ex.name)}">
        <img src="${esc(ex.thumb)}" alt="" loading="lazy" decoding="async" width="360" height="240"></button>
      <div class="ex-body">
        <div class="ex-title">${it.tag ? `<span class="tag">${esc(it.tag)}</span>` : ""}${esc(ex.name)}</div>
        <div class="ex-dose">${doseHTML(it)}</div>
        ${notes ? `<div class="ex-note">${esc(notes)}</div>` : ""}
        <div class="ex-cue">${esc(it.cue)}</div>
        ${loggable ? `<div class="log-toggle"><button type="button" class="btn btn-sm" data-action="log" aria-expanded="${open}" aria-controls="log-${n}-${key}">${icon("i-pencil")}${open ? "Hide log" : "Log sets"}</button>
          <span class="log-summary">${rec ? `Logged: <b>${esc(setsText(rec))}</b>` : ""}</span></div>` : ""}
      </div>
      <button type="button" class="tile" data-action="check" aria-pressed="${checked}" aria-label="Mark ${esc(ex.name)} complete"><svg aria-hidden="true"><use href="#lotus"/></svg></button>
      ${loggable && open ? logPanelHTML(n, key, it) : ""}
    </li>`;
  }

  function repTarget(reps) { const m = String(reps).match(/\d+/); return m ? m[0] : ""; }
  function repUnit(reps) { return /\d\s*s\b/.test(reps) ? "sec" : /\d\s*m\b/.test(reps) ? "m" : "reps"; }
  function logPanelHTML(n, key, it) {
    const rec = S.logs[n] && S.logs[n][key];
    const last = lastLog(it.id, n);
    const unit = rec ? rec.u : S.settings.unit;
    const rows = [];
    for (let i = 0; i < it.sets; i++) {
      const w = rec && rec.s[i] ? rec.s[i][0] : "";
      const r = rec && rec.s[i] ? rec.s[i][1] : "";
      const pw = last && last.s[i] && last.s[i][0] ? last.s[i][0] : "";
      const pr = last && last.s[i] && last.s[i][1] ? last.s[i][1] : repTarget(it.reps);
      rows.push(`<div class="log-row"><span class="set-n" aria-hidden="true">${i + 1}</span>
        <label><input data-set="${i}" data-f="w" inputmode="decimal" autocomplete="off" value="${esc(w)}" placeholder="${esc(pw || "–")}" aria-label="Set ${i + 1} weight in ${unit}"><span class="unit">${unit}</span></label>
        <span class="times" aria-hidden="true">×</span>
        <label><input data-set="${i}" data-f="r" inputmode="numeric" autocomplete="off" value="${esc(r)}" placeholder="${esc(pr)}" aria-label="Set ${i + 1} ${repUnit(it.reps)}"><span class="unit">${repUnit(it.reps)}</span></label></div>`);
    }
    const lastLine = last
      ? `Last time · Day ${last.day} (${esc(fmtShort(dateOf(last.day)))}): <b>${esc(setsText(last))}</b>. Beat it.`
      : esc(H.empty.firstTime);
    return `<div class="log" id="log-${n}-${key}" data-n="${n}" data-key="${key}">
      <div class="log-last">${lastLine}</div>${rows.join("")}
      <div class="log-foot"><span>Faded numbers show last time${last ? "" : " (or the target reps)"}.</span>
      ${last ? `<button type="button" class="btn btn-sm btn-ghost" data-action="fill-last">Copy last time</button>` : ""}</div></div>`;
  }

  function blockHTML(n, b, bi) {
    return `<section class="block" data-bi="${bi}">
      <div class="block-head"><h2>${esc(b.title)}</h2><div class="meta">${locChip(b.where)}<span class="chip">${icon("i-clock")}${b.minutes} min</span></div></div>
      ${b.note ? `<div class="block-note">${esc(b.note)}</div>` : ""}
      <ol class="ex-list">${b.items.map((it, ii) => itemHTML(n, bi, ii, it, b.kind)).join("")}</ol></section>`;
  }

  function progressHTML(n) {
    const c = checkedCount(n), t = D.totals[n];
    return `<div class="day-progress" id="day-progress"><span>${c} / ${t}</span><div class="bar" aria-hidden="true"><span style="width:${(100 * c / t).toFixed(1)}%"></span></div><span>${Math.round(100 * c / t)}%</span></div>`;
  }
  function masteredHTML(n) {
    const day = D.days[n - 1];
    return isDone(n) ? `<div class="mastered-banner" id="mastered">You have mastered ${ELEMENTS[day.element]} today.</div>` : `<div id="mastered"></div>`;
  }
  function suppsHTML(iso) { // its own yes/no, separate from the workout checklist, so it never changes a day's mastery
    const on = !!S.supps[iso];
    return `<section class="card supplements"><h2 class="eyebrow">Supplement checklist</h2>
      <button type="button" class="supp-toggle" data-action="supps" data-iso="${iso}" aria-pressed="${on}">
        <span class="supp-box" aria-hidden="true">${icon("i-check")}</span><span class="supp-label">Took supplements</span>
        <span class="supp-state" aria-hidden="true">${on ? "Yes" : "No"}</span></button></section>`;
  }

  // ------------------------------------------------------------------ views
  function renderDay(n, opts = {}) {
    const day = D.days[n - 1];
    const el = day.element;
    const iso = dateOf(n);
    const isToday = toNum(iso) === todayNum();
    const phase = phaseOf(day.phase);
    const shifts = S.shifts.length;
    const done = isDone(n);
    const actions = [];
    if (!done) actions.push(`<button type="button" class="btn btn-sm" data-action="push" data-n="${n}">${icon("i-push")}${isToday ? "Can't train today? Push it back a day" : "Push this workout back a day"}</button>`);
    if (shifts) actions.push(`<button type="button" class="btn btn-sm btn-ghost" data-action="undo">${icon("i-undo")}Undo last shift</button>`);
    if (!isToday) actions.push(`<a class="btn btn-sm btn-ghost" href="#/today">${icon("i-today")}Jump to today</a>`);
    const shiftNote = shifts ? `<div class="shift-note">Schedule shifted <strong>+${shifts} day${shifts > 1 ? "s" : ""}</strong> · the arc now ends <strong>${esc(fmtMed(toISO(endNum())))}</strong></div>` : "";
    const sandTip = day.location !== "Gym" ? `<div class="sand-tip">${icon("i-sand")} No court today, or it's frozen? Turf or a gym floor works; keep the intent.</div>` : "";
    setView(`<div class="wrap" data-el="${el}"><div class="day-layout">
      <aside class="day-side">
        <section class="banner" data-el="${el}" aria-labelledby="day-title">
          <div class="scene" aria-hidden="true">${SCENES[el]}</div>
          <div class="banner-text">
            <div class="el-line eyebrow">${icon(`el-${el}`)} ${ELEMENTS[el]} · ${esc(day.focus)}</div>
            <h1 id="day-title">${esc(day.title)}</h1>
            <div class="date-line">${esc(fmtLong(iso))} · Day ${n} of ${total()}</div>
          </div>
          <div class="chips">
            ${isToday ? `<span class="chip chip-strong">Today</span>` : ""}
            <span class="chip chip-el" title="${esc(phase.blurb)}">Phase ${phase.numeral} · ${esc(phase.name)}</span>
            ${locChip(day.location)}
            <span class="chip">${icon("i-clock")}≈ ${day.minutes} min</span>
            <span class="chip">${esc(day.formatName)}</span>
            ${day.contacts ? `<span class="chip" title="Plyometric foot contacts">≈ ${day.contacts} contacts</span>` : ""}
          </div>
        </section>
        <div class="day-actions">${actions.join("")}${shiftNote}</div>
        ${scrollCard(n, el)}
        <section class="card summary" data-el="${el}">
          <p>${esc(day.summary)}</p>
          <p class="phase-note">${esc(day.phaseNote)}</p>
          ${sandTip}
          ${progressHTML(n)}
          ${masteredHTML(n)}
        </section>
      </aside>
      <div class="day-main" data-n="${n}">
        ${day.blocks.map((b, bi) => blockHTML(n, b, bi)).join("")}
        <section class="card notes" style="margin-top:14px"><label class="eyebrow" for="notes-${n}">Session notes</label>
          <textarea id="notes-${n}" data-action="notes" data-n="${n}" placeholder="${esc(H.empty.notes)}">${esc(S.notes[n] || "")}</textarea></section>
        ${suppsHTML(iso)}
        <nav class="day-nav" aria-label="Other days">
          ${n > 1 ? `<a class="btn" href="#/day/${n - 1}">${icon("i-left")}Day ${n - 1}</a>` : "<span></span>"}
          ${n < total() ? `<a class="btn" href="#/day/${n + 1}">Day ${n + 1}${icon("i-right")}</a>` : "<span></span>"}
        </nav>
      </div></div></div>`, { el, top: opts.top !== false, title: isToday ? "Today" : `Day ${n}` });
    lastRenderedToday = todayISO();
  }

  function renderGap(iso, isToday) {
    const next = nextWorkoutFrom(toNum(iso));
    const nd = next ? D.days[next - 1] : null;
    setView(`<div class="wrap narrow"><section class="card gap-card" data-el="air">
      ${icon("i-tea", "big-icon")}
      <div class="eyebrow">${esc(fmtLong(iso))}${isToday ? " · Today" : ""}</div>
      <h1>${esc(H.empty.gapTitle)}</h1>
      <p>${esc(H.empty.gapText)}</p>
      ${nd ? `<p class="muted">Next up: <strong>Day ${next} · ${ELEMENTS[nd.element]} · ${esc(nd.focus)}</strong><br>${esc(fmtLong(dateOf(next)))}</p>
        <div class="btn-row" style="justify-content:center"><a class="btn btn-primary" href="#/day/${next}">Preview Day ${next}</a>
        ${S.shifts.length ? `<button type="button" class="btn" data-action="undo">${icon("i-undo")}Undo last shift</button>` : ""}</div>` : ""}
      <p class="shift-note" style="margin-top:14px">Schedule shifted <strong>+${S.shifts.length}</strong> · ends ${esc(fmtMed(toISO(endNum())))}</p>
    </section>${suppsHTML(iso)}</div>`, { el: "air", title: "Rest stop" });
    lastRenderedToday = todayISO();
  }

  function renderToday() {
    setNav("today");
    const t = todayInfo();
    if (t.state === "workout") return renderDay(t.n);
    if (t.state === "gap") return renderGap(todayISO(), true);
    if (t.state === "before") {
      setView(`<div class="wrap narrow"><section class="card gap-card">${icon("lotus", "big-icon")}
        <div class="eyebrow">${esc(fmtLong(todayISO()))}</div><h1>The arc approaches</h1>
        <p>${esc(H.empty.beforeStart.replace("{n}", t.daysTo))}</p>
        <p class="muted">Day 1 begins ${esc(fmtLong(D.program.start))}.</p>
        <a class="btn btn-primary" href="#/day/1">Preview Day 1</a></section></div>`, { title: "Today" });
      return;
    }
    const st = streakInfo();
    setView(`<div class="wrap narrow"><section class="card gap-card">${icon("lotus", "big-icon")}
      <div class="eyebrow">${esc(fmtLong(todayISO()))}</div><h1>The arc is complete</h1>
      <p>${esc(H.empty.afterEnd)}</p>
      <p class="muted">${doneCount()} of ${total()} days mastered · best streak ${st.best}</p>
      <div class="btn-row" style="justify-content:center"><a class="btn btn-primary" href="#/progress">See your progress</a><a class="btn" href="#/day/${total()}">Revisit Day ${total()}</a></div></section></div>`, { title: "Today" });
  }

  function renderDate(iso) {
    setNav("calendar");
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) return renderToday();
    const e = entryAt(toNum(iso));
    if (!e) {
      setView(`<div class="wrap narrow"><section class="card gap-card">${icon("i-calendar", "big-icon")}<div class="eyebrow">${esc(fmtLong(iso))}</div>
        <h1>Outside the arc</h1><p>The training arc runs ${esc(fmtMed(D.program.start))} to ${esc(fmtMed(toISO(endNum())))}.</p>
        <a class="btn" href="#/calendar">Back to the calendar</a></section></div>`, { title: "Calendar" });
      return;
    }
    if (e.type === "w") return renderDay(e.n);
    return renderGap(iso, toNum(iso) === todayNum());
  }

  function monthKey(iso) { return iso.slice(0, 7); }
  function renderCalendar(arg) {
    setNav("calendar");
    const first = monthKey(D.program.start), last = monthKey(toISO(endNum()));
    const tk = monthKey(todayISO());
    let ym = /^\d{4}-\d{2}$/.test(arg || "") ? arg : (tk >= first && tk <= last ? tk : first);
    if (ym < first) ym = first;
    if (ym > last) ym = last;
    const [y, m] = ym.split("-").map(Number);
    const firstNum = Math.round(Date.UTC(y, m - 1, 1) / DAY_MS);
    const daysIn = new Date(Date.UTC(y, m, 0)).getUTCDate();
    const lead = (new Date(firstNum * DAY_MS).getUTCDay() + 6) % 7; // Monday-first
    const prevYM = toISO(firstNum - 1).slice(0, 7), nextYM = toISO(firstNum + daysIn).slice(0, 7);
    const cells = [];
    for (let i = 0; i < lead; i++) cells.push(`<div class="cal-cell out" aria-hidden="true"></div>`);
    let monthTotal = 0, monthDone = 0;
    for (let d = 1; d <= daysIn; d++) {
      const dn = firstNum + d - 1, iso = toISO(dn), e = entryAt(dn);
      const today = dn === todayNum() ? " today" : "";
      if (!e) { cells.push(`<div class="cal-cell out${today}"><span class="num">${d}</span></div>`); continue; }
      if (e.type === "gap") {
        cells.push(`<a class="cal-cell gap${today}" href="#/date/${iso}" aria-label="${esc(fmtLong(iso))}: pushed rest day"><span class="num">${d}</span>${icon("i-tea")}<span class="loc">REST</span></a>`);
        continue;
      }
      const day = D.days[e.n - 1];
      const done = isDone(e.n), partial = !done && checkedCount(e.n) > 0;
      monthTotal++; if (done) monthDone++;
      const loc = day.location === "Gym + Sand" ? "G+S" : day.location.toUpperCase();
      cells.push(`<a class="cal-cell${done ? " done" : partial ? " partial" : ""}${today}" data-el="${day.element}" href="#/day/${e.n}"
        aria-label="${esc(fmtLong(iso))}: Day ${e.n}, ${ELEMENTS[day.element]} ${esc(day.focus)}, ${esc(day.location)}${done ? ", mastered" : partial ? ", in progress" : ""}">
        <span class="num">${d}</span>${icon(`el-${day.element}`)}<span class="loc">${loc}</span></a>`);
    }
    const monthName = new Date(firstNum * DAY_MS).toLocaleDateString(undefined, { timeZone: "UTC", month: "long", year: "numeric" });
    setView(`<div class="wrap narrow"><section class="card cal-card">
      <div class="cal-head">
        <a class="icon-btn" href="#/calendar/${prevYM}" ${ym <= first ? 'aria-disabled="true" tabindex="-1" style="opacity:.35;pointer-events:none"' : ""} aria-label="Previous month">${icon("i-left")}</a>
        <h1>${esc(monthName)}</h1>
        <a class="icon-btn" href="#/calendar/${nextYM}" ${ym >= last ? 'aria-disabled="true" tabindex="-1" style="opacity:.35;pointer-events:none"' : ""} aria-label="Next month">${icon("i-right")}</a>
      </div>
      <div class="cal-grid">${["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((w) => `<div class="cal-dow" aria-hidden="true">${w.slice(0, 1)}<span class="sr-only">${w}</span></div>`).join("")}${cells.join("")}</div>
      <div class="month-stats"><span class="chip">${monthDone} / ${monthTotal} mastered this month</span>${S.shifts.length ? `<span class="chip">Shifted +${S.shifts.length}</span>` : ""}
        ${tk !== ym && tk >= first && tk <= last ? `<a class="chip" href="#/calendar/${tk}">Back to this month</a>` : ""}</div>
      <div class="cal-legend">
        ${Object.keys(ELEMENTS).map((el) => `<span data-el="${el}"><i></i>${ELEMENTS[el]} · ${SHORT_FOCUS[el]}</span>`).join("")}
        <span>GYM · SAND · G+S = both</span><span>✓ mastered</span><span>◯ in progress</span><span>${icon("i-tea")} pushed rest day</span>
      </div></section></div>`, { title: "Calendar" });
  }

  function renderProgress() {
    setNav("progress");
    const doneN = doneCount(), pct = Math.round((100 * doneN) / total());
    const st = streakInfo();
    const t = todayInfo();
    const dayNo = t.state === "workout" ? t.n : t.state === "gap" ? (t.next || total()) : t.state === "before" ? 0 : total();
    const per = { earth: 0, water: 0, fire: 0, air: 0 }, perTot = { earth: 0, water: 0, fire: 0, air: 0 };
    D.days.forEach((d) => { perTot[d.element]++; if (isDone(d.day)) per[d.element]++; });
    // Avatar State meter: four arcs, one per element, each filling its quarter
    const R = 60, C = 2 * Math.PI * R, q = C / 4;
    const segs = Object.keys(ELEMENTS).map((el, i) => {
      const len = (q - 4) * (per[el] / perTot[el]);
      return `<circle class="seg" r="${R}" cx="75" cy="75" style="stroke:var(--${el});stroke-dasharray:${len.toFixed(2)} ${C};stroke-dashoffset:${(-i * q).toFixed(2)}"/>`;
    }).join("");
    const curPhase = t.state === "workout" ? D.days[t.n - 1].phase : t.state === "gap" && t.next ? D.days[t.next - 1].phase : t.state === "before" ? "foundation" : "peak";
    const pIdx = D.program.phases.findIndex((p) => p.id === curPhase);
    const prs = personalRecords();
    setView(`<div class="wrap narrow">
      <section class="card meter-card">
        <div class="meter${pct >= 100 ? " glow" : ""}" role="img" aria-label="Avatar State meter: ${pct}% of the arc mastered">
          <svg viewBox="0 0 150 150"><circle class="track" r="${R}" cx="75" cy="75"/>${segs}</svg>
          <div class="center"><span class="pct">${pct}%</span><span class="lbl">Avatar State</span></div></div>
        <div><div class="eyebrow">Your arc</div><div class="stat-big">${dayNo ? `Day ${dayNo} of ${total()}` : "Not started yet"}</div>
          <p class="muted small" style="margin:.4em 0 0">${plural(doneN, "day")} mastered. ${pct >= 100 ? "Fully realized." : "Fill every element to enter the Avatar State."}</p></div>
      </section>
      <section class="card"><div class="stats">
        <div class="stat"><div class="v">${st.current}</div><div class="k">Current streak</div></div>
        <div class="stat"><div class="v">${st.best}</div><div class="k">Best streak</div></div>
        <div class="stat"><div class="v">+${S.shifts.length}</div><div class="k">Days shifted</div></div>
        <div class="stat"><div class="v">${esc(fmt(toISO(endNum()), { month: "short", day: "numeric" }))}</div><div class="k">Arc ends</div></div>
      </div><p class="muted small" style="margin:10px 0 0">${esc(streakLine(st.current))}</p></section>
      <section class="card"><h2 class="h-brush" style="font-size:24px;margin-bottom:10px">Elements mastered</h2><div class="el-bars">
        ${Object.keys(ELEMENTS).map((el) => `<div class="el-bar" data-el="${el}">${icon(`el-${el}`)}<span>${ELEMENTS[el]}</span>
          <div class="bar"><span style="width:${(100 * per[el] / perTot[el]).toFixed(1)}%"></span></div><span>${per[el]}/${perTot[el]}</span></div>`).join("")}
      </div>${doneN ? "" : `<p class="muted small" style="margin:12px 0 0">${esc(H.empty.noCompletions)}</p>`}</section>
      <section class="card"><h2 class="h-brush" style="font-size:24px;margin-bottom:10px">Training phases</h2><div class="timeline">
        ${D.program.phases.map((p, i) => `<div class="phase${i === pIdx ? " current" : i < pIdx ? " past" : ""}"><div class="n"><span class="n-word">PHASE </span>${p.numeral}</div><div class="t">${esc(p.name)}</div>
          <div class="d">${esc(fmt(p.start, { month: "short" }))}${p.start.slice(0, 7) !== p.end.slice(0, 7) ? "–" + esc(fmt(p.end, { month: "short" })) : ""}</div></div>`).join("")}
      </div><p class="muted small" style="margin:10px 0 0">${esc(D.program.phases[Math.max(0, pIdx)].blurb)}</p></section>
      <section class="card"><h2 class="h-brush" style="font-size:24px;margin-bottom:6px">Best lifts</h2>
        ${prs.length ? `<ul class="pr-list">${prs.map((p) => `<li><span class="nm">${esc(p.name)}</span><span class="best">${esc(p.best)}</span>
          <span class="sub">${p.sessions} session${p.sessions > 1 ? "s" : ""} · last Day ${p.lastDay}</span><span class="sub" style="text-align:right">${p.e1rm ? `≈ ${p.e1rm} ${p.u} e1RM` : ""}</span></li>`).join("")}</ul>`
        : `<p class="muted">${esc(H.empty.noLogs)}</p><p class="muted small">${esc(H.empty.noLogsSub)}</p>`}
      </section></div>`, { title: "Progress" });
  }

  function personalRecords() {
    const by = {};
    for (const [dn, items] of Object.entries(S.logs)) {
      for (const rec of Object.values(items)) {
        const ex = D.ex[rec.ex];
        if (!ex) continue;
        const p = (by[rec.ex] ||= { name: ex.name, sessions: 0, lastDay: 0, bestW: -1, bestR: 0, u: rec.u, e1: 0 });
        p.sessions++;
        p.lastDay = Math.max(p.lastDay, Number(dn));
        for (const [w, r] of rec.s) {
          const wn = parseFloat(w), rn = parseInt(r, 10);
          if (!(wn > 0)) { if (rn > p.bestR && p.bestW < 0) p.bestR = rn; continue; }
          if (wn > p.bestW || (wn === p.bestW && rn > p.bestR)) { p.bestW = wn; p.bestR = rn || 0; p.u = rec.u; }
          if (rn > 0 && rn <= 12) p.e1 = Math.max(p.e1, wn * (1 + rn / 30));
        }
      }
    }
    return Object.values(by).sort((a, b) => b.lastDay - a.lastDay).slice(0, 15).map((p) => ({
      name: p.name, sessions: p.sessions, lastDay: p.lastDay, u: p.u,
      best: p.bestW > 0 ? `${p.bestW} ${p.u} × ${p.bestR || "?"}` : `${p.bestR} reps`,
      e1rm: p.e1 ? Math.round(p.e1) : 0,
    }));
  }

  function renderMore() {
    setNav("more");
    const logs = Object.values(S.logs).reduce((a, m) => a + Object.keys(m).length, 0);
    const on = syncOn();
    const syncCard = window.WLTA_ACCOUNT ? `<section class="card"><h2 class="h-brush" style="font-size:24px">Cloud sync</h2><p class="muted small">You’re signed in. Your checklists, logs, notes and schedule follow you across devices.</p><div class="setting-row"><div><strong>Status</strong><div class="muted small" id="sync-status" aria-live="polite">${esc(syncStatusText())}</div></div><button type="button" class="btn btn-sm" data-action="sync-now">${icon("i-cloud")}Sync now</button></div><button type="button" class="btn btn-sm btn-ghost" data-action="sign-out">Sign out</button></section>` : !CONVEX_URL ? "" : `<section class="card"><h2 class="h-brush" style="font-size:24px">Cloud sync</h2>
        <p class="muted small">Progress is saved to the cloud under a private sync code. Use the same code on your other devices to share it.</p>
        <div class="setting-row"><div><strong>Status</strong><div class="muted small" id="sync-status" aria-live="polite">${esc(syncStatusText())}</div></div>
          ${on ? `<button type="button" class="btn btn-sm" data-action="sync-now">${icon("i-cloud")}Sync now</button>` : `<button type="button" class="btn btn-sm btn-primary" data-action="sync-on">${icon("i-cloud")}Turn on</button>`}</div>
        ${on ? `<div class="sync-block"><strong>Your sync code</strong>
          <div class="code-line"><code class="sync-code" id="sync-code">${esc(sync.code.toUpperCase())}</code><button type="button" class="btn btn-sm" data-action="copy-code">Copy</button></div>
          <div class="muted small">Keep it private: anyone with it can see and change your progress.</div></div>` : ""}
        <form class="sync-block" id="sync-link"><label for="link-code"><strong>Use a code from another device</strong></label>
          <div class="code-line"><input id="link-code" name="code" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="LOTUS-XXXX-XXXX-XXXX-XXXX"><button type="submit" class="btn btn-sm">Link</button></div>
          <div class="muted small">Progress already on this device is merged in, so nothing is lost.</div></form>
        ${on ? `<button type="button" class="btn btn-sm btn-ghost" data-action="sync-off">Turn off sync on this device</button>` : ""}
      </section>`;
    setView(`<div class="wrap narrow">
      <section class="card"><h1 class="h-brush" style="font-size:30px">The Scroll Room</h1>
        <p class="muted small" style="margin:.3em 0 0">${CONVEX_URL ? "Settings, cloud sync, backups and credits." : "Settings, backups and credits. Everything is stored on this device only."}</p>
        <div class="setting-row"><div><strong>Weight unit</strong><div class="muted small">Used for new logs. Old logs keep their unit.</div></div>
          <div class="seg-ctl" role="group" aria-label="Weight unit">${["lb", "kg"].map((u) => `<button type="button" data-action="unit" data-u="${u}" aria-pressed="${S.settings.unit === u}">${u}</button>`).join("")}</div></div>
        <div class="setting-row"><div><strong>Schedule shifts</strong><div class="muted small">${S.shifts.length ? `Shifted +${S.shifts.length} day${S.shifts.length > 1 ? "s" : ""}. The arc now ends ${esc(fmtMed(toISO(endNum())))}.` : `On schedule. The arc ends ${esc(fmtMed(toISO(endNum())))}.`}</div></div>
          ${S.shifts.length ? `<button type="button" class="btn btn-sm" data-action="undo">${icon("i-undo")}Undo last</button>` : ""}</div>
      </section>
      ${syncCard}
      <section class="card"><h2 class="h-brush" style="font-size:24px">Backup &amp; move devices</h2>
        <p class="muted small">${plural(doneCount(), "mastered day")}, ${plural(logs, "logged exercise")}, ${plural(Object.keys(S.notes).length, "note")} and ${plural(S.shifts.length, "shift")} saved here.</p>
        <div class="btn-row"><button type="button" class="btn btn-primary" data-action="export">${icon("i-download")}Export backup</button>
          <button type="button" class="btn" data-action="import">${icon("i-upload")}Import backup</button></div>
      </section>
      <section class="card"><h2 class="h-brush" style="font-size:24px">Credits &amp; about</h2>
        <div class="prose small"><p>Exercise photos: the public-domain <a href="https://github.com/yuhonas/free-exercise-db" rel="noopener" target="_blank">free-exercise-db</a>, plus a few photos from Pexels, Unsplash and Wikimedia Commons. Each one was checked to show the exact movement.</p>
        <p>Quotes: original lines written in the spirit of <em>Avatar: The Last Airbender</em>. This is a personal fan project with no affiliation to Nickelodeon or the show's creators.</p></div>
        <a class="btn" href="#/credits">See all image credits</a>
      </section>
      <section class="card"><h2 class="h-brush" style="font-size:24px">Start over</h2>
        <p class="muted small">${window.WLTA_ACCOUNT ? 'This clears your shared progress on every device. Export a backup first.' : esc(H.io.resetConfirm)+(on ? " Your cloud copy is kept under your current sync code, and this device gets a new one." : "")}</p>
        <button type="button" class="btn btn-danger" data-action="reset">${window.WLTA_ACCOUNT?'Reset shared progress':'Erase all progress on this device'}</button></section>
    </div>`, { title: "More" });
  }

  function renderCredits() {
    setNav("more");
    const list = D.creditsList;
    const groups = [
      ["free-exercise-db", "free-exercise-db · Unlicense (public domain)", list.filter((c) => c.source === "free-exercise-db")],
      ["external", "Pexels, Unsplash & Wikimedia Commons", list.filter((c) => c.source !== "free-exercise-db" && c.source !== "Original illustration")],
      ["placeholder", "Illustrated placeholders (original)", list.filter((c) => c.source === "Original illustration")],
    ];
    const row = (c) => {
      const ex = D.ex[c.id];
      const src = c.sourceUrl ? `<a href="${esc(c.sourceUrl)}" target="_blank" rel="noopener">${esc(c.source)}</a>` : esc(c.source);
      const lic = c.licenseUrl ? `<a href="${esc(c.licenseUrl)}" target="_blank" rel="noopener">${esc(c.license)}</a>` : esc(c.license);
      return `<li><img src="${esc(ex ? ex.thumb : c.files[0])}" alt="" loading="lazy" width="54" height="36"><div><div class="nm">${esc(c.exercise)}</div>
        <div class="src">${src}${c.author ? ` · ${esc(c.author)}` : ""} · ${lic}${c.modifications ? ` · ${esc(c.modifications)}` : ""}${c.note ? ` · ${esc(c.note)}` : ""}</div></div></li>`;
    };
    setView(`<div class="wrap narrow"><section class="card"><h1 class="h-brush" style="font-size:30px">Image credits</h1>
      <p class="muted small" style="margin:.3em 0 1em">${list.length} exercise images, each checked to show the exact movement. Where no correct, openly licensed photo existed, an illustrated placeholder is used instead of a wrong photo. Full details live in <code>data/image-credits.json</code>.</p>
      ${groups.map(([k, title, items], i) => `<details class="credit-group card" style="margin-top:10px" ${i > 0 ? "open" : ""}><summary>${esc(title)} <span class="chip">${items.length}</span></summary>
        <ul class="credit-list" style="margin-top:8px">${items.map(row).join("")}</ul></details>`).join("")}
      <p class="small muted" style="margin-top:14px">free-exercise-db images come from the <a href="https://github.com/wrkout/exercises.json" target="_blank" rel="noopener">wrkout/exercises.json</a> project and are released under the Unlicense. Pexels and Unsplash photos are used under their free licenses; Wikimedia Commons files under the license shown.</p>
      <a class="btn" href="#/more">${icon("i-left")}Back</a></section></div>`, { title: "Credits" });
  }

  function renderError(err) {
    console.error("[WLTA]", err);
    const fileProto = location.protocol === "file:";
    view().innerHTML = `<div class="wrap narrow"><section class="card error-card"><h1 class="h-brush" style="font-size:30px">The scrolls could not be unrolled</h1>
      <p>${fileProto ? "Browsers block loading data files when a page is opened straight from disk." : "The training data failed to load. Check your connection and refresh."}</p>
      ${fileProto ? `<p>Start a tiny local server in the project folder, then open <code>http://localhost:8000</code>:</p><p><code>python -m http.server 8000</code></p>` : ""}
      <p class="muted small">${esc(err && err.message)}</p></section></div>`;
  }

  // ------------------------------------------------------------------ lightbox
  let lbTimer = null;
  function openLightbox(id) {
    const ex = D.ex[id];
    if (!ex) return;
    const lb = $("#lightbox");
    const credit = D.credits[id];
    const alt = !!ex.imageAlt;
    const creditText = !credit ? ""
      : credit.source === "Original illustration" ? "Illustrated placeholder: no openly licensed photo of this exact movement was found."
        : credit.source === "free-exercise-db" ? "Photos: free-exercise-db (public domain, Unlicense)."
          : `Photo: ${credit.author} · ${credit.source} · ${credit.license}.`;
    lb.innerHTML = `<div class="lightbox-card" data-el="${ex.element}">
      <button type="button" class="close-btn" data-action="close-lightbox" aria-label="Close">${icon("i-close")}</button>
      <div class="lightbox-media">
        <img class="f0" src="${esc(ex.image)}" alt="${esc(ex.name)}${alt ? ", start position" : ""}">
        ${alt ? `<img class="f1 hide" src="${esc(ex.imageAlt)}" alt="${esc(ex.name)}, finish position">
          <div class="frame-label seg-ctl" role="group" aria-label="Movement frame"><button type="button" data-action="frame" data-f="0" aria-pressed="true">Start</button><button type="button" data-action="frame" data-f="1" aria-pressed="false">Finish</button></div>` : ""}
      </div>
      <div class="lightbox-body"><div class="eyebrow">${esc(ex.category)} · ${esc(ex.equipment)}</div>
        <h2 id="lb-title">${esc(ex.name)}</h2>${ex.desc ? `<p>${esc(ex.desc)}</p>` : ""}
        <ul>${ex.cues.map((c) => `<li>${esc(c)}</li>`).join("")}</ul>
        <div class="credit">${esc(creditText)}</div></div></div>`;
    lb.hidden = false;
    document.body.style.overflow = "hidden";
    $(".close-btn", lb).focus();
    clearInterval(lbTimer);
    if (alt && !reducedMotion()) { let f = 0; lbTimer = setInterval(() => { f = 1 - f; setFrame(f); }, 1700); }
  }
  function setFrame(f) {
    const lb = $("#lightbox");
    const f1 = $(".f1", lb);
    if (!f1) return;
    f1.classList.toggle("hide", f === 0);
    $$("[data-action=frame]", lb).forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.f) === f)));
  }
  function closeLightbox() { const lb = $("#lightbox"); lb.hidden = true; lb.innerHTML = ""; clearInterval(lbTimer); document.body.style.overflow = ""; }

  // ------------------------------------------------------------------ celebration
  function celebrate(n) {
    const day = D.days[n - 1], el = day.element;
    const ov = $("#celebrate");
    ov.dataset.el = el;
    const parts = Array.from({ length: reducedMotion() ? 0 : 30 }, (_, i) =>
      `<i class="p-${el}${el === "earth" && i % 3 === 0 ? " g" : ""}" style="--x:${rand(2, 96)}%;--s:${rand(7, 16)}px;--d:${rand(24, 42) / 10}s;--delay:${rand(0, 14) / 10}s;--dx:${rand(-90, 90)}px;--dy:${-rand(90, 280)}px"></i>`).join("");
    const st = streakInfo();
    ov.innerHTML = `<div class="particles" aria-hidden="true">${parts}</div>
      <div class="celebrate-card"><div class="emblem">${icon(`el-${el}`)}</div>
        <div class="stats-line">Day ${n} of ${total()} · ${esc(day.formatName)}</div>
        <h2 id="cel-title">You have mastered ${ELEMENTS[el]} today.</h2>
        <p>${esc(pick(H.completion[el]))}</p>
        <p class="stats-line">Streak ${st.current} · Avatar State ${Math.round((100 * doneCount()) / total())}%</p>
        <button type="button" class="btn btn-primary" data-action="close-celebrate">Bow and continue</button></div>`;
    ov.hidden = false;
    $("[data-action=close-celebrate]", ov).focus();
  }
  function closeCelebrate() { const ov = $("#celebrate"); ov.hidden = true; ov.innerHTML = ""; }

  // ------------------------------------------------------------------ actions
  function toggleCheck(n, key, btn) {
    const c = (S.checks[n] ||= {});
    if (c[key]) delete c[key]; else c[key] = 1;
    if (!Object.keys(c).length) delete S.checks[n];
    const was = isDone(n);
    const now = checkedCount(n) >= D.totals[n];
    if (now && !was) S.done[n] = new Date().toISOString();
    if (!now && was) delete S.done[n];
    save();
    const on = !!(S.checks[n] && S.checks[n][key]);
    btn.setAttribute("aria-pressed", String(on));
    btn.closest(".ex").classList.toggle("done", on);
    btn.classList.remove("pop"); void btn.offsetWidth; if (on) btn.classList.add("pop");
    const prog = $("#day-progress");
    if (prog) prog.outerHTML = progressHTML(n);
    const mb = $("#mastered");
    if (mb) mb.outerHTML = masteredHTML(n);
    if (now && !was) celebrate(n);
  }

  function toggleSupps(iso, btn) {
    if (S.supps[iso]) delete S.supps[iso]; else S.supps[iso] = 1;
    save();
    const on = !!S.supps[iso];
    btn.setAttribute("aria-pressed", String(on));
    $(".supp-state", btn).textContent = on ? "Yes" : "No";
    const box = $(".supp-box", btn);
    box.classList.remove("pop"); void box.offsetWidth; if (on) box.classList.add("pop");
  }

  function pushBack(n) {
    if (isDone(n)) { toast("That day is already mastered. No need to push it."); return; }
    S.shifts.push(n);
    calCache = null;
    save(true);
    toast(pick(H.shift).replace("{end}", fmtMed(toISO(endNum()))), { undo: true });
    route();
  }
  function undoShift() {
    if (!S.shifts.length) return;
    S.shifts.pop();
    calCache = null;
    save(true);
    toast(pick(H.undo));
    route();
  }

  function onLogInput(input) {
    const panel = input.closest(".log");
    const n = Number(panel.dataset.n), key = panel.dataset.key;
    const day = D.days[n - 1];
    const [bi, ii] = key.split(".").map(Number);
    const it = day.blocks[bi].items[ii];
    const vals = $$("input", panel);
    const s = [];
    for (let i = 0; i < it.sets; i++) {
      const w = vals.find((x) => Number(x.dataset.set) === i && x.dataset.f === "w").value.trim().slice(0, 8);
      const r = vals.find((x) => Number(x.dataset.set) === i && x.dataset.f === "r").value.trim().slice(0, 8);
      s.push([w, r]);
    }
    const logs = (S.logs[n] ||= {});
    if (s.some((x) => x[0] || x[1])) logs[key] = { ex: it.id, u: (logs[key] && logs[key].u) || S.settings.unit, s, t: Date.now() };
    else delete logs[key];
    if (!Object.keys(logs).length) delete S.logs[n];
    save();
    const sum = $(".log-summary", panel.closest(".ex"));
    if (sum) sum.innerHTML = logs[key] ? `Logged: <b>${esc(setsText(logs[key]))}</b>` : "";
  }
  function fillLast(panel) {
    const n = Number(panel.dataset.n);
    const [bi, ii] = panel.dataset.key.split(".").map(Number);
    const it = D.days[n - 1].blocks[bi].items[ii];
    const last = lastLog(it.id, n);
    if (!last) return;
    $$("input", panel).forEach((inp) => { const v = last.s[Number(inp.dataset.set)]; if (v) inp.value = v[inp.dataset.f === "w" ? 0 : 1] || ""; });
    onLogInput($("input", panel));
    toast("Copied last time. Now add a little.");
  }
  function toggleLog(btn) {
    const li = btn.closest(".ex"), main = btn.closest(".day-main");
    const n = Number(main.dataset.n), key = li.dataset.key;
    const id = `${n}:${key}`;
    const existing = $(".log", li);
    if (existing) { existing.remove(); openLogs.delete(id); btn.setAttribute("aria-expanded", "false"); btn.lastChild.textContent = "Log sets"; return; }
    const [bi, ii] = key.split(".").map(Number);
    li.insertAdjacentHTML("beforeend", logPanelHTML(n, key, D.days[n - 1].blocks[bi].items[ii]));
    openLogs.add(id);
    btn.setAttribute("aria-expanded", "true");
    btn.lastChild.textContent = "Hide log";
    const first = $(".log input", li);
    if (first && !("ontouchstart" in window)) first.focus();
  }

  function exportPayload() { return { app: APP_ID, version: 1, exportedAt: new Date().toISOString(), data: S }; }
  function exportData() {
    const blob = new Blob([JSON.stringify(exportPayload(), null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `white-lotus-backup-${todayISO()}.json`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
    toast(H.io.exported);
  }
  function parseBackup(obj) { return sanitize(isObj(obj) && obj.app === APP_ID ? obj.data : obj); }
  function applyImport(data) { S = reconcile(data); calCache = null; openLogs.clear(); save(true); route(); }
  async function importFile(file) {
    let obj;
    try { obj = JSON.parse(await file.text()); } catch (e) { toast(H.io.badFile); return; }
    const data = parseBackup(obj);
    if (!data) { toast(H.io.badFile); return; }
    const logs = Object.values(data.logs).reduce((a, m) => a + Object.keys(m).length, 0);
    const ok = await confirmModal({
      title: "Replace this device's data?",
      body: `The backup holds ${plural(Object.keys(data.done).length, "mastered day")}, ${plural(logs, "logged exercise")}, ${plural(Object.keys(data.notes).length, "note")} and ${plural(data.shifts.length, "schedule shift")}. It will replace what's on this device${syncOn() ? " and in your cloud copy" : ""}.`,
      ok: "Import backup",
    });
    if (!ok) return;
    applyImport(data);
    toast(H.io.imported);
  }
  async function resetAll() {
    const body = window.WLTA_ACCOUNT ? 'This clears your shared progress on every device. Export a backup first.' : H.io.resetConfirm + (syncOn() ? " Your cloud copy is kept under your current sync code, and this device gets a new one." : "");
    const ok = await confirmModal({ title: "Erase everything?", body, ok: "Erase all progress", danger: true });
    if (!ok) return;
    if (syncOn() && !window.WLTA_ACCOUNT) Object.assign(sync, { code: newCode(), rev: 0 });
    S = blankState(); calCache = null; openLogs.clear(); save(true);
    toast(H.io.resetDone);
    location.hash = "#/today";
    route();
  }

  // ------------------------------------------------------------------ events
  function bindEvents() {
    document.addEventListener("click", (e) => {
      const t = e.target.closest("[data-action]");
      if (!t) {
        if (e.target.id === "lightbox") closeLightbox();
        return;
      }
      const a = t.dataset.action;
      if (a === "check") { const main = t.closest(".day-main"); toggleCheck(Number(main.dataset.n), t.closest(".ex").dataset.key, t); }
      else if (a === "supps") toggleSupps(t.dataset.iso, t);
      else if (a === "img") openLightbox(t.dataset.id);
      else if (a === "log") toggleLog(t);
      else if (a === "fill-last") fillLast(t.closest(".log"));
      else if (a === "push") pushBack(Number(t.dataset.n));
      else if (a === "undo") { $("#toast").classList.remove("show"); undoShift(); }
      else if (a === "close-lightbox") closeLightbox();
      else if (a === "frame") { clearInterval(lbTimer); setFrame(Number(t.dataset.f)); }
      else if (a === "close-celebrate") closeCelebrate();
      else if (a === "unit") { S.settings.unit = t.dataset.u; save(true); renderMore(); }
      else if (a === "export") exportData();
      else if (a === "import") $("#import-file").click();
      else if (a === "reset") resetAll();
      else if (a === "sync-now") syncNow();
      else if (a === "sign-out") { awaitSyncThenSignOut(); }
      else if (a === "copy-code") copyCode();
      else if (a === "sync-off") setSyncOff(true);
      else if (a === "sync-on") setSyncOff(false);
    });
    document.addEventListener("submit", (e) => {
      if (e.target.id !== "sync-link") return;
      e.preventDefault();
      linkCode(e.target.elements.code.value);
    });
    document.addEventListener("input", (e) => {
      const t = e.target;
      if (t.matches(".log input")) onLogInput(t);
      else if (t.dataset.action === "notes") {
        const n = Number(t.dataset.n);
        if (t.value.trim()) S.notes[n] = t.value.slice(0, 4000); else delete S.notes[n];
        save();
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape") return;
      if (!$("#lightbox").hidden) closeLightbox();
      else if (!$("#celebrate").hidden) closeCelebrate();
    });
    $("#celebrate").addEventListener("click", (e) => { if (e.target.id === "celebrate") closeCelebrate(); });
    $("#import-file").addEventListener("change", (e) => { const f = e.target.files[0]; e.target.value = ""; if (f) importFile(f); });
    window.addEventListener("hashchange", () => route());
    document.addEventListener("visibilitychange", () => { // new day while the app sat open
      if (document.visibilityState === "visible" && lastRenderedToday && lastRenderedToday !== todayISO() && /^#?\/?(today)?$/.test(location.hash.replace(/^#/, ""))) route();
    });
    window.addEventListener("pagehide", () => save(true, false)); // flush only: real changes already queued a sync
  }

  function route() {
    closeLightbox();
    const h = location.hash.replace(/^#\/?/, "");
    const [name, arg] = h.split("/");
    if (name === "day") {
      const n = Math.min(total(), Math.max(1, parseInt(arg, 10) || 1));
      const t = todayInfo();
      setNav(t.state === "workout" && t.n === n ? "today" : "calendar");
      return renderDay(n);
    }
    if (name === "date") return renderDate(arg);
    if (name === "calendar") return renderCalendar(arg);
    if (name === "progress") return renderProgress();
    if (name === "more") return renderMore();
    if (name === "credits") return renderCredits();
    return renderToday();
  }

  // ------------------------------------------------------------------ boot
  async function loadData() {
    const get = (p) => fetch(p, { cache: "no-cache" }).then((r) => { if (!r.ok) throw new Error(`${p} → HTTP ${r.status}`); return r.json(); });
    const [sched, exs, content, credits] = await Promise.all([
      get("data/schedule.json"), get("data/exercises.json"), get("data/content.json"),
      get("data/image-credits.json").catch(() => ({ images: [] })),
    ]);
    D = {
      program: sched.program, days: sched.days, content,
      ex: Object.fromEntries(exs.exercises.map((e) => [e.id, e])),
      credits: Object.fromEntries(credits.images.map((c) => [c.id, c])), creditsList: credits.images, totals: {},
    };
    sched.days.forEach((d) => { D.totals[d.day] = d.blocks.reduce((a, b) => a + b.items.length, 0); });
    H = content.humor;
  }

  async function init() {
    await window.WLTA_READY;
    if (window.WLTA_ACCOUNT) CONVEX_URL = "/api";
    const msg = $("#loading-msg");
    if (msg) msg.textContent = pick(LOADING);
    const p = new URLSearchParams(location.search).get("today");
    if (p && /^\d{4}-\d{2}-\d{2}$/.test(p)) todayOverride = p;
    try { await loadData(); } catch (e) { renderError(e); return; }
    if (msg) msg.textContent = pick(H.loading);
    S = loadState();
    loadSync();
    bindEvents();
    route();
    startSync();
    // Small console API for testing and power users.
    window.WLTA = {
      get state() { return JSON.parse(JSON.stringify(S)); },
      get sync() { return { ...sync, status: syncState, error: syncError }; },
      dateOf, entryAt: (iso) => entryAt(toNum(iso)), endDate: () => toISO(endNum()), todayInfo, streakInfo,
      exportPayload, parseBackup, applyImport, pushBack, undoShift, syncNow, normalizeCode,
    };
  }

  init();
})();
