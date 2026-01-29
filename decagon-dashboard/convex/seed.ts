import { mutation } from "./_generated/server";
import { v } from "convex/values";

// ============ HELPER FUNCTIONS ============

/**
 * Infer job level from title
 */
function inferJobLevel(title: string): string {
  const t = title.toLowerCase();

  if (
    t.includes("ceo") ||
    t.includes("cto") ||
    t.includes("cfo") ||
    t.includes("coo") ||
    t.includes("chief")
  ) {
    return "Executive";
  }
  if (t.includes("executive director")) return "Executive";
  if (t.includes("managing director")) return "Executive";
  if (t.includes("president") && !t.includes("vice president")) return "Executive";
  if (t.includes("vice president") || t.includes("vp,") || t.includes("vp ")) return "VP";
  if (t.includes("director") && !t.includes("managing")) return "Director";
  if (t.includes("head of")) return "Director";
  if (t.includes("manager")) return "Manager";
  if (t.includes("lead") || t.includes("principal") || t.includes("senior")) return "Senior";
  if (t.includes("analyst") || t.includes("associate") || t.includes("engineer")) {
    return "Individual Contributor";
  }
  return "Unknown";
}

/**
 * Infer job function from title
 */
function inferJobFunction(title: string): string {
  const t = title.toLowerCase();

  if (t.includes("product")) return "Product";
  if (t.includes("engineering") || t.includes("software") || t.includes("developer")) {
    return "Engineering";
  }
  if (t.includes("ux") || t.includes("design") || t.includes("experience")) return "Design/UX";
  if (t.includes("customer success") || t.includes("cx") || t.includes("support")) {
    return "Customer Success";
  }
  if (t.includes("operations") || t.includes("ops")) return "Operations";
  if (t.includes("innovation") || t.includes("strategy") || t.includes("strategic")) {
    return "Strategy/Innovation";
  }
  if (t.includes("fintech") || t.includes("investment") || t.includes("banking")) {
    return "Banking/Finance";
  }
  if (t.includes("marketing")) return "Marketing";
  if (t.includes("sales")) return "Sales";
  if (t.includes("event")) return "Events";
  if (t.includes("content")) return "Content";
  return "General Management";
}

/**
 * Infer role type
 */
function inferRoleType(jobLevel: string, title: string): string {
  const t = title.toLowerCase();

  if (jobLevel === "Executive" || jobLevel === "VP") return "Decision Maker";
  if (jobLevel === "Director") {
    if (t.includes("strategy") || t.includes("innovation") || t.includes("product")) {
      return "Decision Maker";
    }
    return "Influencer";
  }
  if (jobLevel === "Manager" || jobLevel === "Senior") return "Influencer";
  if (t.includes("analyst") || t.includes("associate")) return "Champion";
  return "User";
}

/**
 * Calculate persona score
 */
function calculatePersonaScore(
  jobLevel: string,
  jobFunction: string,
  roleType: string
): number {
  let score = 50;

  switch (jobLevel) {
    case "Executive": score += 30; break;
    case "VP": score += 25; break;
    case "Director": score += 20; break;
    case "Manager": score += 10; break;
    case "Senior": score += 5; break;
  }

  switch (jobFunction) {
    case "Strategy/Innovation": score += 15; break;
    case "Product": score += 12; break;
    case "Customer Success": score += 12; break;
    case "Engineering": score += 10; break;
    case "Design/UX": score += 8; break;
    case "Operations": score += 5; break;
  }

  if (roleType === "Decision Maker") score += 5;

  return Math.min(score, 100);
}

// ============ JPMORGAN LEADS DATA ============

