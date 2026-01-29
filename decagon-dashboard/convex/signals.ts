import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ============ QUERIES ============

// Get all signals
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("signals").order("desc").collect();
  },
});

// Get signals by company
export const getByCompany = query({
  args: { companyId: v.id("companies") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("signals")
      .withIndex("by_company", (q) => q.eq("companyId", args.companyId))
      .order("desc")
      .collect();
  },
});

// Get signals by type
export const getByType = query({
  args: { signalType: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("signals")
      .withIndex("by_type", (q) => q.eq("signalType", args.signalType))
      .collect();
  },
});

// Get recent signals
export const getRecent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("signals")
      .order("desc")
      .take(args.limit || 20);
  },
});

// ============ MUTATIONS ============

// Create signal
export const create = mutation({
  args: {
    companyId: v.id("companies"),
    signalType: v.string(),
    title: v.string(),
    description: v.string(),
    sourceUrl: v.optional(v.string()),
    relevanceScore: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("signals", {
      ...args,
      discoveredAt: Date.now(),
    });
  },
});

// Update signal
export const update = mutation({
  args: {
    id: v.id("signals"),
    signalType: v.optional(v.string()),
    title: v.optional(v.string()),
    description: v.optional(v.string()),
    sourceUrl: v.optional(v.string()),
    relevanceScore: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    const filteredUpdates = Object.fromEntries(
      Object.entries(updates).filter(([_, v]) => v !== undefined)
    );
    await ctx.db.patch(id, filteredUpdates);
  },
});

// Delete signal
export const remove = mutation({
  args: { id: v.id("signals") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// Bulk create signals (for migration)
export const bulkCreate = mutation({
  args: {
    signals: v.array(
      v.object({
        companyId: v.id("companies"),
        signalType: v.string(),
        title: v.string(),
        description: v.string(),
        sourceUrl: v.optional(v.string()),
        relevanceScore: v.optional(v.number()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const signal of args.signals) {
      const id = await ctx.db.insert("signals", {
        ...signal,
        discoveredAt: Date.now(),
      });
      ids.push(id);
    }
    return ids;
  },
});
