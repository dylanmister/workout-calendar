import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// One row per sync code: the app's saved progress, stored as the same JSON the browser keeps in localStorage.
export default defineSchema({
  progress: defineTable({
    code: v.string(),
    state: v.string(),
    rev: v.number(), // bumps on every save, so a device can tell when another one saved first
    updatedAt: v.number(),
  }).index("by_code", ["code"]),
});
