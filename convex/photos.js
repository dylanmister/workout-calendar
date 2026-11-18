import { mutation, query } from "./_generated/server";
import { ConvexError, v } from "convex/values";

// Daily progress photos. Like progress, these are only reachable through the signed-in Vercel API,
// which holds the server key; the browser never sees storage IDs or storage URLs.
const CODE = /^lotus(-[a-z2-7]{4}){4}$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const MAX_BYTES = { full: 3 * 1024 * 1024, thumb: 512 * 1024 };

function checkCode(code, serverKey) {
  if (!process.env.PROGRESS_SERVER_KEY || serverKey !== process.env.PROGRESS_SERVER_KEY) throw new ConvexError("Unauthorized");
  if (!CODE.test(code)) throw new ConvexError("That isn't a valid sync code.");
}
function checkDate(date) {
  const d = new Date(`${date}T00:00:00Z`);
  if (!DATE.test(date) || Number.isNaN(d.getTime()) || d.toISOString().slice(0, 10) !== date) throw new ConvexError("That isn't a valid date.");
}
const byDate = (ctx, code, date) => ctx.db.query("photos").withIndex("by_code_date", (q) => q.eq("code", code).eq("date", date)).unique();
const pixels = (n) => Math.max(1, Math.min(10000, Math.round(Number(n) || 1)));

async function checkUpload(ctx, id, max) {
  const meta = await ctx.db.system.get("_storage", id);
  if (!meta || meta.size > max || (meta.contentType && meta.contentType !== "image/jpeg")) throw new ConvexError("That photo couldn't be saved.");
}

// Every photo for the account, oldest first (the index is ordered by date).
export const list = query({
  args: { code: v.string(), serverKey: v.string() },
  handler: async (ctx, { code, serverKey }) => {
    checkCode(code, serverKey);
    const rows = await ctx.db.query("photos").withIndex("by_code_date", (q) => q.eq("code", code)).collect();
    return rows.map((r) => ({ date: r.date, v: r.updatedAt, w: r.w, h: r.h }));
  },
});

// A short-lived storage URL for one image, which the API reads server-side and streams to the signed-in browser.
export const file = query({
  args: { code: v.string(), serverKey: v.string(), date: v.string(), size: v.union(v.literal("full"), v.literal("thumb")) },
  handler: async (ctx, { code, serverKey, date, size }) => {
    checkCode(code, serverKey);
    checkDate(date);
    const row = await byDate(ctx, code, date);
    if (!row) return null;
    const url = await ctx.storage.getUrl(row[size]);
    return url ? { url, v: row.updatedAt } : null;
  },
});

export const uploadUrls = mutation({
  args: { code: v.string(), serverKey: v.string() },
  handler: async (ctx, { code, serverKey }) => {
    checkCode(code, serverKey);
    return { full: await ctx.storage.generateUploadUrl(), thumb: await ctx.storage.generateUploadUrl() };
  },
});

// Saves the day's photo, replacing (and deleting) any earlier one for the same date.
export const save = mutation({
  args: { code: v.string(), serverKey: v.string(), date: v.string(), full: v.id("_storage"), thumb: v.id("_storage"), w: v.number(), h: v.number() },
  handler: async (ctx, { code, serverKey, date, full, thumb, w, h }) => {
    checkCode(code, serverKey);
    checkDate(date);
    if (full === thumb) throw new ConvexError("That photo couldn't be saved.");
    await checkUpload(ctx, full, MAX_BYTES.full);
    await checkUpload(ctx, thumb, MAX_BYTES.thumb);
    const fields = { full, thumb, w: pixels(w), h: pixels(h), updatedAt: Date.now() };
    const old = await byDate(ctx, code, date);
    if (old) {
      await ctx.db.patch("photos", old._id, fields);
      for (const id of [old.full, old.thumb]) if (id !== full && id !== thumb) await ctx.storage.delete(id);
    } else {
      await ctx.db.insert("photos", { code, date, ...fields });
    }
    return { date, v: fields.updatedAt, w: fields.w, h: fields.h };
  },
});

export const remove = mutation({
  args: { code: v.string(), serverKey: v.string(), date: v.string() },
  handler: async (ctx, { code, serverKey, date }) => {
    checkCode(code, serverKey);
    checkDate(date);
    const row = await byDate(ctx, code, date);
    if (row) {
      await ctx.db.delete("photos", row._id);
      await ctx.storage.delete(row.full);
      await ctx.storage.delete(row.thumb);
    }
    return { ok: true };
  },
});

// Cleans up files from an upload whose save failed, so they don't sit in storage unused.
// Files that belong to a saved photo are never touched.
export const discard = mutation({
  args: { code: v.string(), serverKey: v.string(), ids: v.array(v.id("_storage")) },
  handler: async (ctx, { code, serverKey, ids }) => {
    checkCode(code, serverKey);
    if (ids.length > 4) throw new ConvexError("Too many files.");
    const used = new Set();
    for (const row of await ctx.db.query("photos").collect()) { used.add(row.full); used.add(row.thumb); }
    for (const id of ids) if (!used.has(id) && (await ctx.db.system.get("_storage", id))) await ctx.storage.delete(id);
    return { ok: true };
  },
});
