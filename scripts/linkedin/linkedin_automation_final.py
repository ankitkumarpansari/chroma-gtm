#!/usr/bin/env python3
"""
LinkedIn Sales Navigator Automation - Final Working Version
Adds ONLY THE FIRST RESULT to 'Outreach (ankit managed)' list

Flow:
1. Search for company
2. Click "Save" button on the FIRST result row (not toolbar)
3. Select "Outreach (ankit managed)" from dropdown
4. Skip if already saved
"""

import asyncio
import json
from pathlib import Path

# Configuration
USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"
TARGET_LIST = "Outreach (ankit managed)"
PROGRESS_FILE = Path.home() / ".linkedin_sales_nav_automation" / "progress.json"
DELAY_BETWEEN_COMPANIES = 5  # seconds

# Companies to add - Updated list from user
COMPANIES = [
    # Original companies
    "Mintlify", "Clay", "Vapi", "Bland AI", "Retell AI", "Synthflow",
    "Voiceflow", "PolyAI", "Rasa", "Cognigy", "Kore.ai", "OneReach",
    "Moveworks", "Forethought", "Ada", "Intercom", "Drift", "Qualified",
    "Gong", "Chorus", "Clari", "People.ai", "6sense", "Demandbase",
    "ZoomInfo", "Apollo.io", "Salesloft", "Groove", "Mixmax",
    
    # New companies from user's list
    "Mintlify", "n8n", "Lindy.ai", "Relay.app", "Jasper", "Guru",
    "GitBook", "ReadMe", "Forethought", "Qualified", "Pieces for Developers",
    "Intercom", "Ada", "Zendesk", "Surfer", "Frase", "MarketMuse",
    "Eightfold.ai", "Moonhub", "Mercor", "Findem", "Koyfin", "Fintool",
    "Rogo", "FinChat", "Numeric", "Truewind", "Mindtrip", "Spotnana",
    "Writer", "Notion", "Coda", "Gumloop", "Relevance AI", "Stack AI",
    "Retool", "PostHog", "Amplitude", "Mixpanel", "Segment", "Hightouch",
    "Census", "Freshworks", "HubSpot", "Gong", "Clari", "Apollo.io",
    "ZoomInfo", "Greptile",
    
    # More from original list
    "Glean", "Hebbia", "Vectara", "Pinecone", "Weaviate", "Qdrant",
    "Milvus", "Chroma", "LanceDB", "Marqo", "Metal", "Zilliz",
    "Cohere", "AI21 Labs", "Anthropic", "OpenAI", "Hugging Face",
    "ElevenLabs", "Resemble AI", "Play.ht", "Murf", "Speechify",
    "Descript", "Loom", "Vidyard", "Figma", "Canva", "Webflow"
]

# Remove duplicates while preserving order
seen = set()
COMPANIES = [x for x in COMPANIES if not (x in seen or seen.add(x))]

