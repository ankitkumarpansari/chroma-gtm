#!/usr/bin/env python3
"""
LinkedIn Sales Navigator Automation with Playwright
Searches for companies and adds them to "Ankit Outreach" list

Flow:
1. Search for company name
2. Wait for search results
3. Click on the first company result to select it
4. Click "Save" button
5. Select "Ankit Outreach" from the list
6. Move to next company
"""

import asyncio
import json
import random
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Configuration
TARGET_LIST = "Outreach (ankit managed)"
USER_DATA_DIR = Path.home() / ".linkedin_sales_nav_automation"
PROGRESS_FILE = USER_DATA_DIR / "progress.json"
COMPANIES_FILE = Path(__file__).parent / "companies_for_linkedin.json"

# Delays (seconds)
SHORT_DELAY = 1
MEDIUM_DELAY = 2
LONG_DELAY = 4


def load_companies() -> list:
    """Load companies from JSON file."""
    if COMPANIES_FILE.exists():
        with open(COMPANIES_FILE, 'r') as f:
            data = json.load(f)
        companies = data.get('companies', [])
        print(f"✅ Loaded {len(companies)} companies from {COMPANIES_FILE.name}")
        return companies
    else:
        print(f"❌ Companies file not found: {COMPANIES_FILE}")
        return []


