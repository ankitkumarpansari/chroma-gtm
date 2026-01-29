import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ============ QUERIES ============

// Get all contacts
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("contacts").order("desc").collect();
  },
});

// Get contacts by company
export const getByCompany = query({
  args: { companyId: v.id("companies") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contacts")
      .withIndex("by_company", (q) => q.eq("companyId", args.companyId))
      .collect();
  },
});

// Get contacts by job level (for targeting VPs, Directors, etc.)
export const getByJobLevel = query({
  args: { jobLevel: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contacts")
      .withIndex("by_job_level", (q) => q.eq("jobLevel", args.jobLevel))
      .collect();
  },
});

// Get decision makers (VP+ level)
export const getDecisionMakers = query({
  args: {},
  handler: async (ctx) => {
    const contacts = await ctx.db.query("contacts").collect();
    return contacts.filter(
      (c) =>
        c.jobLevel === "VP" ||
        c.jobLevel === "Executive" ||
        c.roleType === "Decision Maker"
    );
  },
});

// Get contacts by outreach status
export const getByOutreachStatus = query({
  args: { status: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contacts")
      .withIndex("by_outreach_status", (q) => q.eq("outreachStatus", args.status))
      .collect();
  },
});

// Get top contacts by persona score
export const getTopContacts = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const contacts = await ctx.db.query("contacts").collect();
    const sorted = contacts.sort((a, b) => b.personaScore - a.personaScore);
    return sorted.slice(0, args.limit || 50);
  },
});

// Search contacts
export const search = query({
  args: { searchTerm: v.string() },
  handler: async (ctx, args) => {
    const contacts = await ctx.db.query("contacts").collect();
    const term = args.searchTerm.toLowerCase();
    return contacts.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.title.toLowerCase().includes(term) ||
        c.companyName.toLowerCase().includes(term)
    );
  },
});

// ============ MUTATIONS ============

// Create a new contact
export const create = mutation({
  args: {
    companyId: v.id("companies"),
    companyName: v.string(),
    name: v.string(),
    title: v.string(),
    jobFunction: v.string(),
    jobLevel: v.string(),
    roleType: v.string(),
    linkedinUrl: v.optional(v.string()),
    email: v.optional(v.string()),
    location: v.optional(v.string()),
    personaScore: v.number(),
    source: v.string(),
    outreachStatus: v.optional(v.string()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("contacts", {
      ...args,
      outreachStatus: args.outreachStatus || "Not Contacted",
      lastContacted: undefined,
    });
  },
});

// Update contact
export const update = mutation({
  args: {
    id: v.id("contacts"),
    name: v.optional(v.string()),
    title: v.optional(v.string()),
    jobFunction: v.optional(v.string()),
    jobLevel: v.optional(v.string()),
    roleType: v.optional(v.string()),
    linkedinUrl: v.optional(v.string()),
    email: v.optional(v.string()),
    location: v.optional(v.string()),
    personaScore: v.optional(v.number()),
    outreachStatus: v.optional(v.string()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    const filteredUpdates = Object.fromEntries(
      Object.entries(updates).filter(([_, v]) => v !== undefined)
    );
    await ctx.db.patch(id, filteredUpdates);
  },
});

// Update outreach status
export const updateOutreachStatus = mutation({
  args: {
    id: v.id("contacts"),
    status: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      outreachStatus: args.status,
      lastContacted: Date.now(),
    });
  },
});

// Delete contact
export const remove = mutation({
  args: { id: v.id("contacts") },
  handler: async (ctx, args) => {
    // Delete related outreach first
    const outreach = await ctx.db
      .query("outreach")
      .withIndex("by_contact", (q) => q.eq("contactId", args.id))
      .collect();

    for (const o of outreach) {
      await ctx.db.delete(o._id);
    }

    await ctx.db.delete(args.id);
  },
});

// Bulk create contacts (for migration)
export const bulkCreate = mutation({
  args: {
    contacts: v.array(
      v.object({
        companyId: v.id("companies"),
        companyName: v.string(),
        name: v.string(),
        title: v.string(),
        jobFunction: v.string(),
        jobLevel: v.string(),
        roleType: v.string(),
        linkedinUrl: v.optional(v.string()),
        email: v.optional(v.string()),
        location: v.optional(v.string()),
        personaScore: v.number(),
        source: v.string(),
      })
    ),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const contact of args.contacts) {
      const id = await ctx.db.insert("contacts", {
        ...contact,
        outreachStatus: "Not Contacted",
        lastContacted: undefined,
        notes: undefined,
      });
      ids.push(id);
    }
    return ids;
  },
});