const JPMORGAN_LEADS = [
  { name: "Erik Larson", title: "Executive Director, Product - CMAS Strategic Initiatives", linkedin: "https://www.linkedin.com/sales/lead/ACwAAAAOCrMBvv1B7FOFUrr-MzLeFnhSbJKW_U4" },
  { name: "Tuan P.", title: "Managing Director", linkedin: "https://www.linkedin.com/sales/lead/ACwAAABvn34BSR10Wrd3CfqVu0IK7yVctLTD4eA" },
  { name: "Shikha Goyal-Allain", title: "Managing Director & Bay Area Market Executive, Innovation Economy - Technology", linkedin: "https://www.linkedin.com/sales/lead/ACwAAACCNswBfy3G8Ae6UnHt-tC4cT7oK8SqFZw" },
  { name: "Lucy Wang", title: "Managing Director", linkedin: "https://www.linkedin.com/sales/lead/ACwAAAFwqpMBvgrlRX0zL_9Zo1GOpIfzmv5s3ho" },
  { name: "Keo Buenpacífico", title: "Vice President, Innovation Economy, Technology", linkedin: "https://www.linkedin.com/sales/lead/ACwAAAmT-XIBpB25bpZTcjpXhDCedUZ0WZzHwbc" },
  { name: "LeAnn Haun", title: "Senior Events Management Associate", linkedin: "https://www.linkedin.com/sales/lead/ACwAAArAAR8BMmQO7pC1H2aQXgBFv1pNq17RbWU" },
  { name: "Andrew Wang", title: "VP, Product Management", linkedin: "https://www.linkedin.com/sales/lead/ACwAAA2quAQBJiiBF3iNfyffpNjSBZ7Q0miUhxE" },
  { name: "Astrid A. Tagariello", title: "Vice President, UX Content Strategy Team Lead", linkedin: "https://www.linkedin.com/sales/lead/ACwAAA-yxmYBQ9N75lluD_xsfUVDEz0uDwPdL6g" },
  { name: "Colby Lennon", title: "Vice President, Firmwide Innovation Strategy", linkedin: "https://www.linkedin.com/sales/lead/ACwAABAeGjcBfKnUyj3glH2wrWWDSnTtsR6IQBY" },
  { name: "Melina Bergkamp", title: "Executive Director", linkedin: "https://www.linkedin.com/sales/lead/ACwAABCVWcAB9BphiAC95NQrWA9oFObf6JCq-lY" },
  { name: "Jake Marrello", title: "Vice President", linkedin: "https://www.linkedin.com/sales/lead/ACwAACB2KugBxZf4q8w9mMWcjxexcsU4QZkcWKc" },
  { name: "Jade Nguyen", title: "Experience Design Development Analyst", linkedin: "https://www.linkedin.com/sales/lead/ACwAACMCJ3MBCBsy2ufNB8JPxiuoT06mt1513nY" },
  { name: "Patrick Steed", title: "Senior Associate, FinTech Investments & Partnerships", linkedin: "https://www.linkedin.com/sales/lead/ACwAACNdL04Bl_yFA2xNVAODMaZpEoWYyDrARJ0" },
  { name: "Katrina Samonte", title: "Commercial Banker, Vice President - Global Passport Banking", linkedin: "https://www.linkedin.com/sales/lead/ACwAACTvPrIB42lOaOLVhxRVtiwuRkJ3xzBjtuk" },
  { name: "Taylor Weinberg Rosen", title: "Executive Director", linkedin: "https://www.linkedin.com/sales/lead/ACwAACoMN3cB6PUiIMHZ2w5-gLJJ8BGnwOTTEDU" },
  { name: "Ali N.", title: "Software Engineer", linkedin: "https://www.linkedin.com/sales/lead/ACwAACrXYvgBCw9E_lvsHJtF2XRmxsoR1sPpeOY" },
];

// ============ SEED MUTATION ============

/**
 * Seed JPMorgan Chase company and contacts
 * Run via: npx convex run seed:seedJPMorganLeads
 */
export const seedJPMorganLeads = mutation({
  args: {},
  handler: async (ctx) => {
    const companyName = "JPMorgan Chase";

    // Check if company already exists
    const existingCompanies = await ctx.db
      .query("companies")
      .withIndex("by_name", (q) => q.eq("name", companyName))
      .collect();

    let companyId;

    if (existingCompanies.length > 0) {
      companyId = existingCompanies[0]._id;
      console.log(`Found existing company: ${companyId}`);
    } else {
      // Create the company
      companyId = await ctx.db.insert("companies", {
        name: companyName,
        domain: "jpmorgan.com",
        icp: "ICP 4: Enterprise Financial Services",
        priority: "Highest",
        signalStrength: "High",
        whyFit: "Major enterprise bank with large CX/support operations, innovation teams actively exploring AI for customer experience",
        decisionMakerTitles: "VP, Managing Director, Executive Director",
        status: "Researching",
        lastUpdated: Date.now(),
      });
      console.log(`Created company: ${companyId}`);
    }

    // Import contacts
    const contactIds = [];
    for (const lead of JPMORGAN_LEADS) {
      const jobLevel = inferJobLevel(lead.title);
      const jobFunction = inferJobFunction(lead.title);
      const roleType = inferRoleType(jobLevel, lead.title);
      const personaScore = calculatePersonaScore(jobLevel, jobFunction, roleType);

      const contactId = await ctx.db.insert("contacts", {
        companyId,
        companyName,
        name: lead.name,
        title: lead.title,
        jobFunction,
        jobLevel,
        roleType,
        linkedinUrl: lead.linkedin,
        email: undefined,
        location: undefined,
        personaScore,
        source: "LinkedIn",
        outreachStatus: "Not Contacted",
        lastContacted: undefined,
        notes: undefined,
      });
      contactIds.push(contactId);
    }

    return {
      companyId,
      contactsImported: contactIds.length,
      message: `Successfully imported ${contactIds.length} JPMorgan Chase contacts`,
    };
  },
});

