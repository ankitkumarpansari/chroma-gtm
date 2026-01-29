/**
 * Import LinkedIn Sales Navigator leads into Convex
 *
 * Usage:
 * 1. First run `npx convex dev` to start Convex and get your deployment URL
 * 2. Set CONVEX_URL environment variable
 * 3. Run `npx tsx scripts/import-linkedin-leads.ts`
 *
 * Or use: npm run import:leads
 */

import { ConvexHttpClient } from "convex/browser";
import { api } from "../convex/_generated/api";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

// ES Module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration - update this for each import
const CONFIG = {
  // CSV file path (relative to data directory)
  csvFile: "jpmorgan_leads.csv",

  // Company details (will be created if doesn't exist)
  company: {
    name: "JPMorgan Chase",
    domain: "jpmorgan.com",
    icp: "ICP 4: Enterprise Financial Services",
    priority: "Highest",
    signalStrength: "High",
    whyFit:
      "Major enterprise bank with large CX/support operations, innovation teams actively exploring AI for customer experience",
    decisionMakerTitles: "VP, Managing Director, Executive Director",
    status: "Researching",
  },
};

// Data directory
const DATA_DIR = path.join(__dirname, "../../data/decagon_discovery");
const CSV_PATH = path.join(DATA_DIR, CONFIG.csvFile);

// Initialize Convex client
const convexUrl = process.env.CONVEX_URL;
if (!convexUrl) {
  console.error("Error: CONVEX_URL environment variable not set");
  console.error("Run `npx convex dev` and copy the deployment URL");
  process.exit(1);
}

const client = new ConvexHttpClient(convexUrl);

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
  if (t.includes("executive director")) {
    return "Executive";
  }
  if (t.includes("managing director")) {
    return "Executive";
  }
  if (t.includes("president") && !t.includes("vice president")) {
    return "Executive";
  }
  if (t.includes("vice president") || t.includes("vp,") || t.includes("vp ")) {
    return "VP";
  }
  if (t.includes("director") && !t.includes("managing")) {
    return "Director";
  }
  if (t.includes("head of")) {
    return "Director";
  }
  if (t.includes("manager")) {
    return "Manager";
  }
  if (t.includes("lead") || t.includes("principal") || t.includes("senior")) {
    return "Senior";
  }
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
  if (t.includes("ux") || t.includes("design") || t.includes("experience")) {
    return "Design/UX";
  }
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
 * Infer role type (Decision Maker, Influencer, Champion, User)
 */
function inferRoleType(jobLevel: string, title: string): string {
  const t = title.toLowerCase();

  if (jobLevel === "Executive" || jobLevel === "VP") {
    return "Decision Maker";
  }
  if (jobLevel === "Director") {
    // Directors in strategy/innovation are often decision makers
    if (t.includes("strategy") || t.includes("innovation") || t.includes("product")) {
      return "Decision Maker";
    }
    return "Influencer";
  }
  if (jobLevel === "Manager" || jobLevel === "Senior") {
    return "Influencer";
  }
  if (t.includes("analyst") || t.includes("associate")) {
    return "Champion";
  }

  return "User";
}

/**
 * Calculate persona score based on title relevance for AI/CX solutions
 */
function calculatePersonaScore(
  jobLevel: string,
  jobFunction: string,
  roleType: string
): number {
  let score = 50; // Base score

  // Job level scoring
  switch (jobLevel) {
    case "Executive":
      score += 30;
      break;
    case "VP":
      score += 25;
      break;
    case "Director":
      score += 20;
      break;
    case "Manager":
      score += 10;
      break;
    case "Senior":
      score += 5;
      break;
  }

  // Job function scoring (relevance to AI/CX solutions)
  switch (jobFunction) {
    case "Strategy/Innovation":
      score += 15;
      break;
    case "Product":
      score += 12;
      break;
    case "Customer Success":
      score += 12;
      break;
    case "Engineering":
      score += 10;
      break;
    case "Design/UX":
      score += 8;
      break;
    case "Operations":
      score += 5;
      break;
  }

  // Role type bonus
  if (roleType === "Decision Maker") {
    score += 5;
  }

  return Math.min(score, 100); // Cap at 100
}

