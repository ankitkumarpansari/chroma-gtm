import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ============ QUERIES ============

// Get all team members
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("teamMembers").order("desc").collect();
  },
});

// Get active team members
export const getActive = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("teamMembers")
      .withIndex("by_active", (q) => q.eq("isActive", true))
      .collect();
  },
});

// Get team member by LinkedIn profile ID
export const getByLinkedInId = query({
  args: { linkedinProfileId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("teamMembers")
      .withIndex("by_linkedin_id", (q) => q.eq("linkedinProfileId", args.linkedinProfileId))
      .first();
  },
});

// Get team members by role
export const getByRole = query({
  args: { role: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("teamMembers")
      .withIndex("by_role", (q) => q.eq("role", args.role))
      .collect();
  },
});

// Get team member with their connections
export const getWithConnections = query({
  args: { teamMemberId: v.id("teamMembers") },
  handler: async (ctx, args) => {
    const teamMember = await ctx.db.get(args.teamMemberId);
    if (!teamMember) return null;

    const connections = await ctx.db
      .query("linkedinConnections")
      .withIndex("by_team_member", (q) => q.eq("teamMemberId", args.teamMemberId))
      .collect();

    const icpConnections = connections.filter((c) => c.isIcpMatch);

    return {
      teamMember,
      connections,
      stats: {
        totalConnections: connections.length,
        icpMatches: icpConnections.length,
        companiesCovered: [...new Set(icpConnections.map((c) => c.matchedCompanyName).filter(Boolean))],
      },
    };
  },
});

// Get connection coverage stats for all team members
export const getConnectionCoverageStats = query({
  args: {},
  handler: async (ctx) => {
    const teamMembers = await ctx.db
      .query("teamMembers")
      .withIndex("by_active", (q) => q.eq("isActive", true))
      .collect();

    const stats = [];

    for (const member of teamMembers) {
      const connections = await ctx.db
        .query("linkedinConnections")
        .withIndex("by_team_member", (q) => q.eq("teamMemberId", member._id))
        .collect();

      const icpConnections = connections.filter((c) => c.isIcpMatch);

      stats.push({
        teamMember: member,
        totalConnections: connections.length,
        icpMatches: icpConnections.length,
        companies: [...new Set(icpConnections.map((c) => c.matchedCompanyName).filter(Boolean))],
      });
    }

    return stats.sort((a, b) => b.icpMatches - a.icpMatches);
  },
});

// ============ MUTATIONS ============

// Create a new team member
export const create = mutation({
  args: {
    name: v.string(),
    role: v.string(),
    linkedinUrl: v.string(),
    linkedinProfileId: v.optional(v.string()),
    department: v.optional(v.string()),
    email: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Extract profile ID from URL if not provided
    let profileId = args.linkedinProfileId;
    if (!profileId && args.linkedinUrl) {
      const match = args.linkedinUrl.match(/\/in\/([^\/\?]+)/);
      if (match) {
        profileId = match[1];
      }
    }

    return await ctx.db.insert("teamMembers", {
      ...args,
      linkedinProfileId: profileId,
      isActive: true,
      connectionCount: 0,
      icpConnectionCount: 0,
      lastSyncedAt: undefined,
    });
  },
});

// Update team member
export const update = mutation({
  args: {
    id: v.id("teamMembers"),
    name: v.optional(v.string()),
    role: v.optional(v.string()),
    department: v.optional(v.string()),
    linkedinUrl: v.optional(v.string()),
    email: v.optional(v.string()),
    isActive: v.optional(v.boolean()),
    connectionCount: v.optional(v.number()),
    icpConnectionCount: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    const filteredUpdates = Object.fromEntries(
      Object.entries(updates).filter(([_, v]) => v !== undefined)
    );
    await ctx.db.patch(id, filteredUpdates);
  },
});

// Update sync status after connection extraction
export const updateSyncStatus = mutation({
  args: {
    id: v.id("teamMembers"),
    connectionCount: v.number(),
    icpConnectionCount: v.number(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      connectionCount: args.connectionCount,
      icpConnectionCount: args.icpConnectionCount,
      lastSyncedAt: Date.now(),
    });
  },
});

// Delete team member
export const remove = mutation({
  args: { id: v.id("teamMembers") },
  handler: async (ctx, args) => {
    // Delete all their connections first
    const connections = await ctx.db
      .query("linkedinConnections")
      .withIndex("by_team_member", (q) => q.eq("teamMemberId", args.id))
      .collect();

    for (const conn of connections) {
      await ctx.db.delete(conn._id);
    }

    await ctx.db.delete(args.id);
  },
});

// Bulk create team members
export const bulkCreate = mutation({
  args: {
    members: v.array(
      v.object({
        name: v.string(),
        role: v.string(),
        linkedinUrl: v.string(),
        linkedinProfileId: v.optional(v.string()),
        department: v.optional(v.string()),
        email: v.optional(v.string()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const member of args.members) {
      // Extract profile ID from URL if not provided
      let profileId = member.linkedinProfileId;
      if (!profileId && member.linkedinUrl) {
        const match = member.linkedinUrl.match(/\/in\/([^\/\?]+)/);
        if (match) {
          profileId = match[1];
        }
      }

      const id = await ctx.db.insert("teamMembers", {
        ...member,
        linkedinProfileId: profileId,
        isActive: true,
        connectionCount: 0,
        icpConnectionCount: 0,
        lastSyncedAt: undefined,
      });
      ids.push({ name: member.name, id });
    }
    return ids;
  },
});
