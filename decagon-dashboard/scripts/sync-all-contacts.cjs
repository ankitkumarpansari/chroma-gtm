#!/usr/bin/env node
/**
 * Sync ALL contact data files to Convex
 */

const { ConvexHttpClient } = require("convex/browser");
const fs = require("fs");
const path = require("path");

require("dotenv").config({ path: ".env.local" });

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
  const convexUrl = process.env.VITE_CONVEX_URL;
  if (!convexUrl) {
    console.error("❌ Missing VITE_CONVEX_URL");
    process.exit(1);
  }
  
  console.log("🔗 Convex:", convexUrl);
  const client = new ConvexHttpClient(convexUrl);
  
  // Build company ID map
  const allCompanies = await client.query("companies:list", {});
  const companyIdMap = {};
  for (const c of allCompanies) {
    companyIdMap[c.name.toLowerCase()] = c._id;
  }
  console.log(`Found ${allCompanies.length} companies`);
  
  // Get existing contacts
  const existingContacts = await client.query("contacts:list", {});
  const existingKeys = new Set(
    existingContacts.map(c => `${c.name.toLowerCase()}|${c.companyName.toLowerCase()}`)
  );
  console.log(`Existing contacts: ${existingContacts.length}`);
  
  // Find all contact CSV files
  const dataDir = path.join(__dirname, '../../data/decagon_discovery');
  const files = fs.readdirSync(dataDir);
  const contactFiles = files.filter(f => 
    (f.includes('contacts') || f.includes('personas')) && f.endsWith('.csv')
  );
  
  console.log(`\nFound ${contactFiles.length} contact files to process`);
  
  const allNewContacts = [];
  
  for (const file of contactFiles) {
    const filePath = path.join(dataDir, file);
    const data = parseCSV(filePath);
    
    for (const row of data) {
      const companyName = row['company'] || row['Company'] || '';
      const name = row['name'] || row['Name'] || '';
      
      if (!companyName || !name) continue;
      
      const key = `${name.toLowerCase()}|${companyName.toLowerCase()}`;
      if (existingKeys.has(key)) continue;
      
      const companyId = companyIdMap[companyName.toLowerCase()];
      if (!companyId) continue;
      
      existingKeys.add(key); // Prevent duplicates within this run
      
      allNewContacts.push({
        companyId,
        companyName,
        name,
        title: row['title'] || row['Title'] || row['job_title'] || '',
        jobFunction: row['job_function'] || row['Job Function'] || 'Unknown',
        jobLevel: row['job_level'] || row['Job Level'] || 'Unknown',
        roleType: row['role_type'] || row['Role Type'] || 'End User',
        linkedinUrl: row['linkedin_url'] || row['LinkedIn'] || row['LinkedIn URL'] || undefined,
        email: row['email'] || row['Email'] || undefined,
        location: row['location'] || row['Location'] || undefined,
        personaScore: parseInt(row['persona_score'] || row['Score'] || row['Persona Score'] || '0') || 0,
        source: row['source'] || row['Source'] || 'Sumble',
      });
    }
    
    console.log(`  ${file}: processed`);
  }
  
  console.log(`\n${allNewContacts.length} new contacts to add`);
  
  if (allNewContacts.length > 0) {
    const batchSize = 50;
    for (let i = 0; i < allNewContacts.length; i += batchSize) {
      const batch = allNewContacts.slice(i, i + batchSize);
      console.log(`  Batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(allNewContacts.length/batchSize)}...`);
      await client.mutation("contacts:bulkCreate", { contacts: batch });
    }
    console.log(`✅ Added ${allNewContacts.length} contacts`);
  }
  
  // Final counts
  const finalContacts = await client.query("contacts:list", {});
  console.log(`\n📊 Total contacts in Convex: ${finalContacts.length}`);
}

main().catch(console.error);
