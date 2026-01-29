/**
 * Sync Decagon Data to Convex
 * 
 * This script reads the CSV data from the spreadsheet exports and syncs it to Convex.
 * 
 * Usage:
 *   cd decagon-dashboard
 *   npx convex run scripts/sync-to-convex
 * 
 * Or run directly with ts-node:
 *   npx ts-node --esm scripts/sync-to-convex.ts
 */

import { ConvexHttpClient } from "convex/browser";
import { api } from "../convex/_generated/api";
import * as fs from "fs";
import * as path from "path";

// Domain mappings for companies
const DOMAIN_MAP: Record<string, string> = {
  'Brex': 'brex.com', 'Mercury': 'mercury.com', 'Ramp': 'ramp.com',
  'Plaid': 'plaid.com', 'Stripe': 'stripe.com', 'Block (Cash App)': 'block.xyz',
  'Synchrony Financial': 'synchrony.com', 'Robinhood': 'robinhood.com',
  'SoFi': 'sofi.com', 'Greenlight': 'greenlight.com', 'Current': 'current.com',
  'Dave': 'dave.com', 'MoneyLion': 'moneylion.com', 'Varo': 'varomoney.com',
  'Intuit': 'intuit.com', 'Radicle Health': 'radiclehealth.com',
  'Figma': 'figma.com', 'Canva': 'canva.com', 'Calendly': 'calendly.com',
  'Loom': 'loom.com', 'Linear': 'linear.app', 'Productboard': 'productboard.com',
  'Airtable': 'airtable.com', 'Miro': 'miro.com', 'Webflow': 'webflow.com',
  'Zapier': 'zapier.com', 'Grammarly': 'grammarly.com', 'Etsy': 'etsy.com',
  'StockX': 'stockx.com', 'Poshmark': 'poshmark.com', 'Mercari': 'mercari.com',
  'Faire': 'faire.com', 'Instacart': 'instacart.com', 'DoorDash': 'doordash.com',
  'Uber': 'uber.com', 'Lyft': 'lyft.com', 'Turo': 'turo.com',
  'Offerup': 'offerup.com', 'Reverb': 'reverb.com', 'Depop': 'depop.com',
  'ThredUp': 'thredup.com', 'Headspace': 'headspace.com', 'Calm': 'calm.com',
  'Hims/Hers': 'forhims.com', 'Ro (Roman/Rory)': 'ro.co',
  'Thirty Madison': 'thirtymadison.com', 'Peloton': 'onepeloton.com',
  'Whoop': 'whoop.com', 'Talkspace': 'talkspace.com', 'BetterHelp': 'betterhelp.com',
  'Teladoc': 'teladoc.com', 'One Medical': 'onemedical.com',
  'Carbon Health': 'carbonhealth.com', 'Airbnb': 'airbnb.com',
  'Booking.com': 'booking.com', 'Expedia': 'expedia.com',
  'United Airlines': 'united.com', 'Delta Airlines': 'delta.com',
  'Marriott': 'marriott.com', 'Hilton': 'hilton.com',
  'Enterprise Holdings': 'enterprise.com', 'GetYourGuide': 'getyourguide.com',
  'Tripadvisor': 'tripadvisor.com', 'KAYAK': 'kayak.com', 'Hopper': 'hopper.com',
};

// Parse CSV file
function parseCSV(filePath: string): Record<string, string>[] {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(line => line.trim());
  if (lines.length === 0) return [];
  
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  const rows: Record<string, string>[] = [];
  
  for (let i = 1; i < lines.length; i++) {
    // Handle CSV with quoted fields
    const values: string[] = [];
    let current = '';
    let inQuotes = false;
    
    for (const char of lines[i]) {
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.trim());
    
    const row: Record<string, string> = {};
    headers.forEach((header, idx) => {
      row[header] = values[idx] || '';
    });
    rows.push(row);
  }
  
  return rows;
}

