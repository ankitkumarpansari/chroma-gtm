#!/usr/bin/env python3
"""
Test script - Open dropdown and show what's inside
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"
COMPANY = "Kore.ai"

async def main():
    print(f"\n🧪 Testing dropdown for '{COMPANY}'...\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            slow_mo=300,
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Search for company
        print("1️⃣ Searching...")
        await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
        await page.wait_for_timeout(4000)
        
        # Click Save button on first result
        print("2️⃣ Clicking Save button...")
        await page.evaluate('''
            () => {
                const resultItems = document.querySelectorAll('li.artdeco-list__item');
                if (resultItems.length === 0) return false;
                const firstResult = resultItems[0];
                const buttons = firstResult.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = btn.textContent.trim();
                    if (text === 'Save' || text === 'Saved') {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        ''')
        
        await page.wait_for_timeout(2000)
        
        # Take screenshot
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/dropdown_debug.png")
        print("📸 Screenshot saved: dropdown_debug.png")
        
        # Get dropdown contents
        print("\n3️⃣ Dropdown contents:")
        items = await page.evaluate('''
            () => {
                const results = [];
                // Get all potential list items
                const allElements = document.querySelectorAll('*');
                
                for (let el of allElements) {
                    const text = (el.textContent || '').trim();
                    const rect = el.getBoundingClientRect();
                    
                    // Look for items containing "Outreach" or list-related text
                    if (text.includes('Outreach') || text.includes('List') || text.includes('Account')) {
                        if (rect.height > 20 && rect.height < 80 && rect.width > 100 && rect.top > 0) {
                            // Check for checkmark
                            const hasSvg = el.querySelector('svg') !== null;
                            const parentHasSvg = el.parentElement?.querySelector('svg') !== null;
                            
                            results.push({
                                text: text.substring(0, 80),
                                tag: el.tagName,
                                hasCheckmark: hasSvg || parentHasSvg,
                                height: rect.height,
                                width: rect.width
                            });
                        }
                    }
                }
                
                // Deduplicate
                const seen = new Set();
                return results.filter(r => {
                    if (seen.has(r.text)) return false;
                    seen.add(r.text);
                    return true;
                }).slice(0, 15);
            }
        ''')
        
        for item in items:
            check = "✓" if item.get("hasCheckmark") else " "
            print(f"   [{check}] {item['tag']}: {item['text'][:60]}")
        
        print("\n4️⃣ Now clicking on 'Outreach (ankit managed)'...")
        
        # Try to click on the list
        clicked = await page.evaluate('''
            () => {
                // Find all elements
                const allElements = document.querySelectorAll('li, div, span, button');
                
                for (let el of allElements) {
                    const text = (el.textContent || '').trim();
                    
                    // Look for "Outreach (ankit managed)"
                    if (text.includes('Outreach') && text.includes('ankit')) {
                        const rect = el.getBoundingClientRect();
                        
                        // Must be visible and reasonable size
                        if (rect.height > 20 && rect.height < 60 && rect.width > 100 && rect.top > 100) {
                            console.log('Clicking:', text.substring(0, 50), 'tag:', el.tagName);
                            el.click();
                            return { clicked: true, text: text.substring(0, 50), tag: el.tagName };
                        }
                    }
                }
                return { clicked: false };
            }
        ''')
        
        print(f"   Result: {clicked}")
        
        await page.wait_for_timeout(2000)
        
        # Take final screenshot
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/after_click.png")
        print("📸 Screenshot saved: after_click.png")
        
        print("\nBrowser staying open for 20 seconds...")
        await page.wait_for_timeout(20000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

