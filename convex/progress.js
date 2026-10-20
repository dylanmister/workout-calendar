import { mutation, query } from "./_generated/server";
import { ConvexError, v } from "convex/values";

// Sync codes are "lotus-" plus 16 random base32 characters (80 bits). Nobody can guess one,
// so the code itself is the key to a person's progress. There are no accounts.
const CODE = /^lotus(-[a-z2-7]{4}){4}$/;
const MAX_STATE = 512 * 1024;

function checkCode(code) {
  if (!CODE.test(code)) throw new ConvexError("That isn't a valid sync code."); // ConvexError text reaches the app in production too
}

const byCode = (ctx, code) => ctx.db.query("progress").withIndex("by_code", (q) => q.eq("code", code)).unique();

export const get = query({
  args: { code: v.string() },
  handler: async (ctx, { code }) => {
    checkCode(code);
    const row = await byCode(ctx, code);
    return row ? { state: row.state, rev: row.rev, updatedAt: row.updatedAt } : null;
  },
});

// Saves only if nothing was saved since `baseRev`. Otherwise it returns the newer copy so the
// device can merge it into its own changes and try again, instead of overwriting another device's work.
export const save = mutation({
  args: { code: v.string(), baseRev: v.number(), state: v.string() },
  handler: async (ctx, { code, baseRev, state }) => {
    checkCode(code);
    if (state.length > MAX_STATE) throw new ConvexError("Saved progress is too large.");
    let parsed = null;
    try { parsed = JSON.parse(state); } catch { /* reported below */ }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new ConvexError("Saved progress must be a JSON object.");
    const row = await byCode(ctx, code);
    const updatedAt = Date.now();
    if (!row) {
      await ctx.db.insert("progress", { code, state, rev: 1, updatedAt });
      return { ok: true, rev: 1 };
    }
    if (row.rev !== baseRev) return { ok: false, rev: row.rev, state: row.state };
    await ctx.db.patch(row._id, { state, rev: row.rev + 1, updatedAt });
    return { ok: true, rev: row.rev + 1 };
  },
});