async function main() {
  // Get Convex URL from environment
  const convexUrl = process.env.VITE_CONVEX_URL || process.env.CONVEX_URL;
  if (!convexUrl) {
    console.error("❌ Missing CONVEX_URL environment variable");
    console.log("Set it in .env.local: VITE_CONVEX_URL=https://your-deployment.convex.cloud");
    process.exit(1);
  }
  
  console.log("🔗 Connecting to Convex:", convexUrl);
  const client = new ConvexHttpClient(convexUrl);
  
  // Find data files
  const dataDir = path.join(__dirname, '../../data/decagon_discovery');
  const targetCompaniesFile = path.join(dataDir, 'decagon_target_companies.csv');
  
  // Find the most recent contacts file
  const files = fs.readdirSync(dataDir);
  const contactFiles = files.filter(f => f.startsWith('decagon_full_contacts_') && f.endsWith('.csv'));
  contactFiles.sort().reverse();
  const contactsFile = contactFiles[0] ? path.join(dataDir, contactFiles[0]) : null;
  
  console.log("\n📁 Data files:");
  console.log("  - Companies:", targetCompaniesFile);
  console.log("  - Contacts:", contactsFile || "Not found");
  
  // ========== SYNC COMPANIES ==========
  console.log("\n" + "=".repeat(60));
  console.log("📊 SYNCING COMPANIES TO CONVEX");
  console.log("=".repeat(60));
  
  if (!fs.existsSync(targetCompaniesFile)) {
    console.error("❌ Target companies file not found");
    process.exit(1);
  }
  
  const companiesData = parseCSV(targetCompaniesFile);
  console.log(`Found ${companiesData.length} companies to sync`);
  
  // Check existing companies to avoid duplicates
  const existingCompanies = await client.query(api.companies.list, {});
  const existingNames = new Set(existingCompanies.map(c => c.name.toLowerCase()));
  console.log(`Found ${existingCompanies.length} existing companies in Convex`);
  
  // Prepare new companies
  const newCompanies = companiesData
    .filter(row => row['Company'] && !existingNames.has(row['Company'].toLowerCase()))
    .map(row => ({
      name: row['Company'] || '',
      domain: DOMAIN_MAP[row['Company']] || '',
      icp: row['ICP'] || row['ICP Category'] || 'Unknown',
      priority: row['Priority'] || 'Medium',
      signalStrength: row['Signal Strength'] || 'Medium',
      whyFit: row['Why Fit'] || row['Why They Fit'] || '',
      decisionMakerTitles: row['Decision Maker Titles'] || row['Target Titles'] || 'VP CX, Director Support',
      status: row['Status'] || 'New',
      owner: row['Owner'] || undefined,
      notes: row['Notes'] || undefined,
    }));
  
  console.log(`\n${newCompanies.length} new companies to add`);
  
  if (newCompanies.length > 0) {
    // Batch in groups of 20
    const batchSize = 20;
    const companyIdMap: Record<string, string> = {};
    
    for (let i = 0; i < newCompanies.length; i += batchSize) {
      const batch = newCompanies.slice(i, i + batchSize);
      console.log(`  Inserting batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(newCompanies.length/batchSize)}...`);
      
      const results = await client.mutation(api.companies.bulkCreate, { companies: batch });
      for (const result of results) {
        companyIdMap[result.name.toLowerCase()] = result.id;
      }
    }
    
    console.log(`✅ Added ${newCompanies.length} companies`);
  }
  
  // Build company ID map from all companies
  const allCompanies = await client.query(api.companies.list, {});
  const companyIdMap: Record<string, string> = {};
  for (const c of allCompanies) {
    companyIdMap[c.name.toLowerCase()] = c._id;
  }
  
  // ========== SYNC CONTACTS ==========
  console.log("\n" + "=".repeat(60));
  console.log("👥 SYNCING CONTACTS TO CONVEX");
  console.log("=".repeat(60));
  
  if (!contactsFile) {
    console.log("⚠️ No contacts file found, skipping contacts sync");
    return;
  }
  
  const contactsData = parseCSV(contactsFile);
  console.log(`Found ${contactsData.length} contacts to sync`);
  
  // Check existing contacts
  const existingContacts = await client.query(api.contacts.list, {});
  const existingContactKeys = new Set(
    existingContacts.map(c => `${c.name.toLowerCase()}|${c.companyName.toLowerCase()}`)
  );
  console.log(`Found ${existingContacts.length} existing contacts in Convex`);
  
  // Prepare new contacts
  const newContacts: any[] = [];
  let skipped = 0;
  
  for (const row of contactsData) {
    const companyName = row['company'] || row['Company'] || '';
    const name = row['name'] || row['Name'] || '';
    
    if (!companyName || !name) {
      skipped++;
      continue;
    }
    
    const key = `${name.toLowerCase()}|${companyName.toLowerCase()}`;
    if (existingContactKeys.has(key)) {
      skipped++;
      continue;
    }
    
    const companyId = companyIdMap[companyName.toLowerCase()];
    if (!companyId) {
      // Company not in our target list, skip
      skipped++;
      continue;
    }
    
    newContacts.push({
      companyId,
      companyName,
      name,
      title: row['title'] || row['Title'] || '',
      jobFunction: row['job_function'] || row['Job Function'] || 'Unknown',
      jobLevel: row['job_level'] || row['Job Level'] || 'Unknown',
      roleType: row['role_type'] || row['Role Type'] || 'End User',
      linkedinUrl: row['linkedin_url'] || row['LinkedIn'] || undefined,
      email: row['email'] || row['Email'] || undefined,
      location: row['location'] || row['Location'] || undefined,
      personaScore: parseInt(row['persona_score'] || row['Score'] || '0') || 0,
      source: row['source'] || row['Source'] || 'Sumble',
    });
  }
  
  console.log(`\n${newContacts.length} new contacts to add (${skipped} skipped)`);
  
  if (newContacts.length > 0) {
    // Batch in groups of 50
    const batchSize = 50;
    
    for (let i = 0; i < newContacts.length; i += batchSize) {
      const batch = newContacts.slice(i, i + batchSize);
      console.log(`  Inserting batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(newContacts.length/batchSize)}...`);
      
      await client.mutation(api.contacts.bulkCreate, { contacts: batch });
    }
    
    console.log(`✅ Added ${newContacts.length} contacts`);
  }
  
  // ========== SUMMARY ==========
  console.log("\n" + "=".repeat(60));
  console.log("📊 SYNC COMPLETE");
  console.log("=".repeat(60));
  
  const finalCompanies = await client.query(api.companies.list, {});
  const finalContacts = await client.query(api.contacts.list, {});
  
  console.log(`\nFinal counts in Convex:`);
  console.log(`  Companies: ${finalCompanies.length}`);
  console.log(`  Contacts: ${finalContacts.length}`);
  
  // Stats
  const stats = await client.query(api.companies.getStats, {});
  console.log(`\nBy ICP:`, stats.byIcp);
  console.log(`By Priority:`, stats.byPriority);
  console.log(`By Status:`, stats.byStatus);
}

main().catch(console.error);
