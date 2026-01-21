#!/usr/bin/env python3
"""
Google Sheets Events Calendar Sync for Chroma GTM

Syncs the 2026 Events Calendar to a Google Sheet with multiple tabs:
- Events Calendar (main list)
- Summary (budget & metrics)
- By Cohort (events grouped by target cohort)
- Action Items (CFP deadlines, registrations)

Usage:
    python google_sheets_events_sync.py                    # Full sync
    python google_sheets_events_sync.py --sheet-id XXX     # Specify sheet ID
    python google_sheets_events_sync.py --dry-run          # Preview without pushing
    python google_sheets_events_sync.py --list             # List current sheet stats

Setup:
    1. Follow credentials/README.md to set up Google Cloud
    2. Add GOOGLE_SHEET_ID to your .env file (or use --sheet-id)
    3. Run: pip install gspread google-auth gspread-formatting
"""

import os
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from gspread_formatting import (
        DataValidationRule, 
        BooleanCondition, 
        set_data_validation_for_cell_range
    )
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install gspread google-auth gspread-formatting")
    exit(1)

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = os.getenv(
    "GOOGLE_SHEETS_CREDENTIALS_FILE",
    str(BASE_DIR / "credentials" / "google_service_account.json")
)

# Default to the events sheet ID, or fall back to main GTM sheet
EVENTS_SHEET_ID = os.getenv("EVENTS_GOOGLE_SHEET_ID") or os.getenv("GOOGLE_SHEET_ID")

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Tab names
TAB_NAMES = {
    "calendar": "Events Calendar 2026",
    "summary": "Summary",
    "by_quarter": "By Quarter",
    "by_cohort": "By Cohort",
    "action_items": "Action Items",
    "critical": "Critical Events"
}

# Status options for event tracking
STATUS_OPTIONS = [
    "Planning",
    "Registered",
    "CFP Submitted",
    "Booth Booked",
    "Confirmed",
    "Attended",
    "Cancelled"
]

# Priority colors
PRIORITY_COLORS = {
    "CRITICAL": {"red": 0.8, "green": 0.2, "blue": 0.2},      # Red
    "High": {"red": 0.95, "green": 0.6, "blue": 0.2},         # Orange
    "Medium": {"red": 0.95, "green": 0.85, "blue": 0.4},      # Yellow
    "Strategic": {"red": 0.4, "green": 0.7, "blue": 0.4},     # Green
}

# =============================================================================
# EVENTS DATA
# =============================================================================

