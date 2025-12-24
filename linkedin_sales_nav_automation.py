#!/usr/bin/env python3
"""
LinkedIn Sales Navigator Company Automation
============================================

This script automates adding companies to your LinkedIn Sales Navigator account.
It searches for each company and saves them to your account.

Usage:
    1. First install dependencies: pip install playwright && playwright install chromium
    2. Run: python linkedin_sales_nav_automation.py
    3. Login to LinkedIn manually when the browser opens
    4. The script will then automate adding companies

Author: Automation Script
"""

import asyncio
import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Company:
    """Company data structure"""
    name: str
    category: str
    valuation: str = ""
    priority: str = ""
    status: str = "pending"  # pending, found, saved, not_found, error
    linkedin_url: str = ""
    error_message: str = ""


# ============================================================================
# COMPANY DATA - Parsed from your research document
# ============================================================================

COMPANIES_DATA = [
    # Category 1: Documentation Platforms
    {"name": "Mintlify", "category": "Documentation Platforms", "valuation": "~$100M", "priority": "HIGH"},
    {"name": "GitBook", "category": "Documentation Platforms", "valuation": "N/A", "priority": "HIGH"},
    {"name": "ReadMe", "category": "Documentation Platforms", "valuation": "~$100M+", "priority": "HIGH"},
    {"name": "Swimm", "category": "Documentation Platforms", "valuation": "~$150M", "priority": "MEDIUM-HIGH"},
    {"name": "Redocly", "category": "Documentation Platforms", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Archbee", "category": "Documentation Platforms", "valuation": "~$20M", "priority": "MEDIUM"},
    {"name": "Bump.sh", "category": "Documentation Platforms", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Theneo", "category": "Documentation Platforms", "valuation": "~$10M", "priority": "MEDIUM"},
    {"name": "Doctave", "category": "Documentation Platforms", "valuation": "N/A", "priority": "LOW"},
    
    # Category 2: Developer Tools and Code Assistants
    {"name": "Cursor", "category": "Developer Tools", "valuation": "$29.3B", "priority": "HIGH"},
    {"name": "Anysphere", "category": "Developer Tools", "valuation": "$29.3B", "priority": "HIGH"},
    {"name": "Cognition", "category": "Developer Tools", "valuation": "$10.2B", "priority": "HIGH"},
    {"name": "Poolside AI", "category": "Developer Tools", "valuation": "$12B", "priority": "HIGH"},
    {"name": "Magic AI", "category": "Developer Tools", "valuation": "~$1.5B", "priority": "HIGH"},
    {"name": "Augment Code", "category": "Developer Tools", "valuation": "$977M", "priority": "HIGH"},
    {"name": "Qodo", "category": "Developer Tools", "valuation": "~$200M", "priority": "HIGH"},
    {"name": "Replit", "category": "Developer Tools", "valuation": "$1.16B", "priority": "HIGH"},
    {"name": "Semgrep", "category": "Developer Tools", "valuation": "~$800M", "priority": "HIGH"},
    {"name": "Sourcegraph", "category": "Developer Tools", "valuation": "$2.6B", "priority": "HIGH"},
    {"name": "Tabnine", "category": "Developer Tools", "valuation": "~$300M", "priority": "MEDIUM-HIGH"},
    {"name": "Continue.dev", "category": "Developer Tools", "valuation": "N/A", "priority": "MEDIUM"},
    
    # Category 3: Legal Tech
    {"name": "Harvey AI", "category": "Legal Tech", "valuation": "$8B", "priority": "HIGH"},
    {"name": "Clio", "category": "Legal Tech", "valuation": "$5B", "priority": "HIGH"},
    {"name": "Spellbook", "category": "Legal Tech", "valuation": "$350M", "priority": "HIGH"},
    {"name": "Luminance", "category": "Legal Tech", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Ironclad", "category": "Legal Tech", "valuation": "$3.2B", "priority": "HIGH"},
    {"name": "ContractPodAi", "category": "Legal Tech", "valuation": "~$500M", "priority": "MEDIUM-HIGH"},
    {"name": "Summize", "category": "Legal Tech", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Definely", "category": "Legal Tech", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "ThoughtRiver", "category": "Legal Tech", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Diligen", "category": "Legal Tech", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "LegalSifter", "category": "Legal Tech", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "LinkSquares", "category": "Legal Tech", "valuation": "~$800M", "priority": "MEDIUM"},
    {"name": "Ontra", "category": "Legal Tech", "valuation": "~$500M", "priority": "MEDIUM-LOW"},
    
    # Category 4: Sales and Revenue Intelligence
    {"name": "Clay", "category": "Sales Intelligence", "valuation": "$3.1B", "priority": "HIGH"},
    {"name": "Apollo.io", "category": "Sales Intelligence", "valuation": "$1.6B", "priority": "HIGH"},
    {"name": "Gong", "category": "Sales Intelligence", "valuation": "$7.25B", "priority": "HIGH"},
    {"name": "ZoomInfo", "category": "Sales Intelligence", "valuation": "~$8B", "priority": "HIGH"},
    {"name": "6sense", "category": "Sales Intelligence", "valuation": "$5.2B", "priority": "MEDIUM-HIGH"},
    {"name": "Outreach", "category": "Sales Intelligence", "valuation": "$4.4B", "priority": "MEDIUM-HIGH"},
    {"name": "Salesloft", "category": "Sales Intelligence", "valuation": "$2.3B", "priority": "MEDIUM-HIGH"},
    {"name": "Seismic", "category": "Sales Intelligence", "valuation": "$3B", "priority": "MEDIUM"},
    {"name": "Highspot", "category": "Sales Intelligence", "valuation": "$3.5B", "priority": "MEDIUM"},
    {"name": "Nooks", "category": "Sales Intelligence", "valuation": "~$300M", "priority": "MEDIUM-HIGH"},
    {"name": "Lusha", "category": "Sales Intelligence", "valuation": "$1.5B", "priority": "MEDIUM"},
    {"name": "Regie.ai", "category": "Sales Intelligence", "valuation": "~$150M", "priority": "MEDIUM"},
    {"name": "People.ai", "category": "Sales Intelligence", "valuation": "$1.1B", "priority": "MEDIUM-LOW"},
    {"name": "Orum", "category": "Sales Intelligence", "valuation": "N/A", "priority": "MEDIUM-LOW"},
    {"name": "Instantly.ai", "category": "Sales Intelligence", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Lemlist", "category": "Sales Intelligence", "valuation": "N/A", "priority": "MEDIUM-LOW"},
    {"name": "Demandbase", "category": "Sales Intelligence", "valuation": "N/A", "priority": "MEDIUM-LOW"},
    {"name": "Bombora", "category": "Sales Intelligence", "valuation": "N/A", "priority": "MEDIUM"},
    
    # Category 5: Customer Support AI
    {"name": "Sierra AI", "category": "Customer Support AI", "valuation": "$10B", "priority": "HIGH"},
    {"name": "Decagon", "category": "Customer Support AI", "valuation": "$1.5B", "priority": "HIGH"},
    {"name": "Intercom", "category": "Customer Support AI", "valuation": "$1B+", "priority": "MEDIUM-HIGH"},
    {"name": "Ada", "category": "Customer Support AI", "valuation": "$1.2B", "priority": "HIGH"},
    {"name": "Kore.ai", "category": "Customer Support AI", "valuation": "~$1B", "priority": "MEDIUM-HIGH"},
    {"name": "Forethought", "category": "Customer Support AI", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Observe.AI", "category": "Customer Support AI", "valuation": "~$800M", "priority": "MEDIUM-HIGH"},
    {"name": "Freshworks", "category": "Customer Support AI", "valuation": "~$5B", "priority": "MEDIUM"},
    {"name": "Dialpad", "category": "Customer Support AI", "valuation": "$2.2B", "priority": "MEDIUM"},
    {"name": "Assembled", "category": "Customer Support AI", "valuation": "~$300M", "priority": "MEDIUM-HIGH"},
    {"name": "Boost.ai", "category": "Customer Support AI", "valuation": "N/A", "priority": "MEDIUM-HIGH"},
    {"name": "Mavenoid", "category": "Customer Support AI", "valuation": "~$150M", "priority": "MEDIUM-HIGH"},
    
    # Category 6: Knowledge Management
    {"name": "Guru", "category": "Knowledge Management", "valuation": "~$300M", "priority": "HIGH"},
    {"name": "Notion", "category": "Knowledge Management", "valuation": "$10B+", "priority": "MEDIUM"},
    {"name": "Tettra", "category": "Knowledge Management", "valuation": "~$10M", "priority": "HIGH"},
    {"name": "Slab", "category": "Knowledge Management", "valuation": "~$50M", "priority": "HIGH"},
    {"name": "Nuclino", "category": "Knowledge Management", "valuation": "~$5M", "priority": "MEDIUM"},
    {"name": "Trainual", "category": "Knowledge Management", "valuation": "~$50M", "priority": "MEDIUM"},
    {"name": "Helpjuice", "category": "Knowledge Management", "valuation": "N/A", "priority": "HIGH"},
    {"name": "Document360", "category": "Knowledge Management", "valuation": "~$50M", "priority": "MEDIUM-HIGH"},
    {"name": "Bloomfire", "category": "Knowledge Management", "valuation": "~$50M", "priority": "HIGH"},
    {"name": "Stonly", "category": "Knowledge Management", "valuation": "~$30M", "priority": "HIGH"},
    {"name": "Shelf.io", "category": "Knowledge Management", "valuation": "~$30M", "priority": "MEDIUM-HIGH"},
    {"name": "Spekit", "category": "Knowledge Management", "valuation": "~$50M", "priority": "MEDIUM"},
    
    # Category 7: Enterprise Search
    {"name": "Glean", "category": "Enterprise Search", "valuation": "$7.2B", "priority": "LOW"},
    {"name": "Coveo", "category": "Enterprise Search", "valuation": "~$1B", "priority": "MEDIUM"},
    {"name": "Elastic", "category": "Enterprise Search", "valuation": "~$10B", "priority": "MEDIUM"},
    {"name": "Algolia", "category": "Enterprise Search", "valuation": "~$2B", "priority": "MEDIUM"},
    {"name": "Lucidworks", "category": "Enterprise Search", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Pryon", "category": "Enterprise Search", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Hebbia", "category": "Enterprise Search", "valuation": "$700M", "priority": "LOW"},
    
    # Category 8: Financial Research and Analysis
    {"name": "AlphaSense", "category": "Financial Research", "valuation": "$4B", "priority": "HIGH"},
    {"name": "Daloopa", "category": "Financial Research", "valuation": "~$100M", "priority": "HIGH"},
    {"name": "Reflexivity", "category": "Financial Research", "valuation": "~$200M", "priority": "HIGH"},
    {"name": "Toggle AI", "category": "Financial Research", "valuation": "~$200M", "priority": "HIGH"},
    {"name": "YipitData", "category": "Financial Research", "valuation": "$1B+", "priority": "HIGH"},
    {"name": "TipRanks", "category": "Financial Research", "valuation": "$200M", "priority": "MEDIUM"},
    {"name": "AlphaSights", "category": "Financial Research", "valuation": "$4.2B", "priority": "MEDIUM"},
    {"name": "Koyfin", "category": "Financial Research", "valuation": "~$50M", "priority": "MEDIUM"},
    {"name": "Seeking Alpha", "category": "Financial Research", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Simply Wall St", "category": "Financial Research", "valuation": "~$30M", "priority": "MEDIUM"},
    {"name": "YCharts", "category": "Financial Research", "valuation": "~$150M", "priority": "MEDIUM"},
    
    # Category 9: Healthcare and Clinical AI
    {"name": "Hippocratic AI", "category": "Healthcare AI", "valuation": "$3.5B", "priority": "HIGH"},
    {"name": "Abridge", "category": "Healthcare AI", "valuation": "$5.3B", "priority": "HIGH"},
    {"name": "Ambience Healthcare", "category": "Healthcare AI", "valuation": "$1.25B", "priority": "HIGH"},
    {"name": "Nabla", "category": "Healthcare AI", "valuation": "~$300M", "priority": "MEDIUM-HIGH"},
    {"name": "Suki AI", "category": "Healthcare AI", "valuation": "~$500M", "priority": "MEDIUM-HIGH"},
    {"name": "Cohere Health", "category": "Healthcare AI", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Viz.ai", "category": "Healthcare AI", "valuation": "$1.2B", "priority": "HIGH"},
    {"name": "PathAI", "category": "Healthcare AI", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Paige AI", "category": "Healthcare AI", "valuation": "~$400M", "priority": "HIGH"},
    {"name": "Tempus AI", "category": "Healthcare AI", "valuation": "$6B+", "priority": "HIGH"},
    {"name": "Regard", "category": "Healthcare AI", "valuation": "~$150M", "priority": "HIGH"},
    {"name": "Notable Health", "category": "Healthcare AI", "valuation": "~$300M", "priority": "MEDIUM-LOW"},
    
    # Category 10: Research and Academic Tools
    {"name": "Elicit", "category": "Research Tools", "valuation": "$100M", "priority": "HIGH"},
    {"name": "Semantic Scholar", "category": "Research Tools", "valuation": "N/A", "priority": "HIGH"},
    {"name": "Consensus", "category": "Research Tools", "valuation": "~$20M", "priority": "MEDIUM-HIGH"},
    {"name": "Scite", "category": "Research Tools", "valuation": "N/A", "priority": "HIGH"},
    {"name": "Iris.ai", "category": "Research Tools", "valuation": "~$30M", "priority": "HIGH"},
    {"name": "ResearchRabbit", "category": "Research Tools", "valuation": "~$5M", "priority": "MEDIUM"},
    {"name": "Connected Papers", "category": "Research Tools", "valuation": "~$5M", "priority": "MEDIUM"},
    {"name": "Litmaps", "category": "Research Tools", "valuation": "~$10M", "priority": "MEDIUM"},
    {"name": "Scholarcy", "category": "Research Tools", "valuation": "~$3M", "priority": "LOW-MEDIUM"},
    
    # Category 11: AI Agents and Automation Platforms
    {"name": "n8n", "category": "AI Agents", "valuation": "$2.5B", "priority": "HIGH"},
    {"name": "Lindy.ai", "category": "AI Agents", "valuation": "~$200M", "priority": "HIGH"},
    {"name": "Zapier", "category": "AI Agents", "valuation": "$5B+", "priority": "HIGH"},
    {"name": "Relevance AI", "category": "AI Agents", "valuation": "~$150M", "priority": "HIGH"},
    {"name": "Qualified", "category": "AI Agents", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Bardeen", "category": "AI Agents", "valuation": "~$100M", "priority": "MEDIUM-HIGH"},
    {"name": "Conversica", "category": "AI Agents", "valuation": "~$300M", "priority": "MEDIUM"},
    {"name": "Induced.ai", "category": "AI Agents", "valuation": "~$20M", "priority": "MEDIUM"},
    {"name": "MultiOn", "category": "AI Agents", "valuation": "~$50M", "priority": "MEDIUM"},
    {"name": "Browse AI", "category": "AI Agents", "valuation": "~$20M", "priority": "MEDIUM"},
    {"name": "Workato", "category": "AI Agents", "valuation": "$5.7B", "priority": "MEDIUM"},
    {"name": "Kustomer", "category": "AI Agents", "valuation": "$250M", "priority": "MEDIUM-LOW"},
    {"name": "Activepieces", "category": "AI Agents", "valuation": "N/A", "priority": "LOW"},
    
    # Category 12: Content and Marketing AI
    {"name": "Writer", "category": "Content AI", "valuation": "$1.9B", "priority": "HIGH"},
    {"name": "Copy.ai", "category": "Content AI", "valuation": "~$100M", "priority": "MEDIUM"},
    {"name": "Jasper", "category": "Content AI", "valuation": "~$1.2B", "priority": "MEDIUM"},
    {"name": "Anyword", "category": "Content AI", "valuation": "~$100M", "priority": "MEDIUM"},
    {"name": "Surfer SEO", "category": "Content AI", "valuation": "~$50M", "priority": "MEDIUM"},
    {"name": "Clearscope", "category": "Content AI", "valuation": "~$30M", "priority": "MEDIUM"},
    {"name": "MarketMuse", "category": "Content AI", "valuation": "~$30M", "priority": "MEDIUM"},
    {"name": "Frase", "category": "Content AI", "valuation": "~$20M", "priority": "MEDIUM"},
    {"name": "Writesonic", "category": "Content AI", "valuation": "~$30M", "priority": "LOW-MEDIUM"},
    {"name": "Rytr", "category": "Content AI", "valuation": "~$5M", "priority": "LOW"},
    {"name": "Grammarly", "category": "Content AI", "valuation": "$13B", "priority": "MEDIUM"},
    {"name": "AI21 Labs", "category": "Content AI", "valuation": "$1.4B", "priority": "MEDIUM"},
    
    # Category 13: Procurement and Spend Management
    {"name": "Zip", "category": "Procurement", "valuation": "$2.2B", "priority": "HIGH"},
    {"name": "Ramp", "category": "Procurement", "valuation": "$22.5B", "priority": "HIGH"},
    {"name": "Brex", "category": "Procurement", "valuation": "~$10B", "priority": "MEDIUM"},
    {"name": "Coupa", "category": "Procurement", "valuation": "PE-owned", "priority": "MEDIUM"},
    {"name": "Jaggaer", "category": "Procurement", "valuation": "~$500M", "priority": "MEDIUM"},
    
    # Category 14: Real Estate Tech with AI
    {"name": "Placer.ai", "category": "Real Estate Tech", "valuation": "$1.5B", "priority": "HIGH"},
    {"name": "Cherre", "category": "Real Estate Tech", "valuation": "~$200M", "priority": "HIGH"},
    {"name": "Crexi", "category": "Real Estate Tech", "valuation": "~$300M", "priority": "MEDIUM-HIGH"},
    {"name": "CoStar", "category": "Real Estate Tech", "valuation": "~$30B", "priority": "LOW"},
    
    # Category 15: Recruiting and HR Tech with AI
    {"name": "Eightfold AI", "category": "HR Tech", "valuation": "~$2B", "priority": "HIGH"},
    {"name": "Paradox", "category": "HR Tech", "valuation": "$1.5B", "priority": "HIGH"},
    {"name": "Beamery", "category": "HR Tech", "valuation": "~$800M", "priority": "MEDIUM-HIGH"},
    {"name": "Phenom", "category": "HR Tech", "valuation": "~$1B", "priority": "MEDIUM"},
    {"name": "Findem", "category": "HR Tech", "valuation": "~$150M", "priority": "MEDIUM-HIGH"},
    {"name": "hireEZ", "category": "HR Tech", "valuation": "~$100M", "priority": "MEDIUM"},
    {"name": "Gem", "category": "HR Tech", "valuation": "~$300M", "priority": "MEDIUM"},
    {"name": "Greenhouse", "category": "HR Tech", "valuation": "~$500M", "priority": "MEDIUM"},
    {"name": "Lever", "category": "HR Tech", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Ashby", "category": "HR Tech", "valuation": "~$100M", "priority": "MEDIUM"},
    {"name": "HireVue", "category": "HR Tech", "valuation": "~$500M", "priority": "MEDIUM"},
]


class LinkedInSalesNavAutomation:
    """Automates adding companies to LinkedIn Sales Navigator"""
    
    def __init__(self, headless: bool = False, profile_name: str = "default"):
        self.headless = headless
        self.profile_name = profile_name
        self.browser = None
        self.context = None
        self.page = None
        self.companies: List[Company] = []
        self.results_file = Path("linkedin_automation_results.json")
        self.state_file = Path("linkedin_automation_state.json")
        
    def load_companies(self, filter_priority: Optional[List[str]] = None) -> List[Company]:
        """Load companies from data, optionally filtering by priority"""
        companies = []
        for data in COMPANIES_DATA:
            if filter_priority and data.get("priority") not in filter_priority:
                continue
            companies.append(Company(
                name=data["name"],
                category=data["category"],
                valuation=data.get("valuation", ""),
                priority=data.get("priority", "MEDIUM")
            ))
        self.companies = companies
        logger.info(f"Loaded {len(companies)} companies")
        return companies
    
    def load_state(self) -> Dict:
        """Load previous automation state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"processed": [], "last_index": 0}
    
    def save_state(self, state: Dict):
        """Save automation state for resume capability"""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def save_results(self):
        """Save results to JSON file"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_companies": len(self.companies),
            "companies": [asdict(c) for c in self.companies]
        }
        with open(self.results_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {self.results_file}")
    
    async def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Add random human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    async def setup_browser(self, profile_name: str = "default"):
        """Initialize Playwright browser with specified profile"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
            raise
        
        self.playwright = await async_playwright().start()
        
        # Use persistent context to maintain login state - with custom profile name
        user_data_dir = Path.home() / f".linkedin_automation_profile_{profile_name}"
        user_data_dir.mkdir(exist_ok=True)
        
        logger.info(f"Using browser profile: {profile_name} at {user_data_dir}")
        
        self.browser = await self.playwright.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.page = self.browser.pages[0] if self.browser.pages else await self.browser.new_page()
        logger.info("Browser initialized")
    
    async def check_login_status(self) -> bool:
        """Check if user is logged into LinkedIn"""
        await self.page.goto("https://www.linkedin.com/sales/home")
        await self.random_delay(2, 4)
        
        # Check if we're on the login page or Sales Navigator home
        current_url = self.page.url
        if "login" in current_url or "checkpoint" in current_url:
            return False
        
        # Check for Sales Navigator specific elements
        try:
            await self.page.wait_for_selector('[data-test-global-nav]', timeout=5000)
            return True
        except:
            return False
    
    async def wait_for_manual_login(self):
        """Wait for user to manually log in"""
        logger.info("=" * 60)
        logger.info("MANUAL LOGIN REQUIRED")
        logger.info("=" * 60)
        logger.info("Please log in to LinkedIn Sales Navigator in the browser window.")
        logger.info("The script will continue automatically once you're logged in.")
        logger.info("=" * 60)
        
        while True:
            if await self.check_login_status():
                logger.info("Login detected! Continuing with automation...")
                break
            await asyncio.sleep(3)
    
    async def search_company(self, company_name: str) -> Optional[str]:
        """Search for a company in Sales Navigator and return its URL"""
        search_url = f"https://www.linkedin.com/sales/search/company?query=(filters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList()%2CselectedSubFilter%3A())%2C(type%3AREGION%2Cvalues%3AList()%2CselectedSubFilter%3A())%2C(type%3AINDUSTRY%2Cvalues%3AList()%2CselectedSubFilter%3A()))%2Ckeywords%3A{company_name.replace(' ', '%20')})"
        
        await self.page.goto(search_url)
        await self.random_delay(2, 4)
        
        try:
            # Wait for search results
            await self.page.wait_for_selector('[data-view-name="search-results-container"]', timeout=10000)
            await self.random_delay(1, 2)
            
            # Find the first company result
            company_links = await self.page.query_selector_all('a[data-control-name="view_company_via_search"]')
            
            if company_links:
                href = await company_links[0].get_attribute('href')
                return f"https://www.linkedin.com{href}" if href else None
            
            # Alternative selector
            results = await self.page.query_selector_all('.search-results__result-item')
            if results:
                link = await results[0].query_selector('a')
                if link:
                    href = await link.get_attribute('href')
                    return f"https://www.linkedin.com{href}" if href and '/sales/company/' in href else None
            
            return None
            
        except Exception as e:
            logger.warning(f"Error searching for {company_name}: {e}")
            return None
    
    async def save_company_to_list(self, company_url: str) -> bool:
        """Save a company to your Sales Navigator saved accounts"""
        try:
            await self.page.goto(company_url)
            await self.random_delay(2, 4)
            
            # Look for the "Save" button
            save_button = await self.page.query_selector('[data-control-name="save"]')
            if not save_button:
                save_button = await self.page.query_selector('button:has-text("Save")')
            
            if not save_button:
                # Try alternative selectors
                save_button = await self.page.query_selector('[aria-label*="Save"]')
            
            if save_button:
                # Check if already saved
                button_text = await save_button.inner_text()
                if "Saved" in button_text:
                    logger.info("Company already saved")
                    return True
                
                await save_button.click()
                await self.random_delay(1, 2)
                logger.info("Company saved successfully")
                return True
            else:
                logger.warning("Save button not found")
                return False
                
        except Exception as e:
            logger.error(f"Error saving company: {e}")
            return False
    
    async def process_company(self, company: Company) -> Company:
        """Process a single company: search and save"""
        logger.info(f"Processing: {company.name} ({company.category})")
        
        try:
            # Search for the company
            company_url = await self.search_company(company.name)
            
            if company_url:
                company.linkedin_url = company_url
                company.status = "found"
                logger.info(f"Found: {company_url}")
                
                # Save the company
                if await self.save_company_to_list(company_url):
                    company.status = "saved"
                else:
                    company.status = "found"
                    company.error_message = "Could not save to list"
            else:
                company.status = "not_found"
                logger.warning(f"Company not found: {company.name}")
            
        except Exception as e:
            company.status = "error"
            company.error_message = str(e)
            logger.error(f"Error processing {company.name}: {e}")
        
        return company
    
    async def run(self, 
                  filter_priority: Optional[List[str]] = None,
                  limit: Optional[int] = None,
                  resume: bool = True):
        """Run the automation"""
        
        # Load companies
        self.load_companies(filter_priority)
        
        if limit:
            self.companies = self.companies[:limit]
        
        # Load previous state if resuming
        state = self.load_state() if resume else {"processed": [], "last_index": 0}
        
        try:
            await self.setup_browser(self.profile_name)
            
            # Check login and wait if needed
            if not await self.check_login_status():
                await self.wait_for_manual_login()
            
            # Process each company
            for i, company in enumerate(self.companies):
                if company.name in state["processed"]:
                    logger.info(f"Skipping already processed: {company.name}")
                    continue
                
                await self.process_company(company)
                
                # Update state
                state["processed"].append(company.name)
                state["last_index"] = i
                self.save_state(state)
                
                # Save results periodically
                if (i + 1) % 5 == 0:
                    self.save_results()
                
                # Random delay between companies
                await self.random_delay(3, 7)
            
            # Final save
            self.save_results()
            
            # Print summary
            self.print_summary()
            
        finally:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
    
    def print_summary(self):
        """Print processing summary"""
        saved = sum(1 for c in self.companies if c.status == "saved")
        found = sum(1 for c in self.companies if c.status == "found")
        not_found = sum(1 for c in self.companies if c.status == "not_found")
        errors = sum(1 for c in self.companies if c.status == "error")
        
        logger.info("=" * 60)
        logger.info("AUTOMATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total companies processed: {len(self.companies)}")
        logger.info(f"Successfully saved: {saved}")
        logger.info(f"Found but not saved: {found}")
        logger.info(f"Not found: {not_found}")
        logger.info(f"Errors: {errors}")
        logger.info("=" * 60)
        
        if not_found > 0:
            logger.info("\nCompanies not found:")
            for c in self.companies:
                if c.status == "not_found":
                    logger.info(f"  - {c.name}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Sales Navigator Company Automation")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (not recommended for login)")
    parser.add_argument("--limit", type=int, help="Limit number of companies to process")
    parser.add_argument("--priority", nargs="+", choices=["HIGH", "MEDIUM-HIGH", "MEDIUM", "MEDIUM-LOW", "LOW"], 
                        help="Filter by priority levels")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh, don't resume from previous state")
    parser.add_argument("--profile", type=str, default="default", help="Browser profile name (use different names for different accounts)")
    parser.add_argument("--list-companies", action="store_true", help="List all companies and exit")
    
    args = parser.parse_args()
    
    if args.list_companies:
        print("\n" + "=" * 80)
        print("COMPANIES TO ADD TO LINKEDIN SALES NAVIGATOR")
        print("=" * 80)
        
        # Group by category
        categories = {}
        for data in COMPANIES_DATA:
            cat = data["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(data)
        
        for cat, companies in categories.items():
            print(f"\n{cat} ({len(companies)} companies):")
            for c in companies:
                print(f"  - {c['name']} [{c.get('priority', 'N/A')}] {c.get('valuation', '')}")
        
        print(f"\n{'=' * 80}")
        print(f"TOTAL: {len(COMPANIES_DATA)} companies")
        print("=" * 80)
        return
    
    automation = LinkedInSalesNavAutomation(headless=args.headless, profile_name=args.profile)
    await automation.run(
        filter_priority=args.priority,
        limit=args.limit,
        resume=not args.no_resume
    )


if __name__ == "__main__":
    asyncio.run(main())

