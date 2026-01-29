import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ============ QUERIES ============

// Get all connections
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("linkedinConnections").order("desc").collect();
  },
});

// Get connections by team member
export const getByTeamMember = query({
  args: { teamMemberId: v.id("teamMembers") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("linkedinConnections")
      .withIndex("by_team_member", (q) => q.eq("teamMemberId", args.teamMemberId))
      .collect();
  },
});

// Get ICP-matched connections only
export const getIcpMatches = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("linkedinConnections")
      .withIndex("by_icp_match", (q) => q.eq("isIcpMatch", true))
      .collect();
  },
});

// Get connections for a specific ICP company
export const getByCompany = query({
  args: { companyId: v.id("companies") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("linkedinConnections")
      .withIndex("by_company_match", (q) => q.eq("matchedCompanyId", args.companyId))
      .collect();
  },
});

// Get warm intro paths - who can introduce us to a company?
export const getWarmIntros = query({
  args: { companyId: v.id("companies") },
  handler: async (ctx, args) => {
    const company = await ctx.db.get(args.companyId);
    if (!company) return null;

    const connections = await ctx.db
      .query("linkedinConnections")
      .withIndex("by_company_match", (q) => q.eq("matchedCompanyId", args.companyId))
      .collect();

    // Enrich with team member details
    const enrichedConnections = await Promise.all(
      connections.map(async (conn) => {
        const teamMember = await ctx.db.get(conn.teamMemberId);
        return {
          ...conn,
          teamMember,
        };
      })
    );

    return {
      company,
      warmIntros: enrichedConnections,
      totalPaths: connections.length,
    };
  },
});

// Search connections by name
export const search = query({
  args: { searchTerm: v.string() },
  handler: async (ctx, args) => {
    const connections = await ctx.db.query("linkedinConnections").collect();
    const term = args.searchTerm.toLowerCase();
    return connections.filter(
      (c) =>
        c.connectionName.toLowerCase().includes(term) ||
        c.connectionTitle.toLowerCase().includes(term) ||
        (c.connectionCompany && c.connectionCompany.toLowerCase().includes(term))
    );
  },
});

// Get connection coverage summary - which ICP companies do we have connections at?
export const getCoverageSummary = query({
  args: {},
  handler: async (ctx) => {
    const icpConnections = await ctx.db
      .query("linkedinConnections")
      .withIndex("by_icp_match", (q) => q.eq("isIcpMatch", true))
      .collect();

    // Group by company
    const byCompany: Record<string, { companyId: string; companyName: string; connections: typeof icpConnections }> = {};

    for (const conn of icpConnections) {
      if (conn.matchedCompanyId && conn.matchedCompanyName) {
        const key = conn.matchedCompanyId;
        if (!byCompany[key]) {
          byCompany[key] = {
            companyId: conn.matchedCompanyId,
            companyName: conn.matchedCompanyName,
            connections: [],
          };
        }
        byCompany[key].connections.push(conn);
      }
    }

    // Convert to array and sort by connection count
    const coverage = Object.values(byCompany)
      .map((c) => ({
        companyId: c.companyId,
        companyName: c.companyName,
        connectionCount: c.connections.length,
        teamMembers: [...new Set(c.connections.map((conn) => conn.teamMemberName))],
        topConnections: c.connections.slice(0, 3).map((conn) => ({
          name: conn.connectionName,
          title: conn.connectionTitle,
          teamMember: conn.teamMemberName,
        })),
      }))
      .sort((a, b) => b.connectionCount - a.connectionCount);

    return {
      totalCompaniesWithConnections: coverage.length,
      totalIcpConnections: icpConnections.length,
      coverage,
    };
  },
});

// ============ MUTATIONS ============