/**
 * Import leads from raw data
 * Can be called with custom company and leads data
 */
export const importLeads = mutation({
  args: {
    company: v.object({
      name: v.string(),
      domain: v.optional(v.string()),
      icp: v.string(),
      priority: v.string(),
      signalStrength: v.string(),
      whyFit: v.string(),
      decisionMakerTitles: v.string(),
      status: v.string(),
    }),
    leads: v.array(
      v.object({
        name: v.string(),
        title: v.string(),
        linkedin: v.optional(v.string()),
        email: v.optional(v.string()),
        location: v.optional(v.string()),
      })
    ),
  },
  handler: async (ctx, args) => {
    // Check if company exists
    const existingCompanies = await ctx.db
      .query("companies")
      .withIndex("by_name", (q) => q.eq("name", args.company.name))
      .collect();

    let companyId;

    if (existingCompanies.length > 0) {
      companyId = existingCompanies[0]._id;
    } else {
      companyId = await ctx.db.insert("companies", {
        ...args.company,
        lastUpdated: Date.now(),
      });
    }

    // Import contacts
    const contactIds = [];
    for (const lead of args.leads) {
      const jobLevel = inferJobLevel(lead.title);
      const jobFunction = inferJobFunction(lead.title);
      const roleType = inferRoleType(jobLevel, lead.title);
      const personaScore = calculatePersonaScore(jobLevel, jobFunction, roleType);

      const contactId = await ctx.db.insert("contacts", {
        companyId,
        companyName: args.company.name,
        name: lead.name,
        title: lead.title,
        jobFunction,
        jobLevel,
        roleType,
        linkedinUrl: lead.linkedin,
        email: lead.email,
        location: lead.location,
        personaScore,
        source: "LinkedIn",
        outreachStatus: "Not Contacted",
        lastContacted: undefined,
        notes: undefined,
      });
      contactIds.push(contactId);
    }

    return {
      companyId,
      contactsImported: contactIds.length,
    };
  },
});

// ============ TEAM MEMBERS & LINKEDIN CONNECTIONS SEED ============

/**
 * Seed a team member with their LinkedIn connections
 * Run via: npx convex run seed:seedTeamMemberConnections
 */
