#!/usr/bin/env python3
"""Take screenshot of current browser"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"

async def main():
    async with async_playwright() as p:
        # Connect to existing browser
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print(f"Current URL: {page.url}")
        
        # Take screenshot
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/current_state.png", full_page=False)
        print("✅ Screenshot saved to current_state.png")
        
        # Get some page info
        print("\n--- Visible Elements ---")
        
        # Checkboxes
        checkboxes = await page.query_selector_all('input[type="checkbox"]')
        checked_count = 0
        for cb in checkboxes:
            if await cb.is_checked():
                checked_count += 1
        print(f"Checkboxes: {len(checkboxes)} total, {checked_count} checked")
        
        # Look for dropdown/modal
        dropdowns = await page.query_selector_all('[role="listbox"], [role="menu"], [role="dialog"]')
        print(f"Dropdowns/dialogs: {len(dropdowns)}")
        
        if dropdowns:
            for dd in dropdowns:
                items = await dd.query_selector_all('*')
                print(f"  Dropdown has {len(items)} elements")
                # Get text items
                for item in items[:20]:
                    text = await item.inner_text()
                    text = text.strip()
                    if text and len(text) < 80 and len(text) > 2:
                        print(f"    - {text}")
        
        # Don't close - keep browser open
        # await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

