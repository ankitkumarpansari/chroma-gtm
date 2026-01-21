#!/usr/bin/env python3
"""Quick test - inspect dropdown structure"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"
TARGET_LIST = "Outreach (ankit managed)"
COMPANY = "Hebbia"  # Try a different company

async def main():
    print(f"\n🧪 Test: Adding '{COMPANY}' to '{TARGET_LIST}'\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            slow_mo=500,
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Step 1: Search
        print("1️⃣ Searching...")
        await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
        await page.wait_for_timeout(4000)
        
        # Step 2: Click Save on first result
        print("\n2️⃣ Clicking Save button...")
        await page.evaluate('''
            () => {
                const resultItems = document.querySelectorAll('li.artdeco-list__item');
                if (resultItems.length === 0) return;
                const firstResult = resultItems[0];
                const buttons = firstResult.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = btn.textContent.trim();
                    if (text === 'Save' || text === 'Saved') {
                        btn.click();
                        return;
                    }
                }
            }
        ''')
        
        await page.wait_for_timeout(2000)
        
        # Take screenshot with dropdown open
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/dropdown_open.png")
        print("📸 Screenshot: dropdown_open.png")
        
        # Step 3: Analyze dropdown structure
        print("\n3️⃣ Analyzing dropdown structure...")
        
        items = await page.evaluate('''
            () => {
                const results = [];
                
                // Find all LI elements that might be list options
                const listItems = document.querySelectorAll('li');
                
                for (let li of listItems) {
                    const text = (li.textContent || '').trim();
                    
                    // Only interested in items with "Outreach" or list names
                    if (text.includes('Outreach') || text.includes('Account') || text.includes('Competitor')) {
                        const rect = li.getBoundingClientRect();
                        
                        if (rect.height > 20 && rect.height < 60 && rect.top > 100 && rect.top < 700) {
                            // Check for checkmark - look for specific checkmark indicators
                            const svgs = li.querySelectorAll('svg');
                            let hasCheckmark = false;
                            
                            for (let svg of svgs) {
                                // Check SVG attributes or path data for checkmark
                                const pathData = svg.innerHTML;
                                if (pathData.includes('check') || 
                                    pathData.includes('M16 8') ||  // Common checkmark path start
                                    svg.getAttribute('data-test-icon')?.includes('check')) {
                                    hasCheckmark = true;
                                    break;
                                }
                            }
                            
                            // Also check aria-checked attribute
                            const ariaChecked = li.getAttribute('aria-checked') === 'true' ||
                                               li.querySelector('[aria-checked="true"]') !== null;
                            
                            // Check for selected class
                            const hasSelectedClass = li.className.includes('selected') ||
                                                     li.className.includes('active') ||
                                                     li.className.includes('checked');
                            
                            results.push({
                                text: text.substring(0, 50).replace(/\\n/g, ' ').trim(),
                                hasCheckmark: hasCheckmark,
                                ariaChecked: ariaChecked,
                                hasSelectedClass: hasSelectedClass,
                                svgCount: svgs.length,
                                top: Math.round(rect.top)
                            });
                        }
                    }
                }
                
                return results;
            }
        ''')
        
        print("\n   Dropdown items found:")
        for item in items:
            check = "✓" if (item.get('hasCheckmark') or item.get('ariaChecked')) else " "
            print(f"   [{check}] {item['text'][:40]} (svgs:{item['svgCount']}, top:{item['top']})")
        
        # Step 4: Now try to click on "Outreach (ankit managed)" if not checked
        print(f"\n4️⃣ Clicking on '{TARGET_LIST}'...")
        
        result = await page.evaluate('''
            () => {
                const listItems = document.querySelectorAll('li');
                
                for (let li of listItems) {
                    const text = (li.textContent || '').trim();
                    
                    if (text.includes('Outreach') && text.includes('ankit managed')) {
                        const rect = li.getBoundingClientRect();
                        
                        if (rect.height > 20 && rect.height < 60 && rect.top > 100 && rect.top < 700) {
                            // Check if already selected
                            const svgs = li.querySelectorAll('svg');
                            let hasCheckmark = false;
                            
                            for (let svg of svgs) {
                                const pathData = svg.innerHTML;
                                if (pathData.includes('check') || 
                                    svg.getAttribute('data-test-icon')?.includes('check')) {
                                    hasCheckmark = true;
                                    break;
                                }
                            }
                            
                            if (hasCheckmark) {
                                return { status: "already_checked", text: text.substring(0, 40) };
                            }
                            
                            // Not checked - click it
                            li.click();
                            return { status: "clicked", text: text.substring(0, 40) };
                        }
                    }
                }
                return { status: "not_found" };
            }
        ''')
        
        print(f"   Result: {result}")
        
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/after_click.png")
        
        print("\nBrowser open for 15 seconds...")
        await page.wait_for_timeout(15000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