EVENTS_DATA = [
    # Q1 Events
    {"name": "CES 2026", "start": "2026-01-06", "end": "2026-01-09", "location": "Las Vegas, NV", "cohorts": "2, 4", "priority": "Strategic", "cost_low": 15000, "cost_high": 30000, "category": "Consumer Tech", "quarter": "Q1", "action": "Attend", "cfp_deadline": "N/A", "website": "https://www.ces.tech/", "notes": "Consumer AI focus; good for brand visibility"},
    {"name": "Generative AI Expo", "start": "2026-02-10", "end": "2026-02-12", "location": "Fort Lauderdale, FL", "cohorts": "1, 2", "priority": "Medium", "cost_low": 8000, "cost_high": 15000, "category": "AI/ML", "quarter": "Q1", "action": "Booth", "cfp_deadline": "Dec 2025", "website": "https://www.techsummit.com/", "notes": "GenAI applications for business"},
    {"name": "Cisco Live Europe", "start": "2026-02-09", "end": "2026-02-13", "location": "Amsterdam, Netherlands", "cohorts": "3, 4", "priority": "Medium", "cost_low": 10000, "cost_high": 20000, "category": "Enterprise", "quarter": "Q1", "action": "Attend", "cfp_deadline": "Jan 2026", "website": "https://www.ciscolive.com/", "notes": "Enterprise infrastructure; AI era focus"},
    {"name": "AI DevWorld 2026", "start": "2026-02-18", "end": "2026-02-20", "location": "San Jose, CA", "cohorts": "1, 2", "priority": "High", "cost_low": 15000, "cost_high": 25000, "category": "AI Developer", "quarter": "Q1", "action": "Booth + Speaking", "cfp_deadline": "Dec 2025", "website": "https://www.developerweek.com/", "notes": "Largest AI/ML developer conference"},
    {"name": "Mobile World Congress", "start": "2026-02-23", "end": "2026-02-26", "location": "Barcelona, Spain", "cohorts": "2, 4", "priority": "Strategic", "cost_low": 25000, "cost_high": 50000, "category": "Mobile/IoT", "quarter": "Q1", "action": "Selective", "cfp_deadline": "Dec 2025", "website": "https://www.mwcbarcelona.com/", "notes": "5G/6G; edge computing; IoT"},
    {"name": "NVIDIA GTC 2026", "start": "2026-03-16", "end": "2026-03-19", "location": "San Jose, CA", "cohorts": "1, 2, 3", "priority": "CRITICAL", "cost_low": 25000, "cost_high": 50000, "category": "AI Infrastructure", "quarter": "Q1", "action": "Booth + Speaking", "cfp_deadline": "Dec 2025", "website": "https://www.nvidia.com/gtc/", "notes": "Premier AI infrastructure conference - MUST ATTEND"},
    {"name": "RSA Conference 2026", "start": "2026-03-23", "end": "2026-03-26", "location": "San Francisco, CA", "cohorts": "3, 4", "priority": "High", "cost_low": 20000, "cost_high": 40000, "category": "Security", "quarter": "Q1", "action": "Booth", "cfp_deadline": "Jan 2026", "website": "https://www.rsaconference.com/", "notes": "Security + AI; enterprise decision makers"},
    
    # Q2 Events
    {"name": "Google Cloud Next 2026", "start": "2026-04-22", "end": "2026-04-24", "location": "Las Vegas, NV", "cohorts": "2, 3, 4", "priority": "High", "cost_low": 20000, "cost_high": 40000, "category": "Cloud", "quarter": "Q2", "action": "Booth", "cfp_deadline": "Feb 2026", "website": "https://cloud.withgoogle.com/next", "notes": "Cloud AI; Vertex AI; enterprise"},
    {"name": "SaaStock USA 2026", "start": "2026-04-15", "end": "2026-04-16", "location": "Austin, TX", "cohorts": "2, 4", "priority": "Medium", "cost_low": 10000, "cost_high": 20000, "category": "SaaS", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Feb 2026", "website": "https://www.saastock.com/", "notes": "SaaS founders and executives"},
    {"name": "Digital Velocity (Tealium)", "start": "2026-04-27", "end": "2026-04-29", "location": "New York, NY", "cohorts": "2, 4", "priority": "Medium", "cost_low": 8000, "cost_high": 15000, "category": "Data/MarTech", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Mar 2026", "website": "https://tealium.com/", "notes": "Customer data; real-time AI"},
    {"name": "SaaStr Annual 2026", "start": "2026-05-12", "end": "2026-05-14", "location": "San Mateo, CA", "cohorts": "2, 4", "priority": "High", "cost_low": 15000, "cost_high": 30000, "category": "SaaS", "quarter": "Q2", "action": "Booth + Speaking", "cfp_deadline": "Mar 2026", "website": "https://www.saastrannual.com/", "notes": "World's largest SaaS conference + AI Summit"},
    {"name": "AI and Big Data Expo NA", "start": "2026-05-18", "end": "2026-05-19", "location": "San Jose, CA", "cohorts": "2, 3, 4", "priority": "High", "cost_low": 15000, "cost_high": 25000, "category": "AI/ML", "quarter": "Q2", "action": "Booth", "cfp_deadline": "Mar 2026", "website": "https://www.ai-expo.net/", "notes": "AI/ML; enterprise data strategies"},
    {"name": "Dell Technologies World", "start": "2026-05-18", "end": "2026-05-21", "location": "Las Vegas, NV", "cohorts": "4", "priority": "Medium", "cost_low": 15000, "cost_high": 25000, "category": "Enterprise", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Apr 2026", "website": "https://www.delltechnologiesworld.com/", "notes": "Enterprise tech; AI decision-making"},
    {"name": "Computex 2026", "start": "2026-06-02", "end": "2026-06-06", "location": "Taipei, Taiwan", "cohorts": "2", "priority": "Strategic", "cost_low": 20000, "cost_high": 35000, "category": "Tech/Hardware", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Apr 2026", "website": "https://www.computextaipei.com.tw/", "notes": "AI hardware; next-gen tech"},
    {"name": "FinOps X 2026", "start": "2026-06-08", "end": "2026-06-11", "location": "San Diego, CA", "cohorts": "2, 4", "priority": "Medium", "cost_low": 10000, "cost_high": 15000, "category": "FinOps", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Apr 2026", "website": "https://x.finops.org/", "notes": "Cloud cost management; FinOps"},
    {"name": "Gartner Marketing Symposium", "start": "2026-06-08", "end": "2026-06-10", "location": "Denver, CO", "cohorts": "4", "priority": "Medium", "cost_low": 10000, "cost_high": 20000, "category": "Marketing", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Apr 2026", "website": "https://www.gartner.com/", "notes": "CMOs; marketing analytics; AI"},
    {"name": "SuperAI 2026", "start": "2026-06-10", "end": "2026-06-11", "location": "Singapore", "cohorts": "2, 4", "priority": "Medium", "cost_low": 15000, "cost_high": 25000, "category": "AI", "quarter": "Q2", "action": "Attend", "cfp_deadline": "Apr 2026", "website": "https://superai.com/", "notes": "Asia AI conference; C-level executives"},
    {"name": "Snowflake Summit 2026", "start": "2026-06-01", "end": "2026-06-04", "location": "San Francisco, CA", "cohorts": "2, 3", "priority": "High", "cost_low": 20000, "cost_high": 35000, "category": "Data/AI", "quarter": "Q2", "action": "Booth", "cfp_deadline": "Apr 2026", "website": "https://www.snowflake.com/summit/", "notes": "Major data conference; competitor customers"},
    {"name": "Data + AI Summit (Databricks)", "start": "2026-06-15", "end": "2026-06-18", "location": "San Francisco, CA", "cohorts": "2, 3", "priority": "High", "cost_low": 20000, "cost_high": 35000, "category": "Data/AI", "quarter": "Q2", "action": "Booth", "cfp_deadline": "Apr 2026", "website": "https://www.databricks.com/dataaisummit", "notes": "Competitor customers; data teams - KEY DATA EVENT"},
    {"name": "AI Engineer World's Fair", "start": "2026-06-30", "end": "2026-07-02", "location": "San Francisco, CA", "cohorts": "1, 2, 3", "priority": "CRITICAL", "cost_low": 30000, "cost_high": 60000, "category": "AI Developer", "quarter": "Q2/Q3", "action": "Booth + Speaking + Sponsor", "cfp_deadline": "Mar 2026", "website": "https://www.ai.engineer/worldsfair", "notes": "Largest technical AI conference - FLAGSHIP EVENT"},
    
    # Q3 Events
    {"name": "Ai4 2026", "start": "2026-08-04", "end": "2026-08-06", "location": "Las Vegas, NV", "cohorts": "2, 4", "priority": "High", "cost_low": 20000, "cost_high": 35000, "category": "Enterprise AI", "quarter": "Q3", "action": "Booth", "cfp_deadline": "May 2026", "website": "https://ai4.io/", "notes": "America's largest AI conference"},
    {"name": "AI Infra Summit 2026", "start": "2026-09-15", "end": "2026-09-17", "location": "Santa Clara, CA", "cohorts": "1, 2, 3", "priority": "CRITICAL", "cost_low": 25000, "cost_high": 45000, "category": "AI Infrastructure", "quarter": "Q3", "action": "Booth + Speaking", "cfp_deadline": "Jun 2026", "website": "https://ai-infra-summit.com/", "notes": "Perfect fit - infrastructure focus"},
    {"name": "Salesforce Dreamforce", "start": "2026-09-15", "end": "2026-09-17", "location": "San Francisco, CA", "cohorts": "4", "priority": "Medium", "cost_low": 15000, "cost_high": 30000, "category": "Enterprise/CRM", "quarter": "Q3", "action": "Attend", "cfp_deadline": "Jul 2026", "website": "https://www.salesforce.com/dreamforce/", "notes": "SI partners; enterprise sales"},
    {"name": "TechCrunch Disrupt", "start": "2026-10-13", "end": "2026-10-15", "location": "San Francisco, CA", "cohorts": "2", "priority": "Medium", "cost_low": 15000, "cost_high": 25000, "category": "Startups", "quarter": "Q4", "action": "Booth", "cfp_deadline": "Jul 2026", "website": "https://techcrunch.com/events/disrupt/", "notes": "Startups; AI-native companies"},
    {"name": "The AI Conference SF", "start": "2026-09-30", "end": "2026-10-01", "location": "San Francisco, CA", "cohorts": "1, 2", "priority": "High", "cost_low": 15000, "cost_high": 25000, "category": "AI", "quarter": "Q3", "action": "Booth + Speaking", "cfp_deadline": "Jul 2026", "website": "https://theaiconference.com/", "notes": "Applied AI startups; neural architectures"},
    
    # Q4 Events
    {"name": "World Summit AI Amsterdam", "start": "2026-10-07", "end": "2026-10-08", "location": "Amsterdam, Netherlands", "cohorts": "2, 4", "priority": "Medium", "cost_low": 15000, "cost_high": 25000, "category": "AI", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Aug 2026", "website": "https://worldsummit.ai/", "notes": "Global AI summit; European market"},
    {"name": "ARRtist Summit 2026", "start": "2026-10-08", "end": "2026-10-08", "location": "Berlin, Germany", "cohorts": "2, 4", "priority": "Medium", "cost_low": 8000, "cost_high": 15000, "category": "SaaS", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Aug 2026", "website": "https://www.arrtist-summit.com/", "notes": "European SaaS community"},
    {"name": "SaaStock Europe 2026", "start": "2026-10-13", "end": "2026-10-14", "location": "Dublin, Ireland", "cohorts": "2, 4", "priority": "Medium", "cost_low": 12000, "cost_high": 20000, "category": "SaaS", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Aug 2026", "website": "https://www.saastock.com/", "notes": "European SaaS conference"},
    {"name": "Gartner IT Symposium", "start": "2026-10-19", "end": "2026-10-22", "location": "Orlando, FL", "cohorts": "4", "priority": "Strategic", "cost_low": 20000, "cost_high": 35000, "category": "Enterprise", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Aug 2026", "website": "https://www.gartner.com/", "notes": "CIOs; enterprise decision makers"},
    {"name": "ZERO-IN (ChurnZero)", "start": "2026-11-04", "end": "2026-11-06", "location": "Nashville, TN", "cohorts": "1, 4", "priority": "Medium", "cost_low": 5000, "cost_high": 10000, "category": "Customer Success", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Sep 2026", "website": "https://churnzero.com/zero-in/", "notes": "Customer success leaders"},
    {"name": "Web Summit 2026", "start": "2026-11-09", "end": "2026-11-12", "location": "Lisbon, Portugal", "cohorts": "2, 4", "priority": "Medium", "cost_low": 20000, "cost_high": 35000, "category": "Tech", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Sep 2026", "website": "https://websummit.com/", "notes": "Major European tech conference"},
    {"name": "KubeCon NA 2026", "start": "2026-11-09", "end": "2026-11-12", "location": "Salt Lake City, UT", "cohorts": "2, 3", "priority": "High", "cost_low": 20000, "cost_high": 35000, "category": "Cloud Native", "quarter": "Q4", "action": "Booth", "cfp_deadline": "Aug 2026", "website": "https://events.linuxfoundation.org/kubecon-cloudnativecon-north-america/", "notes": "Cloud-native devs; Kubernetes"},
    {"name": "CISO Summit", "start": "2026-11-10", "end": "2026-11-11", "location": "Dallas, TX", "cohorts": "4", "priority": "Strategic", "cost_low": 10000, "cost_high": 20000, "category": "Security", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Sep 2026", "website": "https://cisosummit.com/", "notes": "Security leaders; AI security"},
    {"name": "AI Engineer Code Summit", "start": "2026-11-15", "end": "2026-11-17", "location": "San Francisco, CA", "cohorts": "1, 2", "priority": "High", "cost_low": 15000, "cost_high": 25000, "category": "AI Developer", "quarter": "Q4", "action": "Booth + Speaking", "cfp_deadline": "Aug 2026", "website": "https://www.ai.engineer/", "notes": "Coding agents; AI engineering"},
    {"name": "Microsoft Ignite", "start": "2026-11-16", "end": "2026-11-20", "location": "Seattle, WA", "cohorts": "3, 4", "priority": "Medium", "cost_low": 15000, "cost_high": 30000, "category": "Enterprise/Cloud", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Sep 2026", "website": "https://ignite.microsoft.com/", "notes": "Azure AI; enterprise cloud"},
    {"name": "Slush 2026", "start": "2026-11-18", "end": "2026-11-19", "location": "Helsinki, Finland", "cohorts": "2", "priority": "Medium", "cost_low": 15000, "cost_high": 25000, "category": "Startups", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Sep 2026", "website": "https://www.slush.org/", "notes": "European startups; investors"},
    {"name": "AWS re:Invent 2026", "start": "2026-12-01", "end": "2026-12-05", "location": "Las Vegas, NV", "cohorts": "2, 3, 4", "priority": "CRITICAL", "cost_low": 40000, "cost_high": 75000, "category": "Cloud", "quarter": "Q4", "action": "Booth + Speaking", "cfp_deadline": "Jul 2026", "website": "https://reinvent.awsevents.com/", "notes": "Largest cloud conference"},
    {"name": "NeurIPS 2026", "start": "2026-12-07", "end": "2026-12-12", "location": "Vancouver, Canada", "cohorts": "2", "priority": "Medium", "cost_low": 10000, "cost_high": 20000, "category": "ML Research", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Jun 2026", "website": "https://nips.cc/", "notes": "ML research; academic + industry"},
]

# =============================================================================
# SMALLER DEVELOPER & OPEN SOURCE EVENTS
# =============================================================================

SMALL_DEV_EVENTS = [
    # Q1 - Developer & Open Source Events
    {"name": "FOSDEM 2026", "start": "2026-01-31", "end": "2026-02-01", "location": "Brussels, Belgium", "cohorts": "1, 2", "priority": "High", "cost_low": 3000, "cost_high": 8000, "category": "Open Source", "quarter": "Q1", "action": "Speaking + Booth", "cfp_deadline": "Dec 2025", "website": "https://fosdem.org/", "notes": "FREE event; largest OSS gathering in Europe; devroom for AI/ML"},
    {"name": "Everything Open 2026", "start": "2026-01-20", "end": "2026-01-22", "location": "Canberra, Australia", "cohorts": "2", "priority": "Low", "cost_low": 5000, "cost_high": 10000, "category": "Open Source", "quarter": "Q1", "action": "Attend", "cfp_deadline": "Nov 2025", "website": "https://everythingopen.au/", "notes": "Australia's premier OSS conference"},
    {"name": "SCALE 23x (SCaLE)", "start": "2026-03-05", "end": "2026-03-08", "location": "Pasadena, CA", "cohorts": "1, 2", "priority": "High", "cost_low": 3000, "cost_high": 8000, "category": "Open Source", "quarter": "Q1", "action": "Booth + Speaking", "cfp_deadline": "Dec 2025", "website": "https://www.socallinuxexpo.org/", "notes": "Largest community-run OSS conf in North America"},
    
    # Q2 - Developer & Open Source Events
    {"name": "Open Developers Summit 2026", "start": "2026-04-23", "end": "2026-04-23", "location": "Prague, Czech Republic", "cohorts": "2", "priority": "Medium", "cost_low": 3000, "cost_high": 6000, "category": "Open Source", "quarter": "Q2", "action": "Speaking", "cfp_deadline": "Feb 2026", "website": "https://events.opensuse.org/", "notes": "openSUSE community; AI/data track"},
    {"name": "PyCon US 2026", "start": "2026-05-14", "end": "2026-05-22", "location": "Pittsburgh, PA", "cohorts": "1, 2", "priority": "High", "cost_low": 8000, "cost_high": 15000, "category": "Developer", "quarter": "Q2", "action": "Booth + Speaking", "cfp_deadline": "Jan 2026", "website": "https://us.pycon.org/", "notes": "Largest Python conference; core Chroma audience"},
    {"name": "PG DATA 2026", "start": "2026-06-04", "end": "2026-06-05", "location": "Chicago, IL", "cohorts": "2, 3", "priority": "Medium", "cost_low": 3000, "cost_high": 6000, "category": "Data/Developer", "quarter": "Q2", "action": "Speaking", "cfp_deadline": "Mar 2026", "website": "https://postgresql.org/", "notes": "PostgreSQL community; pgvector users"},
    
    # Q3 - Developer & Open Source Events
    {"name": "EuroPython 2026", "start": "2026-07-13", "end": "2026-07-19", "location": "Prague, Czech Republic", "cohorts": "1, 2", "priority": "High", "cost_low": 8000, "cost_high": 15000, "category": "Developer", "quarter": "Q3", "action": "Booth + Speaking", "cfp_deadline": "Mar 2026", "website": "https://europython.eu/", "notes": "Largest Python conference in Europe"},
    {"name": "WeAreDevelopers World Congress", "start": "2026-07-16", "end": "2026-07-18", "location": "Berlin, Germany", "cohorts": "2", "priority": "Medium", "cost_low": 10000, "cost_high": 20000, "category": "Developer", "quarter": "Q3", "action": "Booth", "cfp_deadline": "Apr 2026", "website": "https://www.wearedevelopers.com/world-congress", "notes": "70K+ developers; major European dev event"},
    {"name": "FrOSCon 2026", "start": "2026-08-22", "end": "2026-08-23", "location": "Sankt Augustin, Germany", "cohorts": "2", "priority": "Low", "cost_low": 2000, "cost_high": 5000, "category": "Open Source", "quarter": "Q3", "action": "Speaking", "cfp_deadline": "Jun 2026", "website": "https://froscon.org/", "notes": "Free OSS conference in Germany"},
    {"name": "Software Freedom Day", "start": "2026-09-19", "end": "2026-09-19", "location": "Worldwide", "cohorts": "1, 2", "priority": "Low", "cost_low": 500, "cost_high": 2000, "category": "Open Source", "quarter": "Q3", "action": "Host Meetup", "cfp_deadline": "N/A", "website": "https://www.softwarefreedomday.org/", "notes": "Global celebration; host local Chroma meetup"},
    {"name": "WeAreDevelopers NA", "start": "2026-09-23", "end": "2026-09-25", "location": "San Jose, CA", "cohorts": "1, 2", "priority": "Medium", "cost_low": 10000, "cost_high": 20000, "category": "Developer", "quarter": "Q3", "action": "Booth", "cfp_deadline": "Jun 2026", "website": "https://www.wearedevelopers.com/world-congress-us", "notes": "North America edition; AI/dev focus"},
    
    # Q4 - Developer & Open Source Events
    {"name": "OpenSSF Community Day EU", "start": "2026-10-06", "end": "2026-10-06", "location": "Prague, Czech Republic", "cohorts": "2", "priority": "Low", "cost_low": 2000, "cost_high": 5000, "category": "Open Source/Security", "quarter": "Q4", "action": "Attend", "cfp_deadline": "Aug 2026", "website": "https://openssf.org/", "notes": "Open source security; co-located with OSS Summit EU"},
    {"name": "Open Source Summit EU 2026", "start": "2026-10-07", "end": "2026-10-09", "location": "Prague, Czech Republic", "cohorts": "1, 2", "priority": "High", "cost_low": 8000, "cost_high": 15000, "category": "Open Source", "quarter": "Q4", "action": "Booth + Speaking", "cfp_deadline": "Jul 2026", "website": "https://events.linuxfoundation.org/", "notes": "Linux Foundation flagship EU event"},
    {"name": "All Things Open 2026", "start": "2026-10-18", "end": "2026-10-20", "location": "Raleigh, NC", "cohorts": "1, 2", "priority": "High", "cost_low": 5000, "cost_high": 12000, "category": "Open Source", "quarter": "Q4", "action": "Booth + Speaking", "cfp_deadline": "Jul 2026", "website": "https://allthingsopen.org/", "notes": "150+ sessions; strong OSS community; affordable"},
    {"name": "PyData Global 2026", "start": "2026-12-01", "end": "2026-12-03", "location": "Virtual + Cities", "cohorts": "1, 2", "priority": "Medium", "cost_low": 3000, "cost_high": 8000, "category": "Data/Developer", "quarter": "Q4", "action": "Speaking", "cfp_deadline": "Sep 2026", "website": "https://pydata.org/", "notes": "Data science Python community; virtual + local"},
]

# Combine all events
EVENTS_DATA = EVENTS_DATA + SMALL_DEV_EVENTS


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def column_letter(col_index: int) -> str:
    """Convert column index (0-based) to letter (A, B, C, ...)."""
    result = ""
    while col_index >= 0:
        result = chr(col_index % 26 + ord('A')) + result
        col_index = col_index // 26 - 1
    return result


def get_sheets_client() -> gspread.Client:
    """Authenticate and return a Google Sheets client."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Credentials file not found: {CREDENTIALS_FILE}\n"
            "Please follow the setup instructions in credentials/README.md"
        )
    
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(credentials)


def get_or_create_worksheet(
    spreadsheet: gspread.Spreadsheet,
    tab_name: str,
    num_cols: int = 20
) -> gspread.Worksheet:
    """Get an existing worksheet or create a new one."""
    try:
        worksheet = spreadsheet.worksheet(tab_name)
        print(f"  Found existing tab: {tab_name}")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=tab_name,
            rows=100,
            cols=num_cols
        )
        print(f"  Created new tab: {tab_name}")
    
    return worksheet


# =============================================================================
# SYNC FUNCTIONS
# =============================================================================

def sync_events_calendar(
    spreadsheet: gspread.Spreadsheet,
    dry_run: bool = False
) -> int:
    """Sync the main events calendar tab."""
    tab_name = TAB_NAMES["calendar"]
    
    headers = [
        "Event Name", "Start Date", "End Date", "Location", "Target Cohorts",
        "Priority", "Est. Cost Low ($)", "Est. Cost High ($)", "Category",
        "Quarter", "Action Required", "CFP Deadline", "Website", "Notes", "Status"
    ]
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write {len(EVENTS_DATA)} events")
        return len(EVENTS_DATA)
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, len(headers) + 2)
    
    # Clear existing data
    worksheet.clear()
    
    # Write headers
    worksheet.update(values=[headers], range_name='A1')
    
    # Format header row
    header_range = f'A1:{column_letter(len(headers) - 1)}1'
    worksheet.format(header_range, {
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6},
        'horizontalAlignment': 'CENTER'
    })
    
    # Prepare data rows
    rows = []
    for event in EVENTS_DATA:
        row = [
            event["name"],
            event["start"],
            event["end"],
            event["location"],
            event["cohorts"],
            event["priority"],
            event["cost_low"],
            event["cost_high"],
            event["category"],
            event["quarter"],
            event["action"],
            event["cfp_deadline"],
            event["website"],
            event["notes"],
            "Planning"  # Default status
        ]
        rows.append(row)
    
    # Write data
    if rows:
        end_col = column_letter(len(headers) - 1)
        worksheet.update(values=rows, range_name=f'A2:{end_col}{len(rows) + 1}')
    
    # Apply conditional formatting for Priority column (F)
    try:
        sheet_id = worksheet.id
        requests = []
        
        for priority, color in PRIORITY_COLORS.items():
            rule = {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": len(rows) + 1,
                            "startColumnIndex": 5,  # Column F (Priority)
                            "endColumnIndex": 6
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": priority}]
                            },
                            "format": {
                                "backgroundColor": color,
                                "textFormat": {
                                    "bold": True,
                                    "foregroundColor": {"red": 1, "green": 1, "blue": 1} if priority == "CRITICAL" else {"red": 0, "green": 0, "blue": 0}
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
            requests.append(rule)
        
        if requests:
            spreadsheet.batch_update({"requests": requests})
            print(f"  Applied priority colors")
    except Exception as e:
        print(f"  Warning: Could not apply priority colors: {e}")
    
    # Apply status dropdown
    try:
        validation_rule = DataValidationRule(
            BooleanCondition('ONE_OF_LIST', STATUS_OPTIONS),
            showCustomUi=True
        )
        status_col = column_letter(14)  # Column O (Status)
        range_str = f"{status_col}2:{status_col}{len(rows) + 1}"
        set_data_validation_for_cell_range(worksheet, range_str, validation_rule)
        print(f"  Applied status dropdown")
    except Exception as e:
        print(f"  Warning: Could not apply status dropdown: {e}")
    
    # Freeze header row
    worksheet.freeze(rows=1)
    
    # Auto-resize columns
    try:
        spreadsheet.batch_update({
            "requests": [{
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": len(headers)
                    }
                }
            }]
        })
    except Exception:
        pass
    
    print(f"  Wrote {len(rows)} events")
    time.sleep(2)
    
    return len(rows)


def sync_summary_tab(
    spreadsheet: gspread.Spreadsheet,
    dry_run: bool = False
) -> None:
    """Sync the summary tab with budget and metrics."""
    tab_name = TAB_NAMES["summary"]
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write summary data")
        return
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, 5)
    worksheet.clear()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Calculate metrics
    total_events = len(EVENTS_DATA)
    critical_events = len([e for e in EVENTS_DATA if e["priority"] == "CRITICAL"])
    high_events = len([e for e in EVENTS_DATA if e["priority"] == "High"])
    medium_events = len([e for e in EVENTS_DATA if e["priority"] == "Medium"])
    strategic_events = len([e for e in EVENTS_DATA if e["priority"] == "Strategic"])
    
    q1_events = len([e for e in EVENTS_DATA if e["quarter"] == "Q1"])
    q2_events = len([e for e in EVENTS_DATA if "Q2" in e["quarter"]])
    q3_events = len([e for e in EVENTS_DATA if "Q3" in e["quarter"]])
    q4_events = len([e for e in EVENTS_DATA if e["quarter"] == "Q4"])
    
    total_cost_low = sum(e["cost_low"] for e in EVENTS_DATA)
    total_cost_high = sum(e["cost_high"] for e in EVENTS_DATA)
    
    critical_cost_low = sum(e["cost_low"] for e in EVENTS_DATA if e["priority"] == "CRITICAL")
    critical_cost_high = sum(e["cost_high"] for e in EVENTS_DATA if e["priority"] == "CRITICAL")
    
    rows = [
        ["CHROMA EVENTS CALENDAR 2026 - SUMMARY", "", ""],
        ["", "", ""],
        ["OVERVIEW", "", ""],
        ["Metric", "Value", "Notes"],
        ["Total Events", total_events, ""],
        ["Critical Events", critical_events, "Must attend with booth + speaking"],
        ["High Priority Events", high_events, "Booth or speaking"],
        ["Medium Priority Events", medium_events, "Attend + network"],
        ["Strategic Events", strategic_events, "Selective presence"],
        ["", "", ""],
        ["QUARTERLY BREAKDOWN", "", ""],
        ["Quarter", "Event Count", ""],
        ["Q1 (Jan-Mar)", q1_events, ""],
        ["Q2 (Apr-Jun)", q2_events, ""],
        ["Q3 (Jul-Sep)", q3_events, ""],
        ["Q4 (Oct-Dec)", q4_events, ""],
        ["", "", ""],
        ["BUDGET SUMMARY", "", ""],
        ["Category", "Low Estimate", "High Estimate"],
        ["Total All Events", f"${total_cost_low:,}", f"${total_cost_high:,}"],
        ["Critical Events Only", f"${critical_cost_low:,}", f"${critical_cost_high:,}"],
        ["Recommended Budget", "$350,000", "$500,000"],
        ["", "", ""],
        ["BUDGET BY PRIORITY", "", ""],
        ["Priority", "% of Budget", "Recommendation"],
        ["CRITICAL (4 events)", "40-50%", "$150,000 - $250,000"],
        ["High (8 events)", "25-30%", "$100,000 - $150,000"],
        ["Medium (16 events)", "20-25%", "$80,000 - $100,000"],
        ["Strategic (4 events)", "5-10%", "$20,000 - $50,000"],
        ["", "", ""],
        ["CRITICAL EVENTS - MUST ATTEND", "", ""],
        ["Event", "Date", "Why Critical"],
        ["NVIDIA GTC 2026", "Mar 17-20", "Premier AI infrastructure conference"],
        ["AI Engineer World's Fair", "Jun 30 - Jul 2", "Largest technical AI conference"],
        ["AI Infra Summit 2026", "Sep 15-17", "Perfect ICP fit - infrastructure focus"],
        ["AWS re:Invent 2026", "Dec 1-5", "Largest cloud conference"],
        ["", "", ""],
        ["Last Updated", now, ""],
    ]
    
    worksheet.update(values=rows, range_name=f'A1:C{len(rows)}')
    
    # Format title
    worksheet.format('A1:C1', {
        'textFormat': {'bold': True, 'fontSize': 16},
        'horizontalAlignment': 'CENTER'
    })
    
    # Format section headers
    section_rows = [3, 11, 18, 24, 31]
    for row_num in section_rows:
        worksheet.format(f'A{row_num}:C{row_num}', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
    
    # Format table headers
    header_rows = [4, 12, 19, 25, 32]
    for row_num in header_rows:
        worksheet.format(f'A{row_num}:C{row_num}', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
        })
    
    worksheet.freeze(rows=1)
    
    print(f"  Summary tab updated")
    time.sleep(1)


def sync_action_items_tab(
    spreadsheet: gspread.Spreadsheet,
    dry_run: bool = False
) -> None:
    """Sync the action items tab with CFP deadlines and registrations."""
    tab_name = TAB_NAMES["action_items"]
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write action items")
        return
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, 8)
    worksheet.clear()
    
    headers = ["Event", "Action", "Deadline", "Priority", "Status", "Owner", "Notes"]
    
    # Generate action items from events
    action_items = []
    
    for event in EVENTS_DATA:
        if event["priority"] in ["CRITICAL", "High"]:
            # CFP submission
            if event["cfp_deadline"] != "N/A":
                action_items.append([
                    event["name"],
                    "Submit CFP",
                    event["cfp_deadline"],
                    event["priority"],
                    "Not Started",
                    "",
                    f"Speaking opportunity at {event['category']} event"
                ])
            
            # Registration
            action_items.append([
                event["name"],
                "Register / Book Booth",
                f"2 months before {event['start']}",
                event["priority"],
                "Not Started",
                "",
                f"Action: {event['action']}"
            ])
            
            # Travel booking
            action_items.append([
                event["name"],
                "Book Travel & Hotel",
                f"1 month before {event['start']}",
                event["priority"],
                "Not Started",
                "",
                event["location"]
            ])
    
    # Sort by priority
    priority_order = {"CRITICAL": 0, "High": 1, "Medium": 2, "Strategic": 3}
    action_items.sort(key=lambda x: priority_order.get(x[3], 99))
    
    # Write data
    worksheet.update(values=[headers], range_name='A1')
    
    if action_items:
        worksheet.update(values=action_items, range_name=f'A2:G{len(action_items) + 1}')
    
    # Format header
    worksheet.format('A1:G1', {
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6},
        'horizontalAlignment': 'CENTER'
    })
    
    # Add status dropdown
    try:
        status_options = ["Not Started", "In Progress", "Completed", "Blocked"]
        validation_rule = DataValidationRule(
            BooleanCondition('ONE_OF_LIST', status_options),
            showCustomUi=True
        )
        range_str = f"E2:E{len(action_items) + 1}"
        set_data_validation_for_cell_range(worksheet, range_str, validation_rule)
    except Exception:
        pass
    
    worksheet.freeze(rows=1)
    
    print(f"  Wrote {len(action_items)} action items")
    time.sleep(1)


def sync_critical_events_tab(
    spreadsheet: gspread.Spreadsheet,
    dry_run: bool = False
) -> None:
    """Sync the critical events tab for quick reference."""
    tab_name = TAB_NAMES["critical"]
    
    print(f"\nSyncing {tab_name}...")
    
    if dry_run:
        print(f"  [DRY RUN] Would write critical events")
        return
    
    worksheet = get_or_create_worksheet(spreadsheet, tab_name, 10)
    worksheet.clear()
    
    critical_events = [e for e in EVENTS_DATA if e["priority"] == "CRITICAL"]
    
    rows = [
        ["🔴 CRITICAL EVENTS - MUST ATTEND", "", "", "", ""],
        ["", "", "", "", ""],
        ["Event", "Date", "Location", "Budget Range", "Why Critical"],
    ]
    
    for event in critical_events:
        rows.append([
            event["name"],
            f"{event['start']} to {event['end']}",
            event["location"],
            f"${event['cost_low']:,} - ${event['cost_high']:,}",
            event["notes"]
        ])
    
    rows.append(["", "", "", "", ""])
    rows.append(["Total Critical Events Budget:", "", "", 
                 f"${sum(e['cost_low'] for e in critical_events):,} - ${sum(e['cost_high'] for e in critical_events):,}", ""])
    
    worksheet.update(values=rows, range_name=f'A1:E{len(rows)}')
    
    # Format title
    worksheet.format('A1:E1', {
        'textFormat': {'bold': True, 'fontSize': 14},
        'backgroundColor': {'red': 0.8, 'green': 0.2, 'blue': 0.2},
        'horizontalAlignment': 'CENTER',
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
    })
    
    # Format header row
    worksheet.format('A3:E3', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
    })
    
    print(f"  Wrote {len(critical_events)} critical events")
    time.sleep(1)


def list_sheet_stats(spreadsheet: gspread.Spreadsheet) -> None:
    """List current statistics from the Google Sheet."""
    print("\nCurrent Google Sheet Statistics:")
    print("-" * 50)
    
    for worksheet in spreadsheet.worksheets():
        try:
            values = worksheet.get_all_values()
            data_rows = len(values) - 1 if values else 0
        except Exception:
            data_rows = "Unknown"
        
        print(f"  {worksheet.title}: {data_rows} rows")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync Chroma Events Calendar to Google Sheets"
    )
    parser.add_argument(
        "--sheet-id",
        type=str,
        help="Google Sheet ID (overrides env variable)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without pushing to Google Sheets"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current sheet statistics"
    )
    
    args = parser.parse_args()
    
    # Get sheet ID
    sheet_id = args.sheet_id or EVENTS_SHEET_ID
    
    if not sheet_id:
        print("ERROR: No Google Sheet ID provided.")
        print("Either:")
        print("  1. Set GOOGLE_SHEET_ID or EVENTS_GOOGLE_SHEET_ID in .env")
        print("  2. Use --sheet-id argument")
        exit(1)
    
    print("=" * 60)
    print("CHROMA EVENTS CALENDAR - GOOGLE SHEETS SYNC")
    print("=" * 60)
    print(f"Sheet ID: {sheet_id[:20]}...")
    print(f"Credentials: {CREDENTIALS_FILE}")
    if args.dry_run:
        print("MODE: DRY RUN (no changes will be made)")
    print()
    
    # Connect to Google Sheets
    try:
        client = get_sheets_client()
        spreadsheet = client.open_by_key(sheet_id)
        print(f"Connected to: {spreadsheet.title}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit(1)
    except gspread.SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet not found. Check your sheet ID.")
        print("Make sure the sheet is shared with the service account email.")
        exit(1)
    except Exception as e:
        print(f"ERROR connecting to Google Sheets: {e}")
        exit(1)
    
    # List mode
    if args.list:
        list_sheet_stats(spreadsheet)
        return
    
    # Sync all tabs
    print("\n" + "=" * 60)
    print("SYNCING EVENTS DATA")
    print("=" * 60)
    
    event_count = sync_events_calendar(spreadsheet, args.dry_run)
    sync_summary_tab(spreadsheet, args.dry_run)
    sync_action_items_tab(spreadsheet, args.dry_run)
    sync_critical_events_tab(spreadsheet, args.dry_run)
    
    # Summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total events synced: {event_count}")
    print(f"Critical events: {len([e for e in EVENTS_DATA if e['priority'] == 'CRITICAL'])}")
    print(f"High priority events: {len([e for e in EVENTS_DATA if e['priority'] == 'High'])}")
    
    if not args.dry_run:
        print(f"\nView your events calendar: https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == "__main__":
    main()