export const seedTeamMemberConnections = mutation({
  args: {
    teamMember: v.object({
      name: v.string(),
      role: v.string(),
      linkedinUrl: v.string(),
      linkedinProfileId: v.optional(v.string()),
      department: v.optional(v.string()),
      email: v.optional(v.string()),
    }),
    connections: v.array(
      v.object({
        name: v.string(),
        title: v.string(),
        linkedin: v.string(),
        company: v.optional(v.string()),
        location: v.optional(v.string()),
      })
    ),
  },
  handler: async (ctx, args) => {
    // Check if team member already exists
    const profileId = args.teamMember.linkedinProfileId || 
      args.teamMember.linkedinUrl.match(/\/in\/([^\/\?]+)/)?.[1];
    
    let teamMemberId;
    
    if (profileId) {
      const existing = await ctx.db
        .query("teamMembers")
        .withIndex("by_linkedin_id", (q) => q.eq("linkedinProfileId", profileId))
        .first();
      
      if (existing) {
        teamMemberId = existing._id;
        console.log(`Found existing team member: ${existing.name}`);
      }
    }
    
    if (!teamMemberId) {
      teamMemberId = await ctx.db.insert("teamMembers", {
        ...args.teamMember,
        linkedinProfileId: profileId,
        isActive: true,
        connectionCount: 0,
        icpConnectionCount: 0,
        lastSyncedAt: undefined,
      });
      console.log(`Created team member: ${args.teamMember.name}`);
    }

    // Get all ICP companies for matching
    const companies = await ctx.db.query("companies").collect();
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

    // Import connections
    let icpMatches = 0;
    const connectionIds = [];
    
    for (const conn of args.connections) {
      // Try to extract company from title if not provided
      let company = conn.company || "";
      if (!company && conn.title) {
        const match = conn.title.match(/(?:at|@|-|\|)\s+(.+)$/i);
        if (match) {
          company = match[1].trim();
        }
      }
      
      // Check if company matches ICP
      const normalizedCompany = company.toLowerCase().trim();
      const withoutSuffix = normalizedCompany.replace(/\s*(inc\.?|llc\.?|corp\.?|ltd\.?)$/i, '').trim();
      const match = companyLookup.get(normalizedCompany) || companyLookup.get(withoutSuffix);
      
      const isIcpMatch = !!match;
      if (isIcpMatch) icpMatches++;
      
      const connectionId = await ctx.db.insert("linkedinConnections", {
        teamMemberId,
        teamMemberName: args.teamMember.name,
        connectionName: conn.name,
        connectionTitle: conn.title,
        connectionCompany: company,
        connectionLinkedinUrl: conn.linkedin,
        connectionLocation: conn.location,
        matchedCompanyId: match?.id as any,
        matchedCompanyName: match?.name,
        isIcpMatch,
        warmIntroRequested: false,
        extractedAt: Date.now(),
      });
      connectionIds.push(connectionId);
    }

    // Update team member stats
    await ctx.db.patch(teamMemberId, {
      connectionCount: connectionIds.length,
      icpConnectionCount: icpMatches,
      lastSyncedAt: Date.now(),
    });

    return {
      teamMemberId,
      connectionsImported: connectionIds.length,
      icpMatches,
      message: `Imported ${connectionIds.length} connections for ${args.teamMember.name} (${icpMatches} ICP matches)`,
    };
  },
});

/**
 * Seed David Cliem's connections (sample data from the user)
 * Run via: npx convex run seed:seedDcliemConnections
 */
export const seedDcliemConnections = mutation({
  args: {},
  handler: async (ctx) => {
    const teamMember = {
      name: "David Cliem",
      role: "CEO Office",
      linkedinUrl: "https://www.linkedin.com/in/dcliem/",
      linkedinProfileId: "dcliem",
      department: "Executive",
    };

    const connections = JPMORGAN_LEADS.map((lead) => ({
      name: lead.name,
      title: lead.title,
      linkedin: lead.linkedin,
      company: "JPMorgan Chase", // These are all JPMorgan contacts
    }));

    // Check if team member already exists
    let teamMemberId;
    const existing = await ctx.db
      .query("teamMembers")
      .withIndex("by_linkedin_id", (q) => q.eq("linkedinProfileId", "dcliem"))
      .first();

    if (existing) {
      teamMemberId = existing._id;
      console.log(`Found existing team member: ${existing.name}`);
    } else {
      teamMemberId = await ctx.db.insert("teamMembers", {
        ...teamMember,
        isActive: true,
        connectionCount: 0,
        icpConnectionCount: 0,
        lastSyncedAt: undefined,
      });
      console.log(`Created team member: ${teamMember.name}`);
    }

    // Get JPMorgan company ID if it exists
    const jpmorgan = await ctx.db
      .query("companies")
      .withIndex("by_name", (q) => q.eq("name", "JPMorgan Chase"))
      .first();

    // Import connections
    const connectionIds = [];
    for (const conn of connections) {
      const connectionId = await ctx.db.insert("linkedinConnections", {
        teamMemberId,
        teamMemberName: teamMember.name,
        connectionName: conn.name,
        connectionTitle: conn.title,
        connectionCompany: conn.company,
        connectionLinkedinUrl: conn.linkedin,
        connectionLocation: undefined,
        matchedCompanyId: jpmorgan?._id,
        matchedCompanyName: jpmorgan?.name,
        isIcpMatch: !!jpmorgan,
        warmIntroRequested: false,
        extractedAt: Date.now(),
      });
      connectionIds.push(connectionId);
    }

    // Update team member stats
    await ctx.db.patch(teamMemberId, {
      connectionCount: connectionIds.length,
      icpConnectionCount: jpmorgan ? connectionIds.length : 0,
      lastSyncedAt: Date.now(),
    });

    return {
      teamMemberId,
      connectionsImported: connectionIds.length,
      icpMatches: jpmorgan ? connectionIds.length : 0,
      message: `Imported ${connectionIds.length} JPMorgan connections for David Cliem`,
    };
  },
});
