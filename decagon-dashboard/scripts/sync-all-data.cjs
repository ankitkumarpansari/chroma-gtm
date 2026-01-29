#!/usr/bin/env node
/**
 * Sync All Decagon Data to Convex
 * 
 * Syncs:
 * 1. Target companies (66 prospect companies)
 * 2. Existing customers (30 companies from Customer Roster)
 * 3. CX Leaders with LinkedIn profiles
 * 
 * Usage:
 *   cd decagon-dashboard
 *   node scripts/sync-all-data.cjs
 */

const { ConvexHttpClient } = require("convex/browser");
const fs = require("fs");
const path = require("path");

// Load environment variables
require("dotenv").config({ path: ".env.local" });

// Domain mappings for target companies
const DOMAIN_MAP = {
  // ICP 1: Consumer Fintech
  'Brex': 'brex.com', 'Mercury': 'mercury.com', 'Ramp': 'ramp.com',
  'Plaid': 'plaid.com', 'Stripe': 'stripe.com', 'Block (Cash App)': 'block.xyz',
  'Synchrony Financial': 'synchrony.com', 'Robinhood': 'robinhood.com',
  'SoFi': 'sofi.com', 'Greenlight': 'greenlight.com', 'Current': 'current.com',
  'Dave': 'dave.com', 'MoneyLion': 'moneylion.com', 'Varo': 'varomoney.com',
  // ICP 2: Consumer SaaS
  'Intuit': 'intuit.com', 'Figma': 'figma.com', 'Canva': 'canva.com',
  'Calendly': 'calendly.com', 'Loom': 'loom.com', 'Linear': 'linear.app',
  'Productboard': 'productboard.com', 'Airtable': 'airtable.com', 'Miro': 'miro.com',
  'Webflow': 'webflow.com', 'Zapier': 'zapier.com', 'Grammarly': 'grammarly.com',
  // ICP 3: E-commerce/Marketplace
  'Etsy': 'etsy.com', 'StockX': 'stockx.com', 'Poshmark': 'poshmark.com',
  'Mercari': 'mercari.com', 'Faire': 'faire.com', 'Instacart': 'instacart.com',
  'DoorDash': 'doordash.com', 'Uber': 'uber.com', 'Lyft': 'lyft.com',
  'Turo': 'turo.com', 'Offerup': 'offerup.com', 'Reverb': 'reverb.com',
  'Depop': 'depop.com', 'ThredUp': 'thredup.com', 'Wayfair': 'wayfair.com',
  // ICP 4: Health & Wellness
  'Headspace': 'headspace.com', 'Calm': 'calm.com', 'Hims/Hers': 'forhims.com',
  'Ro (Roman/Rory)': 'ro.co', 'Thirty Madison': 'thirtymadison.com',
  'Peloton': 'onepeloton.com', 'Whoop': 'whoop.com', 'Talkspace': 'talkspace.com',
  'BetterHelp': 'betterhelp.com', 'Teladoc': 'teladoc.com', 'One Medical': 'onemedical.com',
  'Carbon Health': 'carbonhealth.com', 'WeightWatchers': 'weightwatchers.com',
  // ICP 5: Travel & Hospitality
  'Airbnb': 'airbnb.com', 'Booking.com': 'booking.com', 'Expedia': 'expedia.com',
  'United Airlines': 'united.com', 'Delta Airlines': 'delta.com',
  'Marriott': 'marriott.com', 'Hilton': 'hilton.com',
  'Enterprise Holdings': 'enterprise.com', 'GetYourGuide': 'getyourguide.com',
  'Tripadvisor': 'tripadvisor.com', 'KAYAK': 'kayak.com', 'Hopper': 'hopper.com',
  // Customer Roster
  'Rocket Mortgage': 'rocketmortgage.com', 'GAP Inc.': 'gapinc.com',
  'SiriusXM': 'siriusxm.com', 'Sutter Health': 'sutterhealth.org',
  'The North Face': 'thenorthface.com', 'Deliveroo': 'deliveroo.com',
  'Discord': 'discord.com', 'DIRECTV': 'directv.com', 'Minted': 'minted.com',
  'Rivian': 'rivian.com', 'Redfin': 'redfin.com', 'ADT': 'adt.com',
  'Sweetgreen': 'sweetgreen.com', 'R1 RCM': 'r1rcm.com', 'Tubi': 'tubi.tv',
  'Sonos': 'sonos.com', 'CDW': 'cdw.com', 'Clear': 'clearme.com',
  'Hy-Vee': 'hy-vee.com', 'Casper': 'casper.com', 'ASOS': 'asos.com',
  'Next': 'next.co.uk', 'Madison Reed': 'madison-reed.com',
  'Safelite': 'safelite.com', 'Guild': 'guild.com',
  // Special
  'H&R Block': 'hrblock.com', 'JPMorgan Chase': 'jpmorganchase.com',
};

