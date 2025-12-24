#!/usr/bin/env python3
"""
Opens browser for manual interaction - I'll watch what you click
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation" / "browser_data"

async def main():
    print("\n" + "="*70)
    print("🖱️  INTERACTIVE MODE - Please show me the clicks!")
    print("="*70)
    print("\nI'll open the browser. Please:")
    print("1. Search for a company (like OSlash)")
    print("2. Show me how to select it")
    print("3. Show me how to add it to 'Outreach (ankit managed)'")
    print("\nI'll watch the page state after each action.")
    print("="*70 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Navigate to Sales Navigator search
        print("📍 Navigating to LinkedIn Sales Navigator...")
        await page.goto("https://www.linkedin.com/sales/search/company?query=(keywords%3AOSlash)")
        await page.wait_for_timeout(3000)
        
        print(f"✅ Page loaded: {page.url}\n")
        
        # Now watch for changes
        print("👀 Watching for your clicks... (Press Ctrl+C when done)")
        print("-" * 70)
        
        last_url = page.url
        click_count = 0
        
        # Listen for console messages
        page.on("console", lambda msg: print(f"   [Console] {msg.text[:100]}") if msg.type == "log" else None)
        
        try:
            while True:
                await page.wait_for_timeout(2000)
                
                current_url = page.url
                if current_url != last_url:
                    print(f"\n🔄 URL changed to: {current_url}")
                    last_url = current_url
                
                # Check for any visible dropdowns or modals
                dropdowns = await page.query_selector_all('[role="listbox"], [role="menu"], [class*="dropdown"]')
                if dropdowns:
                    print(f"\n📋 Dropdown detected! Items:")
                    for dd in dropdowns[:1]:  # Just first dropdown
                        items = await dd.query_selector_all('[role="option"], [role="menuitem"], li')
                        for item in items[:10]:
                            text = await item.inner_text()
                            text = text.strip()[:60]
                            if text:
                                print(f"      - {text}")
                
                # Check for selected checkboxes
                checked = await page.query_selector_all('input[type="checkbox"]:checked')
                if checked:
                    print(f"\n☑️ {len(checked)} checkbox(es) selected")
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("📝 Session ended. Let me know what you observed!")
            print("="*70)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

