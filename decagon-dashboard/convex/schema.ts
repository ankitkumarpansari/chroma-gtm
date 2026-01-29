import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Internal team members whose LinkedIn connections we track
  teamMembers: defineTable({
    name: v.string(),
    role: v.string(), // "CEO Office", "VP Sales", "AE", "SDR"
    department: v.optional(v.string()),
    linkedinUrl: v.string(),
    linkedinProfileId: v.optional(v.string()), // e.g., "dcliem"
    email: v.optional(v.string()),
    isActive: v.boolean(),
    connectionCount: v.optional(v.number()), // Total LinkedIn connections
    icpConnectionCount: v.optional(v.number()), // Connections matching ICP
    lastSyncedAt: v.optional(v.number()),
  })
    .index("by_linkedin_id", ["linkedinProfileId"])
    .index("by_role", ["role"])
    .index("by_active", ["isActive"]),

  // LinkedIn connections of team members matched against ICP
  linkedinConnections: defineTable({
    teamMemberId: v.id("teamMembers"), // Who on our team is connected
    teamMemberName: v.string(), // Denormalized for easier queries
    connectionName: v.string(),
    connectionTitle: v.string(),
    connectionCompany: v.optional(v.string()),
    connectionLinkedinUrl: v.string(),
    connectionLocation: v.optional(v.string()),
    matchedCompanyId: v.optional(v.id("companies")), // FK if matches ICP company
    matchedCompanyName: v.optional(v.string()), // Denormalized
    isIcpMatch: v.boolean(), // Quick filter flag
    connectionDegree: v.optional(v.number()), // 1st, 2nd degree
    warmIntroRequested: v.optional(v.boolean()),
    warmIntroRequestedAt: v.optional(v.number()),
    notes: v.optional(v.string()),
    extractedAt: v.number(),
  })
    .index("by_team_member", ["teamMemberId"])
    .index("by_company_match", ["matchedCompanyId"])
    .index("by_icp_match", ["isIcpMatch"])
    .index("by_connection_name", ["connectionName"])
    .index("by_linkedin_url", ["connectionLinkedinUrl"]),

  // Target companies we're prospecting, categorized by ICP (Ideal Customer Profile)
  companies: defineTable({
    name: v.string(),
    domain: v.optional(v.string()),
    icp: v.string(), // "ICP 1: Consumer Fintech", "ICP 2: Consumer SaaS", etc.
    priority: v.string(), // "Highest", "High", "Medium-High", "Strategic", "Emerging"
    signalStrength: v.string(), // "Very High", "High", "Medium-High", "Medium"
    whyFit: v.string(),
    decisionMakerTitles: v.string(),
    status: v.string(), // "New", "Researching", "Contacted", "Meeting Scheduled", "Proposal", "Closed Won", "Closed Lost"
    owner: v.optional(v.string()),
    notes: v.optional(v.string()),
    lastUpdated: v.number(), // timestamp
  })
    .index("by_icp", ["icp"])
    .index("by_status", ["status"])
    .index("by_priority", ["priority"])
    .index("by_name", ["name"]),

  // Contacts at target companies
  contacts: defineTable({
    companyId: v.id("companies"), // foreign key
    companyName: v.string(), // denormalized for easier queries
    name: v.string(),
    title: v.string(),
    jobFunction: v.string(), // "Customer Success", "Operations", "Support"
    jobLevel: v.string(), // "VP", "Director", "Manager", "Senior", "Individual Contributor", "Executive"
    roleType: v.string(), // "Decision Maker", "Influencer", "Champion", "User"
    linkedinUrl: v.optional(v.string()),
    email: v.optional(v.string()),
    location: v.optional(v.string()),
    personaScore: v.number(), // Higher = better fit
    source: v.string(), // "Sumble", "LinkedIn", "Apollo", "Manual"
    outreachStatus: v.string(), // "Not Contacted", "Email Sent", "LinkedIn Sent", "Replied", "Meeting Booked", "Not Interested"
    lastContacted: v.optional(v.number()),
    notes: v.optional(v.string()),
  })
    .index("by_company", ["companyId"])
    .index("by_job_level", ["jobLevel"])
    .index("by_persona_score", ["personaScore"])
    .index("by_outreach_status", ["outreachStatus"])
    .index("by_company_name", ["companyName"]),

  // Outreach activity tracking
  outreach: defineTable({
    contactId: v.id("contacts"),
    companyId: v.id("companies"),
    channel: v.string(), // "email", "linkedin", "phone", "meeting"
    messageType: v.string(), // "initial", "follow_up_1", "follow_up_2", "follow_up_3", "meeting_invite"
    subject: v.optional(v.string()),
    messageContent: v.optional(v.string()),
    sentAt: v.number(),
    response: v.optional(v.string()), // "opened", "clicked", "replied", "meeting_booked", "unsubscribed", "bounced"
    responseAt: v.optional(v.number()),
    responseContent: v.optional(v.string()),
  })
    .index("by_contact", ["contactId"])
    .index("by_company", ["companyId"])
    .index("by_sent_date", ["sentAt"])
    .index("by_channel", ["channel"]),

  // Company signals and research notes
  signals: defineTable({
    companyId: v.id("companies"),
    signalType: v.string(), // "hiring", "funding", "product_launch", "cx_investment", "leadership_change", "expansion"
    title: v.string(),
    description: v.string(),
    sourceUrl: v.optional(v.string()),
    discoveredAt: v.number(),
    relevanceScore: v.optional(v.number()), // 1-10
  })
    .index("by_company", ["companyId"])
    .index("by_type", ["signalType"])
    .index("by_discovered", ["discoveredAt"]),
});
