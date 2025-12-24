#!/usr/bin/env python3
"""
Test script - Add a single company (OSlash) to LinkedIn Sales Navigator
Correct flow:
1. Search for company
2. Click checkbox to select the first result
3. Click "Save to list" in toolbar
4. Select "Outreach (ankit managed)" from dropdown
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

TARGET_LIST = "Outreach (ankit managed)"
USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation"
COMPANY_NAME = "OSlash"


async def main():
    print(f"\n{'='*60}")
    print(f"🧪 TEST: Adding '{COMPANY_NAME}' to '{TARGET_LIST}'")
    print(f"{'='*60}\n")
    
    playwright = await async_playwright().start()
    
    # Launch browser with saved session
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR / "browser_data"),
        headless=False,
        viewport={"width": 1400, "height": 900},
        slow_mo=200,  # Slow down so we can see what's happening
    )
    
    page = browser.pages[0] if browser.pages else await browser.new_page()
    page.set_default_timeout(30000)
    
    try:
        # Step 1: Go to Sales Navigator and check login
        print("1️⃣ Checking login...")
        await page.goto("https://www.linkedin.com/sales/home")
        await asyncio.sleep(3)
        
        if "login" in page.url:
            print("   ⚠️ Please log in to LinkedIn in the browser window...")
            while "login" in page.url:
                await asyncio.sleep(2)
            print("   ✅ Logged in!")
            await asyncio.sleep(2)
        else:
            print("   ✅ Already logged in")
            
        # Step 2: Search for the company
        print(f"\n2️⃣ Searching for '{COMPANY_NAME}'...")
        search_url = f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY_NAME})"
        await page.goto(search_url)
        await asyncio.sleep(4)
        print("   ✅ Search page loaded")
        
        # Step 3: Check if company is already saved (look for "Saved" button instead of "Save")
        print(f"\n3️⃣ Checking if '{COMPANY_NAME}' is already saved...")
        
        # Find the first result row
        first_result = await page.query_selector('li[class*="artdeco-list__item"]')
        if first_result:
            # Check if it has "Saved" button (meaning already saved)
            saved_button = await first_result.query_selector('button:has-text("Saved")')
            if saved_button:
                print(f"   ⏭️ '{COMPANY_NAME}' is already saved - checking which list...")
                # Click the Saved button to see dropdown
                await saved_button.click()
                await asyncio.sleep(1.5)
                
                # Check if our list is checked
                page_content = await page.content()
                if TARGET_LIST in page_content:
                    # Look for checkmark next to our list
                    list_item = await page.query_selector(f'text="{TARGET_LIST}"')
                    if list_item:
                        parent = await list_item.evaluate_handle('el => el.closest("li") || el.parentElement')
                        parent_html = await parent.inner_html() if parent else ""
                        if "check" in parent_html.lower() or "✓" in parent_html:
                            print(f"   ✅ Already in '{TARGET_LIST}' - SKIPPING")
                            await page.keyboard.press('Escape')
                            return
                
                # Not in our list yet, need to add
                print(f"   📋 Adding to '{TARGET_LIST}'...")
                # Find and click our list
                list_items = await page.query_selector_all('div, span, li')
                for item in list_items:
                    try:
                        text = await item.inner_text()
                        if text and "Outreach" in text and "ankit" in text.lower() and len(text) < 100:
                            if await item.is_visible():
                                box = await item.bounding_box()
                                if box and 15 < box['height'] < 80:
                                    print(f"   📌 Clicking '{text.strip()[:40]}'...")
                                    await item.click()
                                    await asyncio.sleep(1)
                                    print(f"   ✅ Added to '{TARGET_LIST}'!")
                                    return
                    except:
                        continue
                
                await page.keyboard.press('Escape')
                print("   ⚠️ Could not find list in dropdown")
                return
        
        # Step 4: Click the checkbox to select the first result
        print(f"\n4️⃣ Selecting first result (checkbox)...")
        
        # Find checkboxes - skip "Select all"
        checkboxes = await page.query_selector_all('input[type="checkbox"]')
        print(f"   Found {len(checkboxes)} checkboxes")
        
        clicked = False
        for i, cb in enumerate(checkboxes):
            try:
                # Get aria-label to skip "Select all"
                aria = await cb.get_attribute('aria-label') or ''
                id_attr = await cb.get_attribute('id') or ''
                
                if 'select all' in aria.lower() or 'select-all' in id_attr.lower():
                    print(f"   Skipping checkbox {i} (Select all)")
                    continue
                    
                # Check if visible
                if await cb.is_visible():
                    print(f"   📌 Clicking checkbox {i}...")
                    await cb.click()
                    await asyncio.sleep(1)
                    clicked = True
                    print(f"   ✅ Checkbox clicked!")
                    break
            except Exception as e:
                print(f"   Error with checkbox {i}: {e}")
                continue
                
        if not clicked:
            print("   ❌ Could not click any checkbox")
            await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_checkbox_fail.png")
            return
            
        # Take screenshot after selecting
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_after_select.png")
        print("   📸 Screenshot: debug_after_select.png")
        
        # Step 5: Click "Save to list" in the toolbar
        print(f"\n5️⃣ Clicking 'Save to list' in toolbar...")
        
        # Look for "Save to list" button in toolbar
        save_to_list = await page.query_selector('button:has-text("Save to list")')
        if not save_to_list:
            # Try finding by partial text
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if 'save' in text.lower() and 'list' in text.lower():
                    save_to_list = btn
                    break
                    
        if save_to_list:
            print("   📌 Clicking 'Save to list'...")
            await save_to_list.click()
            await asyncio.sleep(2)
            print("   ✅ Dropdown should be open")
        else:
            print("   ❌ Could not find 'Save to list' button")
            await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_no_save_btn.png")
            return
            
        # Take screenshot of dropdown
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_dropdown.png")
        print("   📸 Screenshot: debug_dropdown.png")
        
        # Step 6: Select our list from dropdown
        print(f"\n6️⃣ Selecting '{TARGET_LIST}' from dropdown...")
        
        # Find and click our list
        found = False
        all_elements = await page.query_selector_all('div, span, li, button, a')
        
        for elem in all_elements:
            try:
                text = await elem.inner_text()
                if not text:
                    continue
                    
                if "Outreach" in text and "ankit" in text.lower() and len(text) < 100:
                    if await elem.is_visible():
                        box = await elem.bounding_box()
                        if box and 15 < box['height'] < 80:
                            print(f"   📌 Found '{text.strip()[:40]}' - clicking...")
                            await elem.click()
                            await asyncio.sleep(1)
                            found = True
                            print(f"   ✅ Added to '{TARGET_LIST}'!")
                            break
            except:
                continue
                
        if not found:
            print("   ❌ Could not find list in dropdown")
            await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_list_not_found.png")
        else:
            await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_success.png")
            print(f"\n✅ SUCCESS! '{COMPANY_NAME}' added to '{TARGET_LIST}'")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/debug_error.png")
        
    finally:
        print("\n" + "="*60)
        print("Test complete. Browser will stay open for inspection.")
        print("Press Ctrl+C to close.")
        print("="*60)
        
        # Keep browser open for a bit
        try:
            await asyncio.sleep(30)
        except:
            pass
            
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(main())
