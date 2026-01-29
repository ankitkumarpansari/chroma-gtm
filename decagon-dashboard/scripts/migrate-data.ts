/**
 * Migration script to import Decagon data from CSV/JSON into Convex
 *
 * Usage:
 * 1. First run `npx convex dev` to start Convex and get your deployment URL
 * 2. Set CONVEX_URL environment variable
 * 3. Run `npm run migrate`
 */

import { ConvexHttpClient } from "convex/browser";
import { api } from "../convex/_generated/api";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

// ES Module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const DATA_DIR = path.join(__dirname, "../../data/decagon_discovery");
const COMPANIES_CSV = path.join(DATA_DIR, "decagon_target_companies.csv");
const CONTACTS_JSON = path.join(
  DATA_DIR,
  "decagon_full_contacts_20260128_133847.json"
);

// Initialize Convex client
const convexUrl = process.env.CONVEX_URL;
if (!convexUrl) {
  console.error("Error: CONVEX_URL environment variable not set");
  console.error("Run `npx convex dev` and copy the deployment URL");
  process.exit(1);
}

const client = new ConvexHttpClient(convexUrl);

// Parse CSV
function parseCSV(content: string): Record<string, string>[] {
  const lines = content.trim().split("\n");
  const headers = lines[0].split(",").map((h) => h.trim());

  return lines.slice(1).map((line) => {
    // Handle quoted fields with commas
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

    const row: Record<string, string> = {};
    headers.forEach((header, i) => {
      row[header] = values[i] || "";
    });
    return row;
  });
}

async function migrateCompanies(): Promise<Map<string, string>> {
  console.log("📦 Migrating companies...");

  const csvContent = fs.readFileSync(COMPANIES_CSV, "utf-8");
  const rows = parseCSV(csvContent);

  const companyMap = new Map<string, string>(); // name -> convex id

  // Batch companies (max 100 at a time for Convex)
  const batchSize = 50;
  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);

    const companies = batch
      .filter((row) => row.Company && row.Company.trim())
      .map((row) => ({
        name: row.Company,
        domain: undefined,
        icp: row.ICP || "Unknown",
        priority: row.Priority || "Medium",
        signalStrength: row["Signal Strength"] || "Medium",
        whyFit: row["Why Fit"] || "",
        decisionMakerTitles: row["Decision Maker Titles"] || "",
        status: row.Status || "New",
        owner: row.Owner || undefined,
        notes: row.Notes || undefined,
      }));

    if (companies.length > 0) {
      const result = await client.mutation(api.companies.bulkCreate, {
        companies,
      });
      result.forEach(({ name, id }) => {
        companyMap.set(name, id);
      });
      console.log(`  ✓ Imported ${companies.length} companies (batch ${Math.floor(i / batchSize) + 1})`);
    }
  }

  console.log(`✅ Total companies imported: ${companyMap.size}`);
  return companyMap;
}

async function migrateContacts(companyMap: Map<string, string>): Promise<void> {
  console.log("\n📇 Migrating contacts...");

  if (!fs.existsSync(CONTACTS_JSON)) {
    console.log("  ⚠️ Contacts JSON file not found, skipping");
    return;
  }

  const jsonContent = fs.readFileSync(CONTACTS_JSON, "utf-8");
  const data = JSON.parse(jsonContent);
  const contacts = data.contacts || [];

  let imported = 0;
  let skipped = 0;

  // Process in batches
  const batchSize = 50;
  for (let i = 0; i < contacts.length; i += batchSize) {
    const batch = contacts.slice(i, i + batchSize);

    const contactsToImport = [];

    for (const contact of batch) {
      const companyId = companyMap.get(contact.company);

      if (!companyId) {
        // Company not in our target list, skip
        skipped++;
        continue;
      }

      contactsToImport.push({
        companyId: companyId as any, // Convex ID type
        companyName: contact.company,
        name: contact.name || "Unknown",
        title: contact.title || "",
        jobFunction: contact.job_function || "Unknown",
        jobLevel: contact.job_level || "Unknown",
        roleType: contact.role_type || "Unknown",
        linkedinUrl: contact.linkedin_url || undefined,
        email: contact.email || undefined,
        location: contact.location || undefined,
        personaScore: contact.persona_score || 0,
        source: contact.source || "Unknown",
      });
    }

    if (contactsToImport.length > 0) {
      await client.mutation(api.contacts.bulkCreate, {
        contacts: contactsToImport,
      });
      imported += contactsToImport.length;
      console.log(`  ✓ Imported ${contactsToImport.length} contacts (batch ${Math.floor(i / batchSize) + 1})`);
    }
  }

  console.log(`✅ Total contacts imported: ${imported}`);
  console.log(`⏭️ Contacts skipped (company not in target list): ${skipped}`);
}

async function main() {
  console.log("🚀 Starting Decagon data migration to Convex\n");
  console.log(`📂 Data directory: ${DATA_DIR}`);
  console.log(`🔗 Convex URL: ${convexUrl}\n`);

  try {
    // Step 1: Migrate companies
    const companyMap = await migrateCompanies();

    // Step 2: Migrate contacts
    await migrateContacts(companyMap);

    console.log("\n🎉 Migration complete!");
  } catch (error) {
    console.error("\n❌ Migration failed:", error);
    process.exit(1);
  }
}

main();
