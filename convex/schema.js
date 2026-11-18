import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// One row per sync code: the app's saved progress, stored as the same JSON the browser keeps in localStorage.
export default defineSchema({
  loginAttempts: defineTable({key:v.string(),count:v.number(),startedAt:v.number()}).index('by_key',['key']),
  progress: defineTable({
    code: v.string(),
    state: v.string(),
    rev: v.number(), // bumps on every save, so a device can tell when another one saved first
    updatedAt: v.number(),
  }).index("by_code", ["code"]),
  // One daily progress photo per sync code and calendar date. The images live in Convex file storage:
  // a full-size JPEG for viewing and a small thumbnail for the gallery. They're kept out of the progress
  // JSON so photos never slow down or bloat checklist syncing.
  photos: defineTable({
    code: v.string(),
    date: v.string(), // YYYY-MM-DD calendar date the photo belongs to
    full: v.id("_storage"),
    thumb: v.id("_storage"),
    w: v.number(), // full-size pixel dimensions, so pages can reserve the right space before the image loads
    h: v.number(),
    updatedAt: v.number(), // doubles as the image version for cache-busting
  }).index("by_code_date", ["code", "date"]),
});