/**
 * Parse CSV with proper handling of quoted fields
 */
function parseCSV(content: string): Record<string, string>[] {
  const lines = content.trim().split("\n");
  const headers = parseCSVLine(lines[0]);

  return lines.slice(1).map((line) => {
    const values = parseCSVLine(line);
    const row: Record<string, string> = {};
    headers.forEach((header, i) => {
      row[header] = values[i] || "";
    });
    return row;
  });
}

function parseCSVLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let inQuotes = false;

  for (const char of line) {
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current.trim());

  return values;
}

// ============ MAIN IMPORT LOGIC ============

async function findOrCreateCompany(): Promise<string> {
  console.log(`🏢 Setting up company: ${CONFIG.company.name}`);

  // Search for existing company
  const existing = await client.query(api.companies.search, {
    searchTerm: CONFIG.company.name,
  });

  if (existing && existing.length > 0) {
    const match = existing.find(
      (c: any) => c.name.toLowerCase() === CONFIG.company.name.toLowerCase()
    );
    if (match) {
      console.log(`  ✓ Found existing company: ${match._id}`);
      return match._id;
    }
  }

  // Create new company
  const companyId = await client.mutation(api.companies.create, CONFIG.company);
  console.log(`  ✓ Created new company: ${companyId}`);
  return companyId;
}

async function importContacts(companyId: string): Promise<void> {
  console.log(`\n📇 Importing contacts from ${CONFIG.csvFile}`);

  if (!fs.existsSync(CSV_PATH)) {
    console.error(`  ❌ CSV file not found: ${CSV_PATH}`);
    process.exit(1);
  }

  const csvContent = fs.readFileSync(CSV_PATH, "utf-8");
  const rows = parseCSV(csvContent);

  console.log(`  Found ${rows.length} contacts in CSV`);

  const contacts = rows
    .filter((row) => row.Name && row.Name.trim())
    .map((row) => {
      const title = row.Designation || row.Title || "";
      const jobLevel = inferJobLevel(title);
      const jobFunction = inferJobFunction(title);
      const roleType = inferRoleType(jobLevel, title);
      const personaScore = calculatePersonaScore(jobLevel, jobFunction, roleType);

      return {
        companyId: companyId as any,
        companyName: CONFIG.company.name,
        name: row.Name,
        title: title,
        jobFunction,
        jobLevel,
        roleType,
        linkedinUrl: row["LinkedIn Profile URL"] || row.LinkedIn || undefined,
        email: row.Email || undefined,
        location: row.Location || undefined,
        personaScore,
        source: "LinkedIn",
      };
    });

  if (contacts.length === 0) {
    console.log("  ⚠️ No valid contacts found in CSV");
    return;
  }

  // Import in batches
  const batchSize = 50;
  let imported = 0;

  for (let i = 0; i < contacts.length; i += batchSize) {
    const batch = contacts.slice(i, i + batchSize);
    await client.mutation(api.contacts.bulkCreate, { contacts: batch });
    imported += batch.length;
    console.log(
      `  ✓ Imported ${batch.length} contacts (batch ${Math.floor(i / batchSize) + 1})`
    );
  }

  console.log(`\n✅ Total contacts imported: ${imported}`);

  // Summary by job level
  console.log("\n📊 Import Summary by Job Level:");
  const levelCounts: Record<string, number> = {};
  contacts.forEach((c) => {
    levelCounts[c.jobLevel] = (levelCounts[c.jobLevel] || 0) + 1;
  });
  Object.entries(levelCounts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([level, count]) => {
      console.log(`   ${level}: ${count}`);
    });
}

async function main() {
  console.log("🚀 LinkedIn Leads Import to Convex\n");
  console.log(`📂 CSV File: ${CSV_PATH}`);
  console.log(`🔗 Convex URL: ${convexUrl}\n`);

  try {
    // Step 1: Find or create company
    const companyId = await findOrCreateCompany();

    // Step 2: Import contacts
    await importContacts(companyId);

    console.log("\n🎉 Import complete!");
  } catch (error) {
    console.error("\n❌ Import failed:", error);
    process.exit(1);
  }
}

main();