// Parse CSV with proper quote handling
function parseCSV(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`  File not found: ${filePath}`);
    return [];
  }
  
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
        values.push(current.trim().replace(/^"|"$/g, ''));
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.trim().replace(/^"|"$/g, ''));
    
    const row = {};
    headers.forEach((header, idx) => {
      row[header] = values[idx] || '';
    });
    rows.push(row);
  }
  
  return rows;
}

// Determine job level from title
function getJobLevel(title) {
  const t = (title || '').toLowerCase();
  if (t.includes('chief') || t.includes('ceo') || t.includes('coo') || t.includes('cco') || t.includes('cxo')) return 'Executive';
  if (t.includes('evp') || t.includes('executive vice')) return 'Executive';
  if (t.includes('svp') || t.includes('senior vice president')) return 'SVP';
  if (t.includes('vp') || t.includes('vice president')) return 'VP';
  if (t.includes('head of') || t.includes('director')) return 'Director';
  if (t.includes('senior manager') || t.includes('sr manager')) return 'Senior Manager';
  if (t.includes('manager')) return 'Manager';
  return 'Individual Contributor';
}

// Determine role type
function getRoleType(title, level) {
  if (['Executive', 'SVP', 'VP'].includes(level)) return 'Decision Maker';
  if (['Director', 'Senior Manager'].includes(level)) return 'Influencer';
  return 'Champion';
}

// Determine job function from title
function getJobFunction(title) {
  const t = (title || '').toLowerCase();
  if (t.includes('customer experience') || t.includes('cx') || t.includes('client experience')) return 'Customer Experience';
  if (t.includes('customer success') || t.includes('client success')) return 'Customer Success';
  if (t.includes('customer support') || t.includes('support') || t.includes('customer care')) return 'Customer Support';
  if (t.includes('customer service') || t.includes('service')) return 'Customer Service';
  if (t.includes('contact center')) return 'Contact Center';
  if (t.includes('operations') || t.includes('ops')) return 'Operations';
  if (t.includes('product')) return 'Product';
  return 'Operations';
}

// Calculate persona score
function calculatePersonaScore(title, tier) {
  let score = 0;
  const level = getJobLevel(title);
  
  // Level scoring
  if (level === 'Executive') score += 10;
  else if (level === 'SVP') score += 9;
  else if (level === 'VP') score += 8;
  else if (level === 'Director') score += 6;
  else if (level === 'Senior Manager') score += 5;
  else if (level === 'Manager') score += 4;
  else score += 2;
  
  // Tier scoring
  if (tier === '1') score += 3;
  else if (tier === '2') score += 2;
  else if (tier === '3') score += 1;
  
  // CX keyword bonus
  const t = (title || '').toLowerCase();
  if (t.includes('customer') || t.includes('cx') || t.includes('support') || t.includes('care')) {
    score += 2;
  }
  
  return score;
}

