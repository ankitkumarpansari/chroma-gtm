import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ============ QUERIES ============

// Get all companies
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("companies").order("desc").collect();
  },
});

// Get companies by ICP
export const getByIcp = query({
  args: { icp: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("companies")
      .withIndex("by_icp", (q) => q.eq("icp", args.icp))
      .collect();
  },
});

// Get companies by status
export const getByStatus = query({
  args: { status: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("companies")
      .withIndex("by_status", (q) => q.eq("status", args.status))
      .collect();
  },
});

// Get companies by priority
export const getByPriority = query({
  args: { priority: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("companies")
      .withIndex("by_priority", (q) => q.eq("priority", args.priority))
      .collect();
  },
});

// Get single company with all contacts
export const getWithContacts = query({
  args: { companyId: v.id("companies") },
  handler: async (ctx, args) => {
    const company = await ctx.db.get(args.companyId);
    if (!company) return null;

    const contacts = await ctx.db
      .query("contacts")
      .withIndex("by_company", (q) => q.eq("companyId", args.companyId))
      .collect();

    const signals = await ctx.db
      .query("signals")
      .withIndex("by_company", (q) => q.eq("companyId", args.companyId))
      .collect();

    return { company, contacts, signals };
  },
});

// Search companies by name
export const search = query({
  args: { searchTerm: v.string() },
  handler: async (ctx, args) => {
    const companies = await ctx.db.query("companies").collect();
    const term = args.searchTerm.toLowerCase();
    return companies.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.icp.toLowerCase().includes(term) ||
        c.whyFit.toLowerCase().includes(term)
    );
  },
});

// Get dashboard stats
export const getStats = query({
  args: {},
  handler: async (ctx) => {
    const companies = await ctx.db.query("companies").collect();
    const contacts = await ctx.db.query("contacts").collect();

    const byStatus: Record<string, number> = {};
    const byIcp: Record<string, number> = {};
    const byPriority: Record<string, number> = {};

    for (const c of companies) {
      byStatus[c.status] = (byStatus[c.status] || 0) + 1;
      byIcp[c.icp] = (byIcp[c.icp] || 0) + 1;
      byPriority[c.priority] = (byPriority[c.priority] || 0) + 1;
    }

    return {
      totalCompanies: companies.length,
      totalContacts: contacts.length,
      byStatus,
      byIcp,
      byPriority,
    };
  },
});

// ============ MUTATIONS ============

// Create a new company
export const create = mutation({
  args: {
    name: v.string(),
    domain: v.optional(v.string()),
    icp: v.string(),
    priority: v.string(),
    signalStrength: v.string(),
    whyFit: v.string(),
    decisionMakerTitles: v.string(),
    status: v.string(),
    owner: v.optional(v.string()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("companies", {
      ...args,
      lastUpdated: Date.now(),
    });
  },
});

// Update company
export const update = mutation({
  args: {
    id: v.id("companies"),
    name: v.optional(v.string()),
    domain: v.optional(v.string()),
    icp: v.optional(v.string()),
    priority: v.optional(v.string()),
    signalStrength: v.optional(v.string()),
    whyFit: v.optional(v.string()),
    decisionMakerTitles: v.optional(v.string()),
    status: v.optional(v.string()),
    owner: v.optional(v.string()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    const filteredUpdates = Object.fromEntries(
      Object.entries(updates).filter(([_, v]) => v !== undefined)
    );
    await ctx.db.patch(id, {
      ...filteredUpdates,
      lastUpdated: Date.now(),
    });
  },
});

// Update company status
export const updateStatus = mutation({
  args: {
    id: v.id("companies"),
    status: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.status,
      lastUpdated: Date.now(),
    });
  },
});

// Delete company
export const remove = mutation({
  args: { id: v.id("companies") },
  handler: async (ctx, args) => {
    // First delete all related contacts
    const contacts = await ctx.db
      .query("contacts")
      .withIndex("by_company", (q) => q.eq("companyId", args.id))
      .collect();

    for (const contact of contacts) {
      // Delete outreach for each contact
      const outreach = await ctx.db
        .query("outreach")
        .withIndex("by_contact", (q) => q.eq("contactId", contact._id))
        .collect();
      for (const o of outreach) {
        await ctx.db.delete(o._id);
      }
      await ctx.db.delete(contact._id);
    }

    // Delete signals
    const signals = await ctx.db
      .query("signals")
      .withIndex("by_company", (q) => q.eq("companyId", args.id))
      .collect();
    for (const s of signals) {
      await ctx.db.delete(s._id);
    }

    // Delete company
    await ctx.db.delete(args.id);
  },
});

// Bulk create companies (for migration)
export const bulkCreate = mutation({
  args: {
    companies: v.array(
      v.object({
        name: v.string(),
        domain: v.optional(v.string()),
        icp: v.string(),
        priority: v.string(),
        signalStrength: v.string(),
        whyFit: v.string(),
        decisionMakerTitles: v.string(),
        status: v.string(),
        owner: v.optional(v.string()),
        notes: v.optional(v.string()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const company of args.companies) {
      const id = await ctx.db.insert("companies", {
        ...company,
        lastUpdated: Date.now(),
      });
      ids.push({ name: company.name, id });
    }
    return ids;
  },
});
