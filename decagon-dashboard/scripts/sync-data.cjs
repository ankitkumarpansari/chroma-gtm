#!/usr/bin/env node
/**
 * Sync Decagon Data to Convex
 * 
 * Usage:
 *   cd decagon-dashboard
 *   node scripts/sync-data.js
 */

const { ConvexHttpClient } = require("convex/browser");
const fs = require("fs");
const path = require("path");

// Load environment variables
require("dotenv").config({ path: ".env.local" });

// Domain mappings
const DOMAIN_MAP = {
  'Brex': 'brex.com', 'Mercury': 'mercury.com', 'Ramp': 'ramp.com',
  'Plaid': 'plaid.com', 'Stripe': 'stripe.com', 'Block (Cash App)': 'block.xyz',
  'Synchrony Financial': 'synchrony.com', 'Robinhood': 'robinhood.com',
  'SoFi': 'sofi.com', 'Greenlight': 'greenlight.com', 'Current': 'current.com',
  'Dave': 'dave.com', 'MoneyLion': 'moneylion.com', 'Varo': 'varomoney.com',
  'Intuit': 'intuit.com', 'Figma': 'figma.com', 'Canva': 'canva.com',
  'Calendly': 'calendly.com', 'Loom': 'loom.com', 'Linear': 'linear.app',
  'Productboard': 'productboard.com', 'Airtable': 'airtable.com', 'Miro': 'miro.com',
  'Webflow': 'webflow.com', 'Zapier': 'zapier.com', 'Grammarly': 'grammarly.com',
  'Etsy': 'etsy.com', 'StockX': 'stockx.com', 'Poshmark': 'poshmark.com',
  'Mercari': 'mercari.com', 'Faire': 'faire.com', 'Instacart': 'instacart.com',
  'DoorDash': 'doordash.com', 'Uber': 'uber.com', 'Lyft': 'lyft.com',
  'Turo': 'turo.com', 'Offerup': 'offerup.com', 'Reverb': 'reverb.com',
  'Depop': 'depop.com', 'ThredUp': 'thredup.com', 'Headspace': 'headspace.com',
  'Calm': 'calm.com', 'Hims/Hers': 'forhims.com', 'Ro (Roman/Rory)': 'ro.co',
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

// Parse CSV
function parseCSV(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(line => line.trim());
  if (lines.length === 0) return [];
  
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  const rows = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = [];
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
    
    const row = {};
    headers.forEach((header, idx) => {
      row[header] = values[idx] || '';
    });
    rows.push(row);
  }
  
  return rows;
}

async function main() {
  const convexUrl = process.env.VITE_CONVEX_URL || process.env.CONVEX_URL;
  if (!convexUrl) {
    console.error("❌ Missing CONVEX_URL. Set VITE_CONVEX_URL in .env.local");
    process.exit(1);
  }
  
  console.log("🔗 Connecting to Convex:", convexUrl);
  const client = new ConvexHttpClient(convexUrl);
  
  // Data files
  const dataDir = path.join(__dirname, '../../data/decagon_discovery');
  const targetCompaniesFile = path.join(dataDir, 'decagon_target_companies.csv');
  
  // Find latest contacts file
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
  
  const companiesData = parseCSV(targetCompaniesFile);
  console.log(`Found ${companiesData.length} companies`);
  
  // Get existing
  const existingCompanies = await client.query("companies:list", {});
  const existingNames = new Set(existingCompanies.map(c => c.name.toLowerCase()));
  console.log(`Existing in Convex: ${existingCompanies.length}`);
  
  // New companies
  const newCompanies = companiesData
    .filter(row => row['Company'] && !existingNames.has(row['Company'].toLowerCase()))
    .map(row => ({
      name: row['Company'] || '',
      domain: DOMAIN_MAP[row['Company']] || '',
      icp: row['ICP'] || row['ICP Category'] || 'Unknown',
      priority: row['Priority'] || 'Medium',
      signalStrength: row['Signal Strength'] || 'Medium',
      whyFit: row['Why Fit'] || row['Why They Fit'] || '',
      decisionMakerTitles: row['Decision Maker Titles'] || 'VP CX, Director Support',
      status: row['Status'] || 'New',
      owner: row['Owner'] || undefined,
      notes: row['Notes'] || undefined,
    }));
  
  console.log(`New to add: ${newCompanies.length}`);
  
  if (newCompanies.length > 0) {
    const batchSize = 20;
    for (let i = 0; i < newCompanies.length; i += batchSize) {
      const batch = newCompanies.slice(i, i + batchSize);
      console.log(`  Batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(newCompanies.length/batchSize)}...`);
      await client.mutation("companies:bulkCreate", { companies: batch });
    }
    console.log(`✅ Added ${newCompanies.length} companies`);
  }
  
  // Build company ID map
  const allCompanies = await client.query("companies:list", {});
  const companyIdMap = {};
  for (const c of allCompanies) {
    companyIdMap[c.name.toLowerCase()] = c._id;
  }
  
  // ========== SYNC CONTACTS ==========
  console.log("\n" + "=".repeat(60));
  console.log("👥 SYNCING CONTACTS TO CONVEX");
  console.log("=".repeat(60));
  
  if (!contactsFile) {
    console.log("⚠️ No contacts file found");
    return;
  }
  
  const contactsData = parseCSV(contactsFile);
  console.log(`Found ${contactsData.length} contacts`);
  
  const existingContacts = await client.query("contacts:list", {});
  const existingKeys = new Set(
    existingContacts.map(c => `${c.name.toLowerCase()}|${c.companyName.toLowerCase()}`)
  );
  console.log(`Existing in Convex: ${existingContacts.length}`);
  
  const newContacts = [];
  let skipped = 0;
  
  for (const row of contactsData) {
    const companyName = row['company'] || row['Company'] || '';
    const name = row['name'] || row['Name'] || '';
    
    if (!companyName || !name) { skipped++; continue; }
    
    const key = `${name.toLowerCase()}|${companyName.toLowerCase()}`;
    if (existingKeys.has(key)) { skipped++; continue; }
    
    const companyId = companyIdMap[companyName.toLowerCase()];
    if (!companyId) { skipped++; continue; }
    
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
  
  console.log(`New to add: ${newContacts.length} (${skipped} skipped)`);
  
  if (newContacts.length > 0) {
    const batchSize = 50;
    for (let i = 0; i < newContacts.length; i += batchSize) {
      const batch = newContacts.slice(i, i + batchSize);
      console.log(`  Batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(newContacts.length/batchSize)}...`);
      await client.mutation("contacts:bulkCreate", { contacts: batch });
    }
    console.log(`✅ Added ${newContacts.length} contacts`);
  }
  
  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("📊 SYNC COMPLETE");
  console.log("=".repeat(60));
  
  const finalCompanies = await client.query("companies:list", {});
  const finalContacts = await client.query("contacts:list", {});
  
  console.log(`\nFinal counts:`);
  console.log(`  Companies: ${finalCompanies.length}`);
  console.log(`  Contacts: ${finalContacts.length}`);
}

main().catch(console.error);