class LinkedInAutomation:
    def __init__(self):
        self.browser = None
        self.page: Page = None
        self.playwright = None
        self.progress = {"saved": [], "skipped": [], "failed": []}
        self.load_progress()
        
    def load_progress(self):
        """Load previous progress."""
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    self.progress = json.load(f)
                print(f"📊 Previous progress: {len(self.progress.get('saved', []))} saved, {len(self.progress.get('skipped', []))} skipped")
            except:
                pass
                
    def save_progress(self):
        """Save progress."""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2)
            
    async def setup(self):
        """Start browser."""
        print("\n🚀 Starting browser...")
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR / "browser_data"),
            headless=False,
            viewport={"width": 1400, "height": 900},
            slow_mo=50,
        )
        
        if self.browser.pages:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()
            
        self.page.set_default_timeout(30000)
        print("✅ Browser ready\n")
        
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def wait(self, seconds: float):
        """Wait with some randomness."""
        await asyncio.sleep(seconds + random.uniform(0.5, 1.5))
        
    async def ensure_logged_in(self):
        """Make sure we're logged into Sales Navigator."""
        print("🔐 Checking login status...")
        
        await self.page.goto("https://www.linkedin.com/sales/home")
        await self.wait(LONG_DELAY)
        
        # Check if on login page
        if "login" in self.page.url or "checkpoint" in self.page.url:
            print("\n" + "="*50)
            print("⚠️  PLEASE LOG IN TO LINKEDIN IN THE BROWSER")
            print("="*50)
            print("The script will continue once you're logged in...\n")
            
            # Wait for login
            while "login" in self.page.url or "checkpoint" in self.page.url:
                await asyncio.sleep(3)
                
            print("✅ Login detected!\n")
            await self.wait(MEDIUM_DELAY)
            
        print("✅ Logged into Sales Navigator\n")
        
    async def search_company(self, company_name: str) -> bool:
        """Search for a company and wait for results."""
        print(f"   🔍 Searching for '{company_name}'...")
        
        # Go to company search
        search_url = f"https://www.linkedin.com/sales/search/company?query=(keywords%3A{company_name.replace(' ', '%20')})"
        await self.page.goto(search_url)
        await self.wait(LONG_DELAY)
        
        # Wait for search results to load
        try:
            # Wait for either results or "no results" message
            await self.page.wait_for_selector(
                'button[aria-label*="Save"], [data-view-name="search-results"], .search-results__result-item',
                timeout=15000
            )
            print(f"   ✅ Search results loaded")
            return True
        except PlaywrightTimeout:
            # Check for no results
            content = await self.page.content()
            if "No results" in content or "0 result" in content:
                print(f"   ⚠️ No results found for '{company_name}'")
                return False
            print(f"   ⚠️ Timeout waiting for results")
            return False
            
    async def check_if_saved(self) -> bool:
        """Check if the first result is already saved to our list."""
        print(f"   🔍 Checking if already saved...")
        
        try:
            # Method 1: Look for "Saved" button that shows it's already in a list
            # Find the Save/Saved button
            save_button = await self.page.query_selector('button[aria-label*="Save"]')
            if not save_button:
                save_button = await self.page.query_selector('button:has-text("Saved")')
            if not save_button:
                save_button = await self.page.query_selector('button:has-text("Save")')
                
            if save_button:
                button_text = await save_button.inner_text()
                
                # If button shows "Saved" it means company is already saved somewhere
                if "Saved" in button_text:
                    # Click to open dropdown and check if it's in OUR list
                    await save_button.click()
                    await self.wait(SHORT_DELAY)
                    
                    # Look for our list with a checkmark
                    try:
                        # Find list items
                        list_items = await self.page.query_selector_all('[role="option"], [role="menuitem"], [role="listitem"], li')
                        
                        for item in list_items:
                            try:
                                text = await item.inner_text()
                                if "Outreach" in text and "ankit" in text.lower():
                                    # Check if this item has a checkmark (is selected)
                                    # Look for SVG checkmark or selected state
                                    checkmark = await item.query_selector('svg, [data-test-icon="checkmark"]')
                                    class_attr = await item.get_attribute('class') or ''
                                    aria_selected = await item.get_attribute('aria-selected')
                                    
                                    # Also check if text contains checkmark character or shows "(147)" etc
                                    if checkmark or 'selected' in class_attr.lower() or aria_selected == 'true':
                                        print(f"   ✅ Already saved to '{TARGET_LIST}' - skipping")
                                        # Close dropdown
                                        await self.page.keyboard.press('Escape')
                                        await self.wait(SHORT_DELAY)
                                        return True
                                        
                                    # Check if there's a checkmark visible next to it
                                    parent = await item.query_selector('xpath=..')
                                    if parent:
                                        parent_html = await parent.inner_html()
                                        if 'check' in parent_html.lower() or '✓' in parent_html:
                                            print(f"   ✅ Already saved to '{TARGET_LIST}' - skipping")
                                            await self.page.keyboard.press('Escape')
                                            await self.wait(SHORT_DELAY)
                                            return True
                            except:
                                continue
                                
                    except Exception as e:
                        print(f"   ⚠️ Error checking list: {e}")
                        
                    # Close dropdown - not in our list yet
                    await self.page.keyboard.press('Escape')
                    await self.wait(SHORT_DELAY)
                    return False
                    
            return False
            
        except Exception as e:
            print(f"   ⚠️ Error checking saved status: {e}")
            return False
        
    async def save_first_result(self) -> bool:
        """Click Save on the first search result and add to list."""
        print(f"   💾 Saving to '{TARGET_LIST}'...")
        
        try:
            # Step 1: Find and click the Save button
            save_button = await self.page.query_selector('button[aria-label*="Save"]')
            if not save_button:
                save_button = await self.page.query_selector('button:has-text("Save")')
            if not save_button:
                save_button = await self.page.query_selector('button:has-text("Saved")')
                
            if not save_button:
                print(f"   ❌ Could not find Save/Saved button")
                return False
                
            # Click the Save button to open dropdown
            print(f"   📌 Opening save dropdown...")
            await save_button.click()
            await self.wait(MEDIUM_DELAY)
            
            # Step 2: Find our list in the dropdown
            print(f"   🔍 Looking for '{TARGET_LIST}'...")
            await self.wait(SHORT_DELAY)
            
            # Look for list items containing "Outreach" and "ankit"
            list_items = await self.page.query_selector_all('div, span, li, button, a, [role="option"], [role="menuitem"]')
            
            target_item = None
            is_already_checked = False
            
            for item in list_items:
                try:
                    text = await item.inner_text()
                    if not text:
                        continue
                        
                    # Check if this is our target list
                    if "Outreach" in text and "ankit" in text.lower():
                        # Check if visible and reasonable size
                        if not await item.is_visible():
                            continue
                        box = await item.bounding_box()
                        if not box or box['height'] > 100:
                            continue
                            
                        # Check if already has checkmark (already selected)
                        # Look for checkmark SVG or selected indicator
                        item_html = await item.inner_html()
                        parent = await item.evaluate_handle('el => el.parentElement')
                        parent_html = ""
                        try:
                            parent_html = await parent.inner_html()
                        except:
                            pass
                            
                        # Check for checkmark indicators
                        if ('check' in item_html.lower() or 'check' in parent_html.lower() or 
                            '✓' in text or 'selected' in item_html.lower()):
                            print(f"   ✅ Already in '{TARGET_LIST}' - skipping!")
                            is_already_checked = True
                            break
                            
                        target_item = item
                        break
                except:
                    continue
                    
            # If already checked, close dropdown and return success (skipped)
            if is_already_checked:
                await self.page.keyboard.press('Escape')
                await self.wait(SHORT_DELAY)
                return True  # Return True because it's already saved
                
            # Click the target list item
            if target_item:
                print(f"   📋 Clicking on list...")
                await target_item.click()
                await self.wait(SHORT_DELAY)
                print(f"   ✅ Added to '{TARGET_LIST}'!")
                return True
            else:
                # Try alternative method - get_by_text
                try:
                    locator = self.page.get_by_text("Outreach (ankit managed)", exact=False)
                    if await locator.count() > 0:
                        await locator.first.click()
                        await self.wait(SHORT_DELAY)
                        print(f"   ✅ Added to list!")
                        return True
                except:
                    pass
                    
            print(f"   ⚠️ Could not find list '{TARGET_LIST}' in dropdown")
            await self.page.keyboard.press('Escape')
            await self.wait(SHORT_DELAY)
            return False
            
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
            try:
                await self.page.keyboard.press('Escape')
            except:
                pass
            return False
            
    async def process_company(self, company: dict) -> str:
        """Process one company. Returns: 'saved', 'skipped', or 'failed'."""
        name = company['name']
        
        print(f"\n{'='*60}")
        print(f"🏢 {name}")
        print(f"   Category: {company.get('category', 'N/A')}")
        print(f"{'='*60}")
        
        # Search
        found = await self.search_company(name)
        if not found:
            print(f"   ❌ FAILED - No results")
            return 'failed'
            
        # Check if already saved
        if await self.check_if_saved():
            print(f"   ⏭️ SKIPPED - Already saved")
            return 'skipped'
            
        # Save to list
        if await self.save_first_result():
            print(f"   ✅ SAVED")
            return 'saved'
        else:
            print(f"   ❌ FAILED - Could not save")
            return 'failed'
            
    async def run(self, companies: list):
        """Run automation on all companies."""
        # Filter out already processed
        already_done = set(self.progress.get('saved', []) + self.progress.get('skipped', []))
        to_process = [c for c in companies if c['name'] not in already_done]
        
        total = len(to_process)
        print(f"\n📋 Companies to process: {total}")
        print(f"📋 Target list: {TARGET_LIST}")
        print(f"📋 Already done: {len(already_done)}\n")
        
        if total == 0:
            print("✅ All companies already processed!")
            return
            
        await self.setup()
        
        try:
            await self.ensure_logged_in()
            
            for i, company in enumerate(to_process, 1):
                print(f"\n📊 Progress: {i}/{total}")
                
                result = await self.process_company(company)
                
                # Track progress
                self.progress[result].append(company['name'])
                self.save_progress()
                
                # Delay between companies
                if i < total:
                    delay = random.uniform(3, 6)
                    if result == 'skipped':
                        delay = delay / 2
                    print(f"\n   ⏳ Waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    
        except KeyboardInterrupt:
            print("\n\n⚠️ Stopped by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
        finally:
            # Summary
            print("\n" + "="*60)
            print("📊 SUMMARY")
            print("="*60)
            print(f"   ✅ Saved: {len(self.progress['saved'])}")
            print(f"   ⏭️ Skipped: {len(self.progress['skipped'])}")
            print(f"   ❌ Failed: {len(self.progress['failed'])}")
            print("="*60)
            
            await self.close()


async def main():
    companies = load_companies()
    if not companies:
        return
        
    print(f"\n{'='*60}")
    print("🎯 LinkedIn Sales Navigator Automation")
    print(f"{'='*60}")
    print(f"   Target list: {TARGET_LIST}")
    print(f"   Companies: {len(companies)}")
    print(f"{'='*60}\n")
    
    automation = LinkedInAutomation()
    await automation.run(companies)


if __name__ == "__main__":
    asyncio.run(main())