// Create a new connection
export const create = mutation({
  args: {
    teamMemberId: v.id("teamMembers"),
    teamMemberName: v.string(),
    connectionName: v.string(),
    connectionTitle: v.string(),
    connectionCompany: v.optional(v.string()),
    connectionLinkedinUrl: v.string(),
    connectionLocation: v.optional(v.string()),
    matchedCompanyId: v.optional(v.id("companies")),
    matchedCompanyName: v.optional(v.string()),
    isIcpMatch: v.boolean(),
    connectionDegree: v.optional(v.number()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Check for duplicate by LinkedIn URL
    const existing = await ctx.db
      .query("linkedinConnections")
      .withIndex("by_linkedin_url", (q) => q.eq("connectionLinkedinUrl", args.connectionLinkedinUrl))
      .first();

    if (existing && existing.teamMemberId === args.teamMemberId) {
      // Update existing instead of creating duplicate
      await ctx.db.patch(existing._id, {
        ...args,
        extractedAt: Date.now(),
      });
      return existing._id;
    }

    return await ctx.db.insert("linkedinConnections", {
      ...args,
      warmIntroRequested: false,
      extractedAt: Date.now(),
    });
  },
});

// Bulk create connections (for import)
export const bulkCreate = mutation({
  args: {
    connections: v.array(
      v.object({
        teamMemberId: v.id("teamMembers"),
        teamMemberName: v.string(),
        connectionName: v.string(),
        connectionTitle: v.string(),
        connectionCompany: v.optional(v.string()),
        connectionLinkedinUrl: v.string(),
        connectionLocation: v.optional(v.string()),
        matchedCompanyId: v.optional(v.id("companies")),
        matchedCompanyName: v.optional(v.string()),
        isIcpMatch: v.boolean(),
        connectionDegree: v.optional(v.number()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const results = { created: 0, updated: 0, skipped: 0 };

    for (const conn of args.connections) {
      // Check for duplicate by LinkedIn URL and team member
      const existing = await ctx.db
        .query("linkedinConnections")
        .withIndex("by_linkedin_url", (q) => q.eq("connectionLinkedinUrl", conn.connectionLinkedinUrl))
        .first();

      if (existing && existing.teamMemberId === conn.teamMemberId) {
        // Update existing
        await ctx.db.patch(existing._id, {
          ...conn,
          extractedAt: Date.now(),
        });
        results.updated++;
      } else if (existing) {
        // Different team member has this connection - create new
        await ctx.db.insert("linkedinConnections", {
          ...conn,
          warmIntroRequested: false,
          extractedAt: Date.now(),
        });
        results.created++;
      } else {
        // New connection
        await ctx.db.insert("linkedinConnections", {
          ...conn,
          warmIntroRequested: false,
          extractedAt: Date.now(),
        });
        results.created++;
      }
    }

    return results;
  },
});

// Request a warm intro
export const requestWarmIntro = mutation({
  args: {
    id: v.id("linkedinConnections"),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      warmIntroRequested: true,
      warmIntroRequestedAt: Date.now(),
      notes: args.notes,
    });
  },
});

// Update connection
export const update = mutation({
  args: {
    id: v.id("linkedinConnections"),
    connectionTitle: v.optional(v.string()),
    connectionCompany: v.optional(v.string()),
    matchedCompanyId: v.optional(v.id("companies")),
    matchedCompanyName: v.optional(v.string()),
    isIcpMatch: v.optional(v.boolean()),
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

// Delete connection
export const remove = mutation({
  args: { id: v.id("linkedinConnections") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// Delete all connections for a team member (for re-sync)
export const removeByTeamMember = mutation({
  args: { teamMemberId: v.id("teamMembers") },
  handler: async (ctx, args) => {
    const connections = await ctx.db
      .query("linkedinConnections")
      .withIndex("by_team_member", (q) => q.eq("teamMemberId", args.teamMemberId))
      .collect();

    for (const conn of connections) {
      await ctx.db.delete(conn._id);
    }

    return { deleted: connections.length };
  },
});

// Match connections against ICP companies (for re-matching after ICP changes)
export const rematchIcp = mutation({
  args: {},
  handler: async (ctx) => {
    const connections = await ctx.db.query("linkedinConnections").collect();
    const companies = await ctx.db.query("companies").collect();

    // Create company name lookup (normalized)
    const companyLookup = new Map<string, { id: string; name: string }>();
    for (const company of companies) {
      const normalized = company.name.toLowerCase().trim();
      companyLookup.set(normalized, { id: company._id, name: company.name });
      
      // Also add without common suffixes
      const withoutSuffix = normalized.replace(/\s*(inc\.?|llc\.?|corp\.?|ltd\.?)$/i, '').trim();
      if (withoutSuffix !== normalized) {
        companyLookup.set(withoutSuffix, { id: company._id, name: company.name });
      }
    }

    let matched = 0;
    let unmatched = 0;

    for (const conn of connections) {
      if (!conn.connectionCompany) {
        continue;
      }

      const normalized = conn.connectionCompany.toLowerCase().trim();
      const withoutSuffix = normalized.replace(/\s*(inc\.?|llc\.?|corp\.?|ltd\.?)$/i, '').trim();

      const match = companyLookup.get(normalized) || companyLookup.get(withoutSuffix);

      if (match) {
        await ctx.db.patch(conn._id, {
          isIcpMatch: true,
          matchedCompanyId: match.id as any,
          matchedCompanyName: match.name,
        });
        matched++;
      } else if (conn.isIcpMatch) {
        // Was matched but no longer matches
        await ctx.db.patch(conn._id, {
          isIcpMatch: false,
          matchedCompanyId: undefined,
          matchedCompanyName: undefined,
        });
        unmatched++;
      }
    }

    return { matched, unmatched, total: connections.length };
  },
});
