#!/usr/bin/env python3
"""Capture current browser state"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        contexts = browser.contexts
        if not contexts:
            print("No browser contexts found")
            return
            
        pages = contexts[0].pages
        if not pages:
            print("No pages found")
            return
            
        page = pages[0]
        print(f"Current URL: {page.url}")
        print(f"Title: {await page.title()}")
        
        # Take screenshot
        await page.screenshot(path="/Users/ankitpansari/Desktop/Chroma GTM/current_state.png")
        print("Screenshot saved to current_state.png")
        
        # Get page structure
        print("\n--- Page Elements ---")
        
        # Check for checkboxes
        checkboxes = await page.query_selector_all('input[type="checkbox"]')
        print(f"Checkboxes: {len(checkboxes)}")
        for i, cb in enumerate(checkboxes[:5]):
            checked = await cb.is_checked()
            aria = await cb.get_attribute('aria-label') or ''
            print(f"  [{i}] checked={checked} aria='{aria[:40]}'")
        
        # Check for buttons with Save
        buttons = await page.query_selector_all('button')
        save_buttons = []
        for btn in buttons:
            text = await btn.inner_text()
            if 'save' in text.lower() or 'list' in text.lower():
                save_buttons.append(text.strip()[:50])
        print(f"\nSave/List buttons: {save_buttons}")
        
        # Check for dropdowns
        dropdowns = await page.query_selector_all('[role="listbox"], [role="menu"], [class*="dropdown"]')
        print(f"\nDropdowns visible: {len(dropdowns)}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