async function main() {
  const convexUrl = process.env.VITE_CONVEX_URL || process.env.CONVEX_URL;
  if (!convexUrl) {
    console.error("❌ Missing CONVEX_URL. Set VITE_CONVEX_URL in .env.local");
    process.exit(1);
  }
  
  console.log("=" .repeat(70));
  console.log("🚀 SYNC ALL DECAGON DATA TO CONVEX");
  console.log("=".repeat(70));
  console.log(`\n🔗 Connecting to: ${convexUrl}`);
  
  const client = new ConvexHttpClient(convexUrl);
  
  // Data directories
  const dataDir = path.join(__dirname, '../../data/decagon_discovery');
  
  // Data files
  const targetCompaniesFile = path.join(dataDir, 'decagon_target_companies.csv');
  const customerRosterFile = path.join(dataDir, 'decagon_existing_customers.csv');
  const cxLeadersFile = path.join(dataDir, 'customer_roster_cx_leaders.csv');
  const hrblockUnitedJpmFile = path.join(dataDir, 'all_contacts_hrblock_united_jpm.csv');
  
  // Find latest full contacts file
  const files = fs.readdirSync(dataDir);
  const fullContactFiles = files.filter(f => f.startsWith('decagon_full_contacts_') && f.endsWith('.csv'));
  fullContactFiles.sort().reverse();
  const fullContactsFile = fullContactFiles[0] ? path.join(dataDir, fullContactFiles[0]) : null;
  
  console.log("\n📁 Data files:");
  console.log("  - Target Companies:", targetCompaniesFile);
  console.log("  - Customer Roster:", customerRosterFile);
  console.log("  - CX Leaders:", cxLeadersFile);
  console.log("  - H&R/United/JPM:", hrblockUnitedJpmFile);
  console.log("  - Full Contacts:", fullContactsFile || "Not found");
  
  // ========== SYNC TARGET COMPANIES ==========
  console.log("\n" + "=".repeat(70));
  console.log("📊 1. SYNCING TARGET COMPANIES");
  console.log("=".repeat(70));
  
  const targetData = parseCSV(targetCompaniesFile);
  console.log(`Found ${targetData.length} target companies`);
  
  // Get existing companies
  const existingCompanies = await client.query("companies:list", {});
  const existingNames = new Set(existingCompanies.map(c => c.name.toLowerCase()));
  console.log(`Existing in Convex: ${existingCompanies.length}`);
  
  // Parse target companies
  const newTargetCompanies = targetData
    .filter(row => {
      const name = row['company'] || row['Company'] || '';
      return name && !existingNames.has(name.toLowerCase());
    })
    .map(row => {
      const name = row['company'] || row['Company'] || '';
      return {
        name,
        domain: DOMAIN_MAP[name] || row['domain'] || '',
        icp: row['icp'] || row['ICP'] || 'Unknown',
        priority: row['priority'] || row['Priority'] || 'Medium',
        signalStrength: row['signal_strength'] || row['Signal Strength'] || 'Medium',
        whyFit: row['why_fit'] || row['Why Fit'] || '',
        decisionMakerTitles: row['decision_maker_titles'] || row['Decision Maker Titles'] || 'VP CX, Director Support',
        status: 'prospect',
      };
    });
  
  console.log(`New target companies to add: ${newTargetCompanies.length}`);
  
  // ========== SYNC CUSTOMER ROSTER ==========
  console.log("\n" + "=".repeat(70));
  console.log("📊 2. SYNCING CUSTOMER ROSTER");
  console.log("=".repeat(70));
  
  const customerData = parseCSV(customerRosterFile);
  console.log(`Found ${customerData.length} existing customers`);
  
  const newCustomerCompanies = customerData
    .filter(row => {
      const name = row['company'] || row['Company'] || '';
      return name && !existingNames.has(name.toLowerCase());
    })
    .map(row => {
      const name = row['company'] || row['Company'] || '';
      return {
        name,
        domain: DOMAIN_MAP[name] || row['website'] || '',
        icp: 'Existing Customer',
        priority: 'Customer',
        signalStrength: 'High',
        whyFit: `${row['industry'] || ''} - Existing Decagon customer`,
        decisionMakerTitles: 'VP CX, Director Support',
        status: 'Active Customer',
      };
    });
  
  console.log(`New customers to add: ${newCustomerCompanies.length}`);
  
  // Combine all companies
  const allNewCompanies = [...newTargetCompanies, ...newCustomerCompanies];
  
  if (allNewCompanies.length > 0) {
    const batchSize = 20;
    for (let i = 0; i < allNewCompanies.length; i += batchSize) {
      const batch = allNewCompanies.slice(i, i + batchSize);
      console.log(`  Adding batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(allNewCompanies.length/batchSize)}...`);
      await client.mutation("companies:bulkCreate", { companies: batch });
    }
    console.log(`✅ Added ${allNewCompanies.length} companies total`);
  }
  
  // Refresh company list and build ID map
  const allCompanies = await client.query("companies:list", {});
  const companyIdMap = {};
  for (const c of allCompanies) {
    companyIdMap[c.name.toLowerCase()] = c._id;
  }
  console.log(`Company ID map built: ${Object.keys(companyIdMap).length} companies`);
  
  // ========== SYNC CX LEADERS ==========
  console.log("\n" + "=".repeat(70));
  console.log("👥 3. SYNCING CX LEADERS (WITH LINKEDIN)");
  console.log("=".repeat(70));
  
  const existingContacts = await client.query("contacts:list", {});
  const existingContactKeys = new Set(
    existingContacts.map(c => `${c.name.toLowerCase()}|${c.companyName.toLowerCase()}`)
  );
  console.log(`Existing contacts in Convex: ${existingContacts.length}`);
  
  // CX Leaders from customer roster research
  const cxLeadersData = parseCSV(cxLeadersFile);
  console.log(`Found ${cxLeadersData.length} CX leaders from research`);
  
  const newCxLeaders = [];
  let skippedCx = 0;
  
  for (const row of cxLeadersData) {
    const companyName = row['company'] || row['Company'] || '';
    const name = row['name'] || row['Name'] || '';
    
    if (!companyName || !name) { skippedCx++; continue; }
    
    const key = `${name.toLowerCase()}|${companyName.toLowerCase()}`;
    if (existingContactKeys.has(key)) { skippedCx++; continue; }
    
    const companyId = companyIdMap[companyName.toLowerCase()];
    if (!companyId) {
      console.log(`  ⚠️ Company not found: ${companyName}`);
      skippedCx++; 
      continue; 
    }
    
    const title = row['title'] || row['Title'] || '';
    const tier = row['tier'] || row['Tier'] || '2';
    const jobLevel = getJobLevel(title);
    
    newCxLeaders.push({
      companyId,
      companyName,
      name,
      title,
      jobFunction: getJobFunction(title),
      jobLevel,
      roleType: getRoleType(title, jobLevel),
      linkedinUrl: row['linkedin_url'] || row['LinkedIn'] || undefined,
      email: row['email'] || row['Email'] || undefined,
      location: row['location'] || row['Location'] || undefined,
      personaScore: calculatePersonaScore(title, tier),
      source: 'Web Research',
    });
    
    existingContactKeys.add(key); // Prevent duplicates within batch
  }
  
  console.log(`New CX leaders to add: ${newCxLeaders.length} (${skippedCx} skipped)`);
  
  // ========== SYNC H&R BLOCK / UNITED / JPM CONTACTS ==========
  console.log("\n" + "=".repeat(70));
  console.log("👥 4. SYNCING H&R BLOCK / UNITED / JPM CONTACTS");
  console.log("=".repeat(70));
  
  const hrblockData = parseCSV(hrblockUnitedJpmFile);
  console.log(`Found ${hrblockData.length} contacts from H&R/United/JPM research`);
  
  const newHrblockContacts = [];
  let skippedHrblock = 0;
  
  for (const row of hrblockData) {
    const companyName = row['company'] || row['Company'] || '';
    const name = row['name'] || row['Name'] || '';
    
    if (!companyName || !name) { skippedHrblock++; continue; }
    
    const key = `${name.toLowerCase()}|${companyName.toLowerCase()}`;
    if (existingContactKeys.has(key)) { skippedHrblock++; continue; }
    
    const companyId = companyIdMap[companyName.toLowerCase()];
    if (!companyId) {
      console.log(`  ⚠️ Company not found: ${companyName}`);
      skippedHrblock++; 
      continue; 
    }
    
    const title = row['title'] || row['Title'] || '';
    const tier = row['tier'] || row['Tier'] || '2';
    const jobLevel = getJobLevel(title);
    
    newHrblockContacts.push({
      companyId,
      companyName,
      name,
      title,
      jobFunction: row['job_function'] || getJobFunction(title),
      jobLevel,
      roleType: getRoleType(title, jobLevel),
      linkedinUrl: row['linkedin_url'] || row['LinkedIn'] || undefined,
      email: row['email'] || row['Email'] || undefined,
      location: row['location'] || row['Location'] || undefined,
      personaScore: calculatePersonaScore(title, tier),
      source: 'Web Research',
    });
    
    existingContactKeys.add(key);
  }
  
  console.log(`New H&R/United/JPM contacts to add: ${newHrblockContacts.length} (${skippedHrblock} skipped)`);
  
  // ========== SYNC FULL CONTACTS (from Sumble) ==========
  console.log("\n" + "=".repeat(70));
  console.log("👥 5. SYNCING SUMBLE CONTACTS");
  console.log("=".repeat(70));
  
  const newSumbleContacts = [];
  let skippedSumble = 0;
  
  if (fullContactsFile) {
    const sumbleData = parseCSV(fullContactsFile);
    console.log(`Found ${sumbleData.length} contacts from Sumble`);
    
    for (const row of sumbleData) {
      const companyName = row['company'] || row['Company'] || '';
      const name = row['name'] || row['Name'] || '';
      
      if (!companyName || !name) { skippedSumble++; continue; }
      
      const key = `${name.toLowerCase()}|${companyName.toLowerCase()}`;
      if (existingContactKeys.has(key)) { skippedSumble++; continue; }
      
      const companyId = companyIdMap[companyName.toLowerCase()];
      if (!companyId) { skippedSumble++; continue; }
      
      const title = row['title'] || row['Title'] || '';
      const jobLevel = getJobLevel(title);
      
      newSumbleContacts.push({
        companyId,
        companyName,
        name,
        title,
        jobFunction: row['job_function'] || getJobFunction(title),
        jobLevel,
        roleType: getRoleType(title, jobLevel),
        linkedinUrl: row['linkedin_url'] || row['LinkedIn'] || undefined,
        email: row['email'] || row['Email'] || undefined,
        location: row['location'] || row['Location'] || undefined,
        personaScore: parseInt(row['persona_score'] || '0') || calculatePersonaScore(title, '2'),
        source: 'Sumble',
      });
      
      existingContactKeys.add(key);
    }
    
    console.log(`New Sumble contacts to add: ${newSumbleContacts.length} (${skippedSumble} skipped)`);
  } else {
    console.log("  No Sumble contacts file found");
  }
  
  // ========== BULK INSERT ALL CONTACTS ==========
  const allNewContacts = [...newCxLeaders, ...newHrblockContacts, ...newSumbleContacts];
  
  console.log("\n" + "=".repeat(70));
  console.log("💾 INSERTING ALL CONTACTS");
  console.log("=".repeat(70));
  console.log(`Total new contacts to add: ${allNewContacts.length}`);
  
  if (allNewContacts.length > 0) {
    const batchSize = 50;
    for (let i = 0; i < allNewContacts.length; i += batchSize) {
      const batch = allNewContacts.slice(i, i + batchSize);
      console.log(`  Batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(allNewContacts.length/batchSize)}...`);
      await client.mutation("contacts:bulkCreate", { contacts: batch });
    }
    console.log(`✅ Added ${allNewContacts.length} contacts`);
  }
  
  // ========== FINAL SUMMARY ==========
  console.log("\n" + "=".repeat(70));
  console.log("📊 SYNC COMPLETE - FINAL COUNTS");
  console.log("=".repeat(70));
  
  const finalCompanies = await client.query("companies:list", {});
  const finalContacts = await client.query("contacts:list", {});
  const stats = await client.query("companies:getStats", {});
  
  console.log(`\n✅ Companies: ${finalCompanies.length}`);
  console.log(`✅ Contacts: ${finalContacts.length}`);
  
  console.log("\n📈 By Status:");
  for (const [status, count] of Object.entries(stats.byStatus || {})) {
    console.log(`   ${status}: ${count}`);
  }
  
  console.log("\n📈 By ICP:");
  for (const [icp, count] of Object.entries(stats.byIcp || {})) {
    console.log(`   ${icp}: ${count}`);
  }
  
  console.log("\n🎯 Top 10 Contacts by Persona Score:");
  const topContacts = finalContacts
    .sort((a, b) => b.personaScore - a.personaScore)
    .slice(0, 10);
  
  for (const c of topContacts) {
    const ln = c.linkedinUrl ? ' ✓LI' : '';
    console.log(`   ${c.name} | ${c.title} | ${c.companyName} (${c.personaScore})${ln}`);
  }
  
  console.log("\n🎉 Done!");
}

main().catch(console.error);
