#!/usr/bin/env python3
"""
Add Mercor to 'Outreach (ankit managed)' list
Based on observed UI structure:
1. Click checkbox next to company
2. Click "Save to list" in toolbar
3. Select list from dropdown
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"
COMPANY = "Mercor"
TARGET_LIST = "Outreach (ankit managed)"

async def main():
    print(f"\n{'='*60}")
    print(f"🎯 Adding '{COMPANY}' to '{TARGET_LIST}'")
    print(f"{'='*60}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            slow_mo=300,  # Slow down to see actions
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        try:
            # Step 1: Navigate to search
            print("1️⃣ Searching for Mercor...")
            await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
            await page.wait_for_timeout(4000)
            
            if "login" in page.url:
                print("   ⚠️ Please log in manually...")
                await page.wait_for_url("**/sales/**", timeout=120000)
                await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
                await page.wait_for_timeout(4000)
            
            print(f"   ✅ Search results loaded")
            
            # Step 2: Find and click the checkbox for the SECOND result (Software Development, 3K+ employees)
            print("\n2️⃣ Selecting Mercor (Software Development)...")
            
            # Get all checkboxes
            checkboxes = await page.query_selector_all('input[type="checkbox"]')
            print(f"   Found {len(checkboxes)} checkboxes")
            
            # Skip first checkbox (Select All) and click the second one (first company result)
            # Actually we want the SECOND company (Software Development with 3K+ employees)
            # Checkboxes: 0=Select All, 1=MERCOR Construction, 2=Mercor Software Dev
            
            target_index = 2  # Third checkbox = second company result (Mercor Software Development)
            
            if len(checkboxes) > target_index:
                cb = checkboxes[target_index]
                # Use JavaScript click to avoid interception
                await page.evaluate('(cb) => cb.click()', cb)
                await page.wait_for_timeout(1500)
                
                # Verify it's checked
                is_checked = await cb.is_checked()
                print(f"   ✅ Checkbox clicked, checked={is_checked}")
            else:
                print(f"   ❌ Not enough checkboxes found")
                return
            
            # Step 3: Click "Save to list" button in toolbar
            print("\n3️⃣ Clicking 'Save to list'...")
            
            # Find the "Save to list" button in toolbar
            save_to_list_btn = await page.query_selector('button:has-text("Save to list")')
            
            if save_to_list_btn:
                # Check if it's enabled now
                is_disabled = await save_to_list_btn.get_attribute('disabled')
                print(f"   Button found, disabled={is_disabled}")
                
                await save_to_list_btn.click()
                await page.wait_for_timeout(2000)
                print(f"   ✅ Clicked 'Save to list'")
            else:
                print(f"   ❌ 'Save to list' button not found")
                # Try alternative
                await page.evaluate('''
                    () => {
                        const buttons = document.querySelectorAll('button');
                        for (let btn of buttons) {
                            if (btn.textContent.toLowerCase().includes('save to list')) {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    }
                ''')
                await page.wait_for_timeout(2000)
            
            # Take screenshot to see dropdown
            await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/dropdown_state.png")
            print("   📸 Screenshot saved: dropdown_state.png")
            
            # Step 4: Select our list from dropdown
            print(f"\n4️⃣ Selecting '{TARGET_LIST}'...")
            
            # Wait for dropdown to appear
            await page.wait_for_timeout(1000)
            
            # Find and click our list
            # Look for text containing "Outreach" and "ankit"
            clicked = await page.evaluate('''
                (targetText) => {
                    // Find all clickable elements
                    const elements = document.querySelectorAll('li, div, span, button, a, [role="option"], [role="menuitem"]');
                    
                    for (let el of elements) {
                        const text = el.textContent || '';
                        if (text.includes('Outreach') && text.toLowerCase().includes('ankit')) {
                            // Check if it's a reasonable size (not a container)
                            const rect = el.getBoundingClientRect();
                            if (rect.height > 10 && rect.height < 100 && rect.width > 50) {
                                console.log('Found:', text.substring(0, 50));
                                el.click();
                                return text.substring(0, 60);
                            }
                        }
                    }
                    return null;
                }
            ''', TARGET_LIST)
            
            if clicked:
                print(f"   ✅ Clicked: '{clicked}'")
                await page.wait_for_timeout(1500)
                
                # Take final screenshot
                await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/final_state.png")
                print("\n🎉 SUCCESS! Mercor added to list!")
            else:
                print(f"   ❌ Could not find '{TARGET_LIST}' in dropdown")
                
                # Debug: show what's in dropdown
                items = await page.evaluate('''
                    () => {
                        const items = [];
                        const elements = document.querySelectorAll('[role="option"], [role="menuitem"], [role="listitem"], li');
                        for (let el of elements) {
                            const text = (el.textContent || '').trim();
                            const rect = el.getBoundingClientRect();
                            if (text && text.length < 100 && rect.height > 10) {
                                items.push(text.substring(0, 70));
                            }
                        }
                        return items.slice(0, 20);
                    }
                ''')
                print("   Available items in dropdown:")
                for item in items:
                    print(f"      - {item}")
            
            print("\n" + "="*60)
            print("Browser will stay open for 20 seconds...")
            await page.wait_for_timeout(20000)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

