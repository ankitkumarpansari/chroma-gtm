#!/usr/bin/env python3
"""
Interactive test - Opens browser, you click through, I'll capture each step
Press Enter in terminal after each action to capture the state
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"
COMPANY = "Mercor"
TARGET_LIST = "Outreach (ankit managed)"

async def capture_state(page, step_name):
    """Capture current page state"""
    print(f"\n{'='*60}")
    print(f"📸 CAPTURING: {step_name}")
    print(f"{'='*60}")
    print(f"URL: {page.url}")
    
    # Screenshot
    screenshot_path = f"/Users/ankitpansari/Desktop/Chroma GTM/step_{step_name.replace(' ', '_')}.png"
    await page.screenshot(path=screenshot_path)
    print(f"Screenshot: {screenshot_path}")
    
    # Checkboxes
    checkboxes = await page.query_selector_all('input[type="checkbox"]')
    checked = [cb for cb in checkboxes if await cb.is_checked()]
    print(f"\nCheckboxes: {len(checkboxes)} total, {len(checked)} checked")
    
    # Buttons with Save/List
    buttons = await page.query_selector_all('button')
    for btn in buttons:
        text = (await btn.inner_text()).strip()
        if text and ('save' in text.lower() or 'list' in text.lower()):
            visible = await btn.is_visible()
            print(f"  Button: '{text[:40]}' visible={visible}")
    
    # Dropdowns/Modals
    dropdowns = await page.query_selector_all('[role="listbox"], [role="menu"], [role="dialog"], [class*="dropdown__content"]')
    if dropdowns:
        print(f"\n🔽 DROPDOWN DETECTED ({len(dropdowns)}):")
        for dd in dropdowns:
            if await dd.is_visible():
                # Get all text items in dropdown
                html = await dd.inner_html()
                text = await dd.inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
                for line in lines[:15]:
                    marker = "✓" if "Outreach" in line and "ankit" in line.lower() else " "
                    print(f"    {marker} {line[:60]}")
    
    print(f"{'='*60}\n")

async def main():
    print(f"\n{'#'*70}")
    print(f"# INTERACTIVE TEST - Adding '{COMPANY}' to '{TARGET_LIST}'")
    print(f"{'#'*70}")
    print(f"\nI'll open the browser to search for {COMPANY}.")
    print("After each step, press ENTER here to capture the state.")
    print("This will help me understand the exact UI elements.\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Navigate to search
        print(f"📍 Navigating to search for '{COMPANY}'...")
        await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
        await page.wait_for_timeout(4000)
        
        if "login" in page.url:
            print("⚠️ Please log in to LinkedIn in the browser...")
            input("Press ENTER after logging in...")
            await page.goto(f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{COMPANY})")
            await page.wait_for_timeout(4000)
        
        # Capture initial state
        await capture_state(page, "1_search_results")
        
        print("\n" + "="*70)
        print("STEP 1: Click the checkbox next to Mercor to select it")
        print("="*70)
        input("Press ENTER after clicking the checkbox...")
        await capture_state(page, "2_after_checkbox")
        
        print("\n" + "="*70)
        print("STEP 2: Click the 'Save to list' button (in toolbar or on row)")
        print("="*70)
        input("Press ENTER after clicking Save to list...")
        await capture_state(page, "3_after_save_click")
        
        print("\n" + "="*70)
        print("STEP 3: Click on 'Outreach (ankit managed)' in the dropdown")
        print("="*70)
        input("Press ENTER after selecting the list...")
        await capture_state(page, "4_after_list_select")
        
        print("\n" + "#"*70)
        print("# DONE! Check the screenshots and output above.")
        print("#"*70)
        
        input("\nPress ENTER to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