async def load_progress():
    """Load progress from file"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": [], "skipped": [], "failed": []}

async def save_progress(progress):
    """Save progress to file"""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

async def add_company_to_list(page, company_name):
    """Add ONLY the first search result to the target list"""
    print(f"\n{'='*60}")
    print(f"🔍 Processing: {company_name}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Search for company
        print("   1️⃣ Searching...")
        search_url = f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{company_name.replace(' ', '%20')})"
        await page.goto(search_url)
        await page.wait_for_timeout(4000)
        
        # Check if logged in
        if "login" in page.url:
            print("   ⚠️ Session expired - please log in")
            return {"status": "login_required"}
        
        # Step 2: Check if there are search results
        print("   2️⃣ Checking for results...")
        
        has_results = await page.evaluate('''
            () => {
                const resultItems = document.querySelectorAll('li.artdeco-list__item');
                return resultItems.length > 0;
            }
        ''')
        
        if not has_results:
            print("   ❌ No search results found")
            return {"status": "failed", "reason": "no_results"}
        
        # Step 3: Click the Save/Saved button on the FIRST result to open dropdown
        print("   3️⃣ Opening Save dropdown on first result...")
        
        clicked = await page.evaluate('''
            () => {
                const resultItems = document.querySelectorAll('li.artdeco-list__item');
                if (resultItems.length === 0) return false;
                
                const firstResult = resultItems[0];
                const buttons = firstResult.querySelectorAll('button');
                
                for (let btn of buttons) {
                    const text = btn.textContent.trim();
                    // Click either "Save" or "Saved" button to open dropdown
                    if (text === 'Save' || text === 'Saved') {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        ''')
        
        if not clicked:
            print("   ❌ Could not click Save button")
            return {"status": "failed", "reason": "click_failed"}
        
        await page.wait_for_timeout(1500)
        
        # Step 4: Check if "Outreach (ankit managed)" is already selected, if not select it
        print(f"   4️⃣ Looking for '{TARGET_LIST}' in dropdown...")
        
        result = await page.evaluate('''
            () => {
                // Find all LI elements in the dropdown
                const listItems = document.querySelectorAll('li');
                
                for (let li of listItems) {
                    const text = (li.textContent || '').trim();
                    
                    // Look for "Outreach (ankit managed)"
                    if (text.includes('Outreach') && text.includes('ankit managed')) {
                        const rect = li.getBoundingClientRect();
                        
                        // Must be visible in dropdown area
                        if (rect.height > 20 && rect.height < 60 && rect.top > 100 && rect.top < 700) {
                            
                            // Check for checkmark SVG - look for actual checkmark paths
                            const svgs = li.querySelectorAll('svg');
                            let hasCheckmark = false;
                            
                            for (let svg of svgs) {
                                const pathData = svg.innerHTML;
                                // Check for checkmark indicators
                                if (pathData.includes('check') || 
                                    svg.getAttribute('data-test-icon')?.includes('check')) {
                                    hasCheckmark = true;
                                    break;
                                }
                            }
                            
                            if (hasCheckmark) {
                                // Already in this list - skip
                                return { status: "already_selected", text: text.substring(0, 50) };
                            }
                            
                            // Not checked - click to add
                            li.click();
                            return { status: "clicked", text: text.substring(0, 50) };
                        }
                    }
                }
                
                return { status: "not_found" };
            }
        ''')
        
        if result.get("status") == "already_selected":
            print(f"   ⏭️ Already in list: {result.get('text', '')}")
            # Close dropdown
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(500)
            return {"status": "skipped", "reason": "already_in_list"}
        elif result.get("status") in ["clicked", "clicked_fallback"]:
            print(f"   ✅ Added to list: {result.get('text', '')}")
            await page.wait_for_timeout(1000)
            # Close dropdown
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(500)
            return {"status": "saved"}
        else:
            print(f"   ❌ Could not find '{TARGET_LIST}' in dropdown")
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(500)
            return {"status": "failed", "reason": "list_not_found"}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"status": "failed", "reason": str(e)}

async def main():
    print(f"\n{'#'*70}")
    print(f"# LinkedIn Sales Navigator Automation")
    print(f"# Target list: {TARGET_LIST}")
    print(f"# Companies: {len(COMPANIES)}")
    print(f"# NOTE: Only adds FIRST search result for each company")
    print(f"{'#'*70}\n")
    
    # Load progress
    progress = await load_progress()
    completed = set(progress.get("completed", []))
    skipped = set(progress.get("skipped", []))
    failed = set(progress.get("failed", []))
    
    # Filter companies not yet processed
    remaining = [c for c in COMPANIES if c not in completed and c not in skipped]
    print(f"📊 Progress: {len(completed)} saved, {len(skipped)} skipped, {len(failed)} failed")
    print(f"📋 Remaining: {len(remaining)} companies\n")
    
    if not remaining:
        print("✅ All companies have been processed!")
        return
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Check login
        print("🔐 Checking login status...")
        await page.goto("https://www.linkedin.com/sales/home")
        await page.wait_for_timeout(3000)
        
        if "login" in page.url:
            print("⚠️ Please log in to LinkedIn Sales Navigator in the browser...")
            print("   Waiting for login...")
            await page.wait_for_url("**/sales/**", timeout=300000)
            print("✅ Logged in!")
            await page.wait_for_timeout(2000)
        else:
            print("✅ Already logged in")
        
        # Process companies
        for i, company in enumerate(remaining):
            print(f"\n[{i+1}/{len(remaining)}] ", end="")
            
            try:
                result = await add_company_to_list(page, company)
                
                # Update progress
                if result["status"] == "saved":
                    progress["completed"].append(company)
                elif result["status"] == "skipped":
                    progress["skipped"].append(company)
                elif result["status"] == "failed":
                    progress["failed"].append(company)
                elif result["status"] == "login_required":
                    print("\n⚠️ Login required - stopping automation")
                    break
                
                # Save progress after each company
                await save_progress(progress)
                
                # Delay before next company
                if i < len(remaining) - 1:
                    delay = DELAY_BETWEEN_COMPANIES
                    if result["status"] == "skipped":
                        delay = 2  # Shorter delay for skipped
                    print(f"   ⏳ Waiting {delay}s...")
                    await page.wait_for_timeout(delay * 1000)
                    
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
                progress["failed"].append(company)
                await save_progress(progress)
                await page.wait_for_timeout(2000)
        
        # Final summary
        print(f"\n{'='*70}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*70}")
        print(f"   ✅ Saved: {len(progress['completed'])}")
        print(f"   ⏭️ Skipped: {len(progress['skipped'])}")
        print(f"   ❌ Failed: {len(progress['failed'])}")
        print(f"{'='*70}\n")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
