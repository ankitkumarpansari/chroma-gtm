import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ============ QUERIES ============

// Get all outreach activities
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("outreach").order("desc").collect();
  },
});

// Get outreach by contact
export const getByContact = query({
  args: { contactId: v.id("contacts") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("outreach")
      .withIndex("by_contact", (q) => q.eq("contactId", args.contactId))
      .order("desc")
      .collect();
  },
});

// Get outreach by company
export const getByCompany = query({
  args: { companyId: v.id("companies") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("outreach")
      .withIndex("by_company", (q) => q.eq("companyId", args.companyId))
      .order("desc")
      .collect();
  },
});

// Get recent outreach
export const getRecent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("outreach")
      .order("desc")
      .take(args.limit || 50);
  },
});

// Get outreach stats
export const getStats = query({
  args: {},
  handler: async (ctx) => {
    const outreach = await ctx.db.query("outreach").collect();

    const byChannel: Record<string, number> = {};
    const byResponse: Record<string, number> = {};
    let totalSent = 0;
    let totalReplied = 0;

    for (const o of outreach) {
      byChannel[o.channel] = (byChannel[o.channel] || 0) + 1;
      totalSent++;
      if (o.response) {
        byResponse[o.response] = (byResponse[o.response] || 0) + 1;
        if (o.response === "replied" || o.response === "meeting_booked") {
          totalReplied++;
        }
      }
    }

    return {
      totalSent,
      totalReplied,
      replyRate: totalSent > 0 ? (totalReplied / totalSent) * 100 : 0,
      byChannel,
      byResponse,
    };
  },
});

// ============ MUTATIONS ============

// Log new outreach
export const create = mutation({
  args: {
    contactId: v.id("contacts"),
    companyId: v.id("companies"),
    channel: v.string(),
    messageType: v.string(),
    subject: v.optional(v.string()),
    messageContent: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Create outreach record
    const id = await ctx.db.insert("outreach", {
      ...args,
      sentAt: Date.now(),
      response: undefined,
      responseAt: undefined,
      responseContent: undefined,
    });

    // Update contact's outreach status
    await ctx.db.patch(args.contactId, {
      outreachStatus:
        args.channel === "email" ? "Email Sent" : "LinkedIn Sent",
      lastContacted: Date.now(),
    });

    return id;
  },
});

// Record response
export const recordResponse = mutation({
  args: {
    id: v.id("outreach"),
    response: v.string(),
    responseContent: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const outreach = await ctx.db.get(args.id);
    if (!outreach) return;

    await ctx.db.patch(args.id, {
      response: args.response,
      responseAt: Date.now(),
      responseContent: args.responseContent,
    });

    // Update contact status based on response
    let newStatus = "Replied";
    if (args.response === "meeting_booked") {
      newStatus = "Meeting Booked";
    } else if (args.response === "unsubscribed" || args.response === "bounced") {
      newStatus = "Not Interested";
    }

    await ctx.db.patch(outreach.contactId, {
      outreachStatus: newStatus,
    });
  },
});

// Delete outreach
export const remove = mutation({
  args: { id: v.id("outreach") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
