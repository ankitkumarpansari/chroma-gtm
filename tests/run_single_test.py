#!/usr/bin/env python3
"""
Simple test - Add OSlash to LinkedIn Sales Navigator using existing session
Uses JavaScript clicks to avoid element interception issues
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

# Use the existing browser data directory with saved session
USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"
TARGET_LIST = "Outreach (ankit managed)"
COMPANY = "OSlash"

async def js_click(page, selector):
    """Click element using JavaScript to avoid interception issues"""
    await page.evaluate(f'''
        const el = document.querySelector('{selector}');
        if (el) el.click();
    ''')

async def main():
    print(f"\n{'='*60}")
    print(f"🧪 Adding '{COMPANY}' to '{TARGET_LIST}'")
    print(f"   Using saved session at: {USER_DATA_DIR}")
    print(f"{'='*60}\n")
    
    async with async_playwright() as p:
        # Launch with existing user data (has saved cookies/session)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            slow_mo=200,
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        try:
            # Step 1: Go to search page for OSlash
            print("1️⃣ Navigating to search page...")
            await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
            await page.wait_for_timeout(4000)
            print(f"   Current URL: {page.url}")
            
            # Check if we're logged in
            if "login" in page.url:
                print("   ⚠️ Not logged in! Please log in manually in the browser...")
                await page.wait_for_url("**/sales/**", timeout=120000)
                print("   ✅ Login detected!")
                await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
                await page.wait_for_timeout(4000)
            
            print(f"   ✅ On search page")
            
            # Step 2: Wait for results to load
            print("\n2️⃣ Waiting for search results...")
            await page.wait_for_timeout(3000)
            
            # Check if OSlash is in results
            content = await page.content()
            if "OSlash" not in content:
                print("   ❌ OSlash not found in search results")
                return
            print("   ✅ OSlash found in results!")
            
            # Step 3: Click the first checkbox using JavaScript
            print("\n3️⃣ Selecting the first company...")
            
            # Use JavaScript to click the first non-select-all checkbox
            clicked = await page.evaluate('''
                () => {
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    for (let cb of checkboxes) {
                        const aria = (cb.getAttribute('aria-label') || '').toLowerCase();
                        const id = (cb.id || '').toLowerCase();
                        if (aria.includes('select all') || id.includes('select-all')) continue;
                        cb.click();
                        return true;
                    }
                    return false;
                }
            ''')
            
            if clicked:
                print("   ✅ Checkbox clicked!")
                await page.wait_for_timeout(1500)
            else:
                print("   ❌ Could not click checkbox")
                return
            
            # Step 4: Click "Save to list" button
            print("\n4️⃣ Clicking 'Save to list'...")
            
            # Use JavaScript to find and click the Save to list button
            save_clicked = await page.evaluate('''
                () => {
                    const buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('save') && text.includes('list')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            ''')
            
            if save_clicked:
                print("   ✅ 'Save to list' clicked!")
                await page.wait_for_timeout(2000)
            else:
                print("   ❌ Could not find 'Save to list' button")
                # Try alternative: look for any button with "Save"
                buttons = await page.query_selector_all('button')
                print(f"   Found {len(buttons)} buttons. Looking for alternatives...")
                for btn in buttons[:20]:
                    text = await btn.inner_text()
                    text = text.strip()[:50]
                    if text and ('save' in text.lower() or 'list' in text.lower()):
                        print(f"      Found: '{text}'")
                return
            
            # Step 5: Select our list from dropdown
            print(f"\n5️⃣ Selecting '{TARGET_LIST}'...")
            await page.wait_for_timeout(1000)
            
            # Use JavaScript to find and click our list
            list_clicked = await page.evaluate('''
                (targetList) => {
                    const elements = document.querySelectorAll('*');
                    for (let el of elements) {
                        const text = el.textContent || '';
                        if (text.includes('Outreach') && text.toLowerCase().includes('ankit') && text.length < 100) {
                            const rect = el.getBoundingClientRect();
                            if (rect.height > 15 && rect.height < 80 && rect.width > 50) {
                                el.click();
                                return text.trim().substring(0, 50);
                            }
                        }
                    }
                    return null;
                }
            ''', TARGET_LIST)
            
            if list_clicked:
                print(f"   ✅ Clicked: '{list_clicked}'")
                await page.wait_for_timeout(1000)
                print(f"\n🎉 SUCCESS! '{COMPANY}' added to '{TARGET_LIST}'")
            else:
                print("   ❌ Could not find list in dropdown")
                # Show what's in the dropdown
                dropdown_items = await page.evaluate('''
                    () => {
                        const items = [];
                        const elements = document.querySelectorAll('[role="option"], [role="menuitem"], li');
                        for (let el of elements) {
                            const text = (el.textContent || '').trim();
                            if (text && text.length < 100) {
                                items.push(text.substring(0, 60));
                            }
                        }
                        return items.slice(0, 15);
                    }
                ''')
                print("   Dropdown items found:")
                for item in dropdown_items:
                    print(f"      - {item}")
            
            # Keep browser open for inspection
            print("\n" + "="*60)
            print("Browser will stay open for 30 seconds...")
            print("="*60)
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
