#!/usr/bin/env python3
"""
Sync Deep Research Pipeline Companies to Attio

Syncs all 270+ companies from the LinkedIn Sales Navigator extension
to your Attio custom list.

Usage:
    python sync_companies_to_attio.py
    python sync_companies_to_attio.py --test  # Test connection only
    python sync_companies_to_attio.py --limit 10  # Sync first 10 only
"""

import os
import json
import requests
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Attio Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
ATTIO_BASE_URL = "https://api.attio.com/v2"
ATTIO_WORKSPACE_SLUG = "chromadb"

# Your custom list ID from the URL you provided
# URL: https://app.attio.com/chromadb/collection/d391cef0-726b-4ee9-8ad2-4237aed35dc6/view/...
ATTIO_LIST_ID = "d391cef0-726b-4ee9-8ad2-4237aed35dc6"

# ============================================================
# COMPANY DATA - 270+ companies from Deep Research Pipeline
# ============================================================

COMPANIES_DATA = [
    # TIER 1 - HIGHEST PRIORITY
    {"name": "Mintlify", "domain": "mintlify.com", "category": "Tier 1 Priority", "valuation": "Acquired Trieve", "priority": "HIGH"},
    {"name": "Clay", "domain": "clay.com", "category": "Tier 1 Priority", "valuation": "$3.1B", "priority": "HIGH"},
    {"name": "Apollo.io", "domain": "apollo.io", "category": "Tier 1 Priority", "valuation": "$110M+ funding", "priority": "HIGH"},
    {"name": "Zendesk", "domain": "zendesk.com", "category": "Tier 1 Priority", "valuation": "$10.2B", "priority": "HIGH"},
    {"name": "Jasper", "domain": "jasper.ai", "category": "Tier 1 Priority", "valuation": "$125M Series A", "priority": "HIGH"},

    # TIER 2 - STRONG CANDIDATES
    {"name": "Pieces for Developers", "domain": "pieces.app", "category": "Tier 2 Priority", "valuation": "Growing", "priority": "HIGH"},
    {"name": "GitBook", "domain": "gitbook.com", "category": "Tier 2 Priority", "valuation": "Bootstrapped", "priority": "HIGH"},
    {"name": "ReadMe", "domain": "readme.com", "category": "Tier 2 Priority", "valuation": "$9M Series A", "priority": "HIGH"},
    {"name": "Forethought", "domain": "forethought.ai", "category": "Tier 2 Priority", "valuation": "~$500M", "priority": "HIGH"},
    {"name": "Qualified", "domain": "qualified.com", "category": "Tier 2 Priority", "valuation": "$100M+ funding", "priority": "HIGH"},

    # TIER 3 - HIGH-VALUE TARGETS
    {"name": "Glean", "domain": "glean.com", "category": "Tier 3 Priority", "valuation": "$7.2B", "priority": "HIGH"},
    {"name": "Cursor", "domain": "cursor.com", "category": "Tier 3 Priority", "valuation": "$29.3B", "priority": "HIGH"},
    {"name": "Harvey", "domain": "harvey.ai", "category": "Tier 3 Priority", "valuation": "$8B", "priority": "HIGH"},
    {"name": "Abridge", "domain": "abridge.com", "category": "Tier 3 Priority", "valuation": "$5.3B", "priority": "HIGH"},
    {"name": "n8n", "domain": "n8n.io", "category": "Tier 3 Priority", "valuation": "$2.5B", "priority": "HIGH"},

    # DOCUMENTATION & API PLATFORMS
    {"name": "Postman", "domain": "postman.com", "category": "Documentation & API", "valuation": "$5.6B", "priority": "HIGH"},
    {"name": "Swagger", "domain": "swagger.io", "category": "Documentation & API", "valuation": "SmartBear owned", "priority": "MEDIUM"},
    {"name": "Stoplight", "domain": "stoplight.io", "category": "Documentation & API", "valuation": "$40M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "APIdog", "domain": "apidog.com", "category": "Documentation & API", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Hoppscotch", "domain": "hoppscotch.io", "category": "Documentation & API", "valuation": "Open-source", "priority": "MEDIUM"},
    {"name": "EchoAPI", "domain": "echoapi.com", "category": "Documentation & API", "valuation": "Early stage", "priority": "MEDIUM"},
    {"name": "Bruno", "domain": "usebruno.com", "category": "Documentation & API", "valuation": "Open-source", "priority": "MEDIUM"},
    {"name": "Kong Insomnia", "domain": "insomnia.rest", "category": "Documentation & API", "valuation": "Kong owned", "priority": "MEDIUM"},
    {"name": "Document360", "domain": "document360.com", "category": "Documentation & API", "valuation": "$12M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Archbee", "domain": "archbee.com", "category": "Documentation & API", "valuation": "$4M+ funding", "priority": "MEDIUM"},
    {"name": "Notion", "domain": "notion.so", "category": "Documentation & API", "valuation": "$10B", "priority": "MEDIUM"},
    {"name": "Slite", "domain": "slite.com", "category": "Documentation & API", "valuation": "$15M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Tettra", "domain": "tettra.com", "category": "Documentation & API", "valuation": "$4M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Slab", "domain": "slab.com", "category": "Documentation & API", "valuation": "Acquired by Qualtrics", "priority": "MEDIUM"},

    # AI CODING ASSISTANTS
    {"name": "Anysphere", "domain": "anysphere.inc", "category": "AI Coding Assistants", "valuation": "$29.3B", "priority": "HIGH"},
    {"name": "Codeium", "domain": "codeium.com", "category": "AI Coding Assistants", "valuation": "$2.85B", "priority": "HIGH"},
    {"name": "Windsurf", "domain": "codeium.com", "category": "AI Coding Assistants", "valuation": "$2.85B", "priority": "HIGH"},
    {"name": "Augment", "domain": "augmentcode.com", "category": "AI Coding Assistants", "valuation": "$977M", "priority": "HIGH"},
    {"name": "Poolside AI", "domain": "poolside.ai", "category": "AI Coding Assistants", "valuation": "$500M Series B", "priority": "HIGH"},
    {"name": "Magic AI", "domain": "magic.dev", "category": "AI Coding Assistants", "valuation": "$400M+ funding", "priority": "HIGH"},
    {"name": "Cognition", "domain": "cognition.ai", "category": "AI Coding Assistants", "valuation": "$4B", "priority": "HIGH"},
    {"name": "Tabnine", "domain": "tabnine.com", "category": "AI Coding Assistants", "valuation": "$55M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Replit", "domain": "replit.com", "category": "AI Coding Assistants", "valuation": "$1.16B", "priority": "HIGH"},
    {"name": "Qodo", "domain": "qodo.ai", "category": "AI Coding Assistants", "valuation": "$51M funding", "priority": "HIGH"},
    {"name": "Sourcegraph", "domain": "sourcegraph.com", "category": "AI Coding Assistants", "valuation": "$150M+ funding", "priority": "HIGH"},
    {"name": "Warp", "domain": "warp.dev", "category": "AI Coding Assistants", "valuation": "$73M funding", "priority": "MEDIUM-HIGH"},
    {"name": "CodeGPT", "domain": "codegpt.co", "category": "AI Coding Assistants", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Continue.dev", "domain": "continue.dev", "category": "AI Coding Assistants", "valuation": "Open-source", "priority": "MEDIUM"},
    {"name": "Bolt.new", "domain": "bolt.new", "category": "AI Coding Assistants", "valuation": "Viral growth", "priority": "HIGH"},
    {"name": "v0.dev", "domain": "v0.dev", "category": "AI Coding Assistants", "valuation": "Vercel", "priority": "MEDIUM-HIGH"},
    {"name": "Lovable", "domain": "lovable.dev", "category": "AI Coding Assistants", "valuation": "$100M ARR", "priority": "HIGH"},

    # SALES INTELLIGENCE
    {"name": "Sumble", "domain": "sumble.com", "category": "Sales Intelligence", "valuation": "$38.5M (Oct 2025)", "priority": "HIGH"},
    {"name": "Cognism", "domain": "cognism.com", "category": "Sales Intelligence", "valuation": "$100M+ funding", "priority": "HIGH"},
    {"name": "ZoomInfo", "domain": "zoominfo.com", "category": "Sales Intelligence", "valuation": "$8B+ market cap", "priority": "HIGH"},
    {"name": "Gong", "domain": "gong.io", "category": "Sales Intelligence", "valuation": "$7.25B", "priority": "HIGH"},
    {"name": "6sense", "domain": "6sense.com", "category": "Sales Intelligence", "valuation": "$5.2B", "priority": "MEDIUM-HIGH"},
    {"name": "Outreach", "domain": "outreach.io", "category": "Sales Intelligence", "valuation": "$4.4B", "priority": "MEDIUM-HIGH"},
    {"name": "Salesloft", "domain": "salesloft.com", "category": "Sales Intelligence", "valuation": "Vista Equity", "priority": "MEDIUM-HIGH"},
    {"name": "Lusha", "domain": "lusha.com", "category": "Sales Intelligence", "valuation": "$205M funding", "priority": "MEDIUM"},
    {"name": "Seamless.AI", "domain": "seamless.ai", "category": "Sales Intelligence", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "LeadIQ", "domain": "leadiq.com", "category": "Sales Intelligence", "valuation": "$30M+ funding", "priority": "MEDIUM"},
    {"name": "Clearbit", "domain": "clearbit.com", "category": "Sales Intelligence", "valuation": "Acquired by HubSpot", "priority": "MEDIUM"},
    {"name": "Demandbase", "domain": "demandbase.com", "category": "Sales Intelligence", "valuation": "$400M+ funding", "priority": "MEDIUM-HIGH"},

    # CUSTOMER SUPPORT AI
    {"name": "Sierra AI", "domain": "sierra.ai", "category": "Customer Support AI", "valuation": "$104M ARR", "priority": "HIGH"},
    {"name": "Decagon", "domain": "decagon.ai", "category": "Customer Support AI", "valuation": "$1.5B", "priority": "HIGH"},
    {"name": "Intercom", "domain": "intercom.com", "category": "Customer Support AI", "valuation": "$1.3B+", "priority": "HIGH"},
    {"name": "Freshworks", "domain": "freshworks.com", "category": "Customer Support AI", "valuation": "$4B+ market cap", "priority": "MEDIUM-HIGH"},
    {"name": "Crescendo.ai", "domain": "crescendo.ai", "category": "Customer Support AI", "valuation": "$500M, $91M ARR", "priority": "HIGH"},
    {"name": "Ada", "domain": "ada.cx", "category": "Customer Support AI", "valuation": "$190M+ funding", "priority": "HIGH"},
    {"name": "Kustomer", "domain": "kustomer.com", "category": "Customer Support AI", "valuation": "Meta spun out", "priority": "MEDIUM"},
    {"name": "Gladly", "domain": "gladly.com", "category": "Customer Support AI", "valuation": "$90M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Gorgias", "domain": "gorgias.com", "category": "Customer Support AI", "valuation": "$60M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Help Scout", "domain": "helpscout.com", "category": "Customer Support AI", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Voiceflow", "domain": "voiceflow.com", "category": "Customer Support AI", "valuation": "$45M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Kore.ai", "domain": "kore.ai", "category": "Customer Support AI", "valuation": "$150M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Rasa", "domain": "rasa.com", "category": "Customer Support AI", "valuation": "$70M+ funding", "priority": "MEDIUM-HIGH"},

    # HEALTHCARE AI
    {"name": "Nabla", "domain": "nabla.com", "category": "Healthcare AI", "valuation": "~$300M, $120M funding", "priority": "HIGH"},
    {"name": "Ambience Healthcare", "domain": "ambiencehealthcare.com", "category": "Healthcare AI", "valuation": "$1.25B", "priority": "HIGH"},
    {"name": "Suki AI", "domain": "suki.ai", "category": "Healthcare AI", "valuation": "$500M", "priority": "HIGH"},
    {"name": "DeepScribe", "domain": "deepscribe.ai", "category": "Healthcare AI", "valuation": "$50M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Freed", "domain": "getfreed.ai", "category": "Healthcare AI", "valuation": "$30M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Regard", "domain": "regard.com", "category": "Healthcare AI", "valuation": "$81M+ funding", "priority": "HIGH"},
    {"name": "CodaMetrix", "domain": "codametrix.com", "category": "Healthcare AI", "valuation": "$95M+ funding", "priority": "HIGH"},
    {"name": "Tennr", "domain": "tennr.com", "category": "Healthcare AI", "valuation": "$605M, $101M Series C", "priority": "HIGH"},
    {"name": "OpenEvidence", "domain": "openevidence.com", "category": "Healthcare AI", "valuation": "$6B, $200M Series C", "priority": "HIGH"},
    {"name": "Eleos Health", "domain": "eleos.health", "category": "Healthcare AI", "valuation": "$50M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Predoc", "domain": "predoc.io", "category": "Healthcare AI", "valuation": "$30M Series A", "priority": "HIGH"},
    {"name": "Commure", "domain": "commure.com", "category": "Healthcare AI", "valuation": "Acquired Augmedix $139M", "priority": "HIGH"},
    {"name": "Notable Health", "domain": "notablehealth.com", "category": "Healthcare AI", "valuation": "$100M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Cohere Health", "domain": "coherehealth.com", "category": "Healthcare AI", "valuation": "$50M+ funding", "priority": "HIGH"},
    {"name": "Viz.ai", "domain": "viz.ai", "category": "Healthcare AI", "valuation": "$250M+ funding", "priority": "HIGH"},
    {"name": "Hippocratic AI", "domain": "hippocraticai.com", "category": "Healthcare AI", "valuation": "$3.5B", "priority": "HIGH"},

    # LEGAL TECH
    {"name": "Harvey AI", "domain": "harvey.ai", "category": "Legal Tech", "valuation": "$8B (Dec 2025)", "priority": "HIGH"},
    {"name": "EvenUp", "domain": "evenuplaw.com", "category": "Legal Tech", "valuation": "$2B+", "priority": "HIGH"},
    {"name": "Clio", "domain": "clio.com", "category": "Legal Tech", "valuation": "$5B", "priority": "HIGH"},
    {"name": "Spellbook", "domain": "spellbook.legal", "category": "Legal Tech", "valuation": "$350M", "priority": "HIGH"},
    {"name": "Eve", "domain": "eve.legal", "category": "Legal Tech", "valuation": "$47M Series A", "priority": "HIGH"},
    {"name": "Filevine", "domain": "filevine.com", "category": "Legal Tech", "valuation": "$400M funding", "priority": "HIGH"},
    {"name": "Eudia", "domain": "eudia.com", "category": "Legal Tech", "valuation": "$105M Series A", "priority": "HIGH"},
    {"name": "Luminance", "domain": "luminance.com", "category": "Legal Tech", "valuation": "Strong growth", "priority": "HIGH"},
    {"name": "Supio", "domain": "supio.com", "category": "Legal Tech", "valuation": "$91M funding", "priority": "HIGH"},
    {"name": "Legora", "domain": "legora.com", "category": "Legal Tech", "valuation": "+3133% search volume", "priority": "MEDIUM-HIGH"},
    {"name": "Darrow", "domain": "darrow.ai", "category": "Legal Tech", "valuation": "$35M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Ironclad", "domain": "ironcladhq.com", "category": "Legal Tech", "valuation": "$150M+ funding", "priority": "HIGH"},
    {"name": "LinkSquares", "domain": "linksquares.com", "category": "Legal Tech", "valuation": "$130M+ funding", "priority": "HIGH"},
    {"name": "Lexion", "domain": "lexion.ai", "category": "Legal Tech", "valuation": "$30M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Relativity", "domain": "relativity.com", "category": "Legal Tech", "valuation": "Private equity", "priority": "MEDIUM-HIGH"},
    {"name": "Onna", "domain": "onna.com", "category": "Legal Tech", "valuation": "$80M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "CS Disco", "domain": "csdisco.com", "category": "Legal Tech", "valuation": "Public", "priority": "MEDIUM-HIGH"},
    {"name": "ContractPodAi", "domain": "contractpodai.com", "category": "Legal Tech", "valuation": "~$500M", "priority": "MEDIUM-HIGH"},
    {"name": "Juro", "domain": "juro.com", "category": "Legal Tech", "valuation": "~$150M", "priority": "MEDIUM"},

    # AI WORKFLOW AUTOMATION
    {"name": "Zapier", "domain": "zapier.com", "category": "AI Workflow Automation", "valuation": "$5B+", "priority": "HIGH"},
    {"name": "Make", "domain": "make.com", "category": "AI Workflow Automation", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Lindy AI", "domain": "lindy.ai", "category": "AI Workflow Automation", "valuation": "~$200M", "priority": "HIGH"},
    {"name": "Relevance AI", "domain": "relevanceai.com", "category": "AI Workflow Automation", "valuation": "$150M", "priority": "HIGH"},
    {"name": "Workato", "domain": "workato.com", "category": "AI Workflow Automation", "valuation": "$5.7B", "priority": "MEDIUM-HIGH"},
    {"name": "Relay.app", "domain": "relay.app", "category": "AI Workflow Automation", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Pipedream", "domain": "pipedream.com", "category": "AI Workflow Automation", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Airbyte", "domain": "airbyte.com", "category": "AI Workflow Automation", "valuation": "$200M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Tray.io", "domain": "tray.io", "category": "AI Workflow Automation", "valuation": "$150M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Bardeen", "domain": "bardeen.ai", "category": "AI Workflow Automation", "valuation": "$15M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Parabola", "domain": "parabola.io", "category": "AI Workflow Automation", "valuation": "$40M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Alloy", "domain": "runalloy.com", "category": "AI Workflow Automation", "valuation": "$100M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Merge", "domain": "merge.dev", "category": "AI Workflow Automation", "valuation": "$75M+ funding", "priority": "MEDIUM-HIGH"},

    # ENTERPRISE SEARCH
    {"name": "Guru", "domain": "getguru.com", "category": "Enterprise Search", "valuation": "$100M+ funding", "priority": "HIGH"},
    {"name": "Coveo", "domain": "coveo.com", "category": "Enterprise Search", "valuation": "Public (TSX: CVO)", "priority": "MEDIUM-HIGH"},
    {"name": "Elastic", "domain": "elastic.co", "category": "Enterprise Search", "valuation": "Public (NYSE: ESTC)", "priority": "MEDIUM"},
    {"name": "Algolia", "domain": "algolia.com", "category": "Enterprise Search", "valuation": "$2.25B", "priority": "MEDIUM-HIGH"},
    {"name": "Lucidworks", "domain": "lucidworks.com", "category": "Enterprise Search", "valuation": "$100M+ funding", "priority": "HIGH"},
    {"name": "Sinequa", "domain": "sinequa.com", "category": "Enterprise Search", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Yext", "domain": "yext.com", "category": "Enterprise Search", "valuation": "Public (NYSE: YEXT)", "priority": "MEDIUM"},
    {"name": "Capacity", "domain": "capacity.com", "category": "Enterprise Search", "valuation": "$30M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Bloomfire", "domain": "bloomfire.com", "category": "Enterprise Search", "valuation": "$25M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Dashworks", "domain": "dashworks.ai", "category": "Enterprise Search", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Hebbia", "domain": "hebbia.ai", "category": "Enterprise Search", "valuation": "$130M+ funding", "priority": "HIGH"},
    {"name": "Vectara", "domain": "vectara.com", "category": "Enterprise Search", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Pryon", "domain": "pryon.com", "category": "Enterprise Search", "valuation": "$100M+ funding", "priority": "HIGH"},

    # FINANCIAL RESEARCH
    {"name": "AlphaSense", "domain": "alpha-sense.com", "category": "Financial Research", "valuation": "$1.4B+ funding", "priority": "HIGH"},
    {"name": "Koyfin", "domain": "koyfin.com", "category": "Financial Research", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Fintool", "domain": "fintool.com", "category": "Financial Research", "valuation": "Launched 2024", "priority": "MEDIUM-HIGH"},
    {"name": "Hudson Labs", "domain": "hudsonlabs.com", "category": "Financial Research", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Rogo", "domain": "rogodata.com", "category": "Financial Research", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Dataminr", "domain": "dataminr.com", "category": "Financial Research", "valuation": "$1.8B", "priority": "HIGH"},
    {"name": "RavenPack", "domain": "ravenpack.com", "category": "Financial Research", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Visible Alpha", "domain": "visiblealpha.com", "category": "Financial Research", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "YCharts", "domain": "ycharts.com", "category": "Financial Research", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Atom Finance", "domain": "atom.finance", "category": "Financial Research", "valuation": "$65M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Daloopa", "domain": "daloopa.com", "category": "Financial Research", "valuation": "~$100M", "priority": "HIGH"},
    {"name": "YipitData", "domain": "yipitdata.com", "category": "Financial Research", "valuation": "$1B+", "priority": "HIGH"},
    {"name": "Toggle AI", "domain": "toggle.ai", "category": "Financial Research", "valuation": "~$200M", "priority": "MEDIUM-HIGH"},
    {"name": "Reflexivity", "domain": "reflexivity.com", "category": "Financial Research", "valuation": "~$200M", "priority": "MEDIUM-HIGH"},

    # HR & RECRUITING AI
    {"name": "Eightfold AI", "domain": "eightfold.ai", "category": "HR & Recruiting AI", "valuation": "$2B+", "priority": "HIGH"},
    {"name": "Paradox", "domain": "paradox.ai", "category": "HR & Recruiting AI", "valuation": "Growing fast", "priority": "HIGH"},
    {"name": "Phenom", "domain": "phenom.com", "category": "HR & Recruiting AI", "valuation": "$1.7B", "priority": "HIGH"},
    {"name": "Beamery", "domain": "beamery.com", "category": "HR & Recruiting AI", "valuation": "$800M", "priority": "HIGH"},
    {"name": "HireVue", "domain": "hirevue.com", "category": "HR & Recruiting AI", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Seekout", "domain": "seekout.com", "category": "HR & Recruiting AI", "valuation": "$115M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Gloat", "domain": "gloat.com", "category": "HR & Recruiting AI", "valuation": "$190M+ funding", "priority": "HIGH"},
    {"name": "Findem", "domain": "findem.ai", "category": "HR & Recruiting AI", "valuation": "$50M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Moonhub", "domain": "moonhub.ai", "category": "HR & Recruiting AI", "valuation": "$50M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Mercor", "domain": "mercor.com", "category": "HR & Recruiting AI", "valuation": "$133M funding", "priority": "HIGH"},
    {"name": "hireEZ", "domain": "hireez.com", "category": "HR & Recruiting AI", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Turing", "domain": "turing.com", "category": "HR & Recruiting AI", "valuation": "$159M funding", "priority": "MEDIUM-HIGH"},
    {"name": "Textio", "domain": "textio.com", "category": "HR & Recruiting AI", "valuation": "$42M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Sense", "domain": "sensehq.com", "category": "HR & Recruiting AI", "valuation": "$90M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Checkr", "domain": "checkr.com", "category": "HR & Recruiting AI", "valuation": "$500M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "iCIMS", "domain": "icims.com", "category": "HR & Recruiting AI", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Greenhouse", "domain": "greenhouse.io", "category": "HR & Recruiting AI", "valuation": "~$500M", "priority": "MEDIUM"},
    {"name": "Lever", "domain": "lever.co", "category": "HR & Recruiting AI", "valuation": "N/A", "priority": "MEDIUM"},
    {"name": "Ashby", "domain": "ashbyhq.com", "category": "HR & Recruiting AI", "valuation": "~$100M", "priority": "MEDIUM"},
    {"name": "Gem", "domain": "gem.com", "category": "HR & Recruiting AI", "valuation": "~$300M", "priority": "MEDIUM"},
    {"name": "Rippling", "domain": "rippling.com", "category": "HR & Recruiting AI", "valuation": "$13.5B", "priority": "MEDIUM"},

    # CONTENT & SEO AI
    {"name": "Surfer SEO", "domain": "surferseo.com", "category": "Content & SEO AI", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Clearscope", "domain": "clearscope.io", "category": "Content & SEO AI", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "Frase", "domain": "frase.io", "category": "Content & SEO AI", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "MarketMuse", "domain": "marketmuse.com", "category": "Content & SEO AI", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Writesonic", "domain": "writesonic.com", "category": "Content & SEO AI", "valuation": "$26M+ funding", "priority": "MEDIUM"},
    {"name": "Copy.ai", "domain": "copy.ai", "category": "Content & SEO AI", "valuation": "$60M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Writer", "domain": "writer.com", "category": "Content & SEO AI", "valuation": "$100M+ funding", "priority": "HIGH"},
    {"name": "Semrush", "domain": "semrush.com", "category": "Content & SEO AI", "valuation": "Public (NYSE: SEMR)", "priority": "MEDIUM"},
    {"name": "Ahrefs", "domain": "ahrefs.com", "category": "Content & SEO AI", "valuation": "Growing", "priority": "MEDIUM"},
    {"name": "Grammarly", "domain": "grammarly.com", "category": "Content & SEO AI", "valuation": "$13B", "priority": "MEDIUM"},
    {"name": "AI21 Labs", "domain": "ai21.com", "category": "Content & SEO AI", "valuation": "$1.4B", "priority": "MEDIUM-HIGH"},
    {"name": "Typeface", "domain": "typeface.ai", "category": "Content & SEO AI", "valuation": "~$1B", "priority": "HIGH"},
    {"name": "Anyword", "domain": "anyword.com", "category": "Content & SEO AI", "valuation": "~$100M", "priority": "MEDIUM"},

    # REAL ESTATE & PROPTECH
    {"name": "EliseAI", "domain": "eliseai.com", "category": "Real Estate & PropTech", "valuation": "$75M+ funding", "priority": "HIGH"},
    {"name": "Dealpath", "domain": "dealpath.com", "category": "Real Estate & PropTech", "valuation": "Growing", "priority": "MEDIUM-HIGH"},
    {"name": "CompStak", "domain": "compstak.com", "category": "Real Estate & PropTech", "valuation": "$70M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "VTS", "domain": "vts.com", "category": "Real Estate & PropTech", "valuation": "$100M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "Measurabl", "domain": "measurabl.com", "category": "Real Estate & PropTech", "valuation": "$100M+ funding", "priority": "MEDIUM-HIGH"},
    {"name": "LeaseAI", "domain": "leaseai.com", "category": "Real Estate & PropTech", "valuation": "$50M Series B", "priority": "HIGH"},
    {"name": "Cherre", "domain": "cherre.com", "category": "Real Estate & PropTech", "valuation": "$50M+ funding", "priority": "HIGH"},
    {"name": "Placer.ai", "domain": "placer.ai", "category": "Real Estate & PropTech", "valuation": "$1.5B", "priority": "HIGH"},
    {"name": "Crexi", "domain": "crexi.com", "category": "Real Estate & PropTech", "valuation": "~$300M", "priority": "MEDIUM-HIGH"},

    # RESEARCH TOOLS
    {"name": "Elicit", "domain": "elicit.com", "category": "Research Tools", "valuation": "$100M", "priority": "HIGH"},
    {"name": "Semantic Scholar", "domain": "semanticscholar.org", "category": "Research Tools", "valuation": "Allen Institute", "priority": "HIGH"},
    {"name": "Consensus", "domain": "consensus.app", "category": "Research Tools", "valuation": "~$20M", "priority": "MEDIUM-HIGH"},
    {"name": "Scite", "domain": "scite.ai", "category": "Research Tools", "valuation": "Acquired", "priority": "HIGH"},
    {"name": "Iris.ai", "domain": "iris.ai", "category": "Research Tools", "valuation": "~$30M", "priority": "HIGH"},
    {"name": "ResearchRabbit", "domain": "researchrabbit.ai", "category": "Research Tools", "valuation": "~$5M", "priority": "MEDIUM"},
    {"name": "Connected Papers", "domain": "connectedpapers.com", "category": "Research Tools", "valuation": "~$5M", "priority": "MEDIUM"},
    {"name": "Litmaps", "domain": "litmaps.com", "category": "Research Tools", "valuation": "~$10M", "priority": "MEDIUM"},

    # PROCUREMENT
    {"name": "Zip", "domain": "ziphq.com", "category": "Procurement", "valuation": "$2.2B", "priority": "HIGH"},
    {"name": "Ramp", "domain": "ramp.com", "category": "Procurement", "valuation": "$22.5B", "priority": "HIGH"},
    {"name": "Brex", "domain": "brex.com", "category": "Procurement", "valuation": "~$10B", "priority": "MEDIUM"},
    {"name": "Coupa", "domain": "coupa.com", "category": "Procurement", "valuation": "PE-owned", "priority": "MEDIUM"},
    {"name": "Airbase", "domain": "airbase.com", "category": "Procurement", "valuation": "~$600M", "priority": "MEDIUM-HIGH"},
    {"name": "Spendesk", "domain": "spendesk.com", "category": "Procurement", "valuation": "~$500M", "priority": "MEDIUM-HIGH"},
]


class AttioCompanySync:
    """Sync companies to Attio CRM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ATTIO_API_KEY
        if not self.api_key:
            print("❌ ATTIO_API_KEY not set in .env")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to Attio."""
        url = f"{ATTIO_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=json_data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def find_company(self, company_name: str, domain: str = None) -> Optional[dict]:
        """Search for existing company in Attio by name or domain."""
        # First try to find by domain (more accurate)
        if domain:
            response = self._request(
                "POST",
                "/objects/companies/records/query",
                {
                    "filter": {
                        "domains": {"$contains": domain}
                    }
                }
            )
            if response and response.get("data"):
                return response["data"][0]
        
        # Fallback to name search
        response = self._request(
            "POST",
            "/objects/companies/records/query",
            {
                "filter": {
                    "name": {"$contains": company_name}
                }
            }
        )
        
        if response and response.get("data"):
            return response["data"][0]
        return None
    
    def create_company(self, company: dict) -> Optional[str]:
        """Create a new company record in Attio with name and domain."""
        values = {
            "name": [{"value": company["name"]}],
        }
        
        # Add domain - this is critical for Attio to identify the company
        if company.get("domain"):
            values["domains"] = [{"domain": company["domain"]}]
        
        # Add description with category and valuation
        description = f"Category: {company.get('category', 'N/A')}\nValuation: {company.get('valuation', 'N/A')}\nPriority: {company.get('priority', 'N/A')}"
        values["description"] = [{"value": description}]
        
        response = self._request(
            "POST",
            "/objects/companies/records",
            {"data": {"values": values}}
        )
        
        if response:
            return response.get("data", {}).get("id", {}).get("record_id")
        return None
    
    def get_list_entries(self) -> List[str]:
        """Get all company names already in the list."""
        existing = []
        response = self._request(
            "POST",
            f"/lists/{ATTIO_LIST_ID}/entries/query",
            {"limit": 500}
        )
        
        if response and response.get("data"):
            for entry in response["data"]:
                parent = entry.get("parent_record", {})
                values = parent.get("values", {})
                name_list = values.get("name", [])
                if name_list:
                    existing.append(name_list[0].get("value", "").lower())
        
        return existing
    
    def add_to_list(self, record_id: str, company: dict) -> bool:
        """Add a company to the custom list."""
        # Add entry without custom attributes (list may not have notes field)
        response = self._request(
            "POST",
            f"/lists/{ATTIO_LIST_ID}/entries",
            {
                "data": {
                    "parent_object": "companies",
                    "parent_record_id": record_id,
                    "entry_values": {}
                }
            }
        )
        
        return response is not None
    
    def sync_company(self, company: dict, existing_in_list: List[str]) -> tuple:
        """Sync a single company. Returns (success, status, record_id)."""
        company_name = company["name"]
        company_domain = company.get("domain")
        
        # Check if already in list
        if company_name.lower() in existing_in_list:
            return True, "already_in_list", None
        
        # Find or create company (search by domain first, then name)
        existing = self.find_company(company_name, company_domain)
        
        if existing:
            record_id = existing.get("id", {}).get("record_id")
        else:
            record_id = self.create_company(company)
            if not record_id:
                return False, "create_failed", None
        
        # Add to list
        if self.add_to_list(record_id, company):
            return True, "added", record_id
        else:
            return False, "list_add_failed", record_id
    
    def sync_all(self, companies: List[dict], delay: float = 0.3, limit: int = None) -> dict:
        """Sync all companies to Attio."""
        if not self.enabled:
            return {"error": "Attio not configured"}
        
        if limit:
            companies = companies[:limit]
        
        print(f"\n📤 Syncing {len(companies)} companies to Attio...")
        print(f"   List ID: {ATTIO_LIST_ID}")
        print()
        
        # Get existing entries
        print("   Fetching existing list entries...")
        existing_in_list = self.get_list_entries()
        print(f"   Found {len(existing_in_list)} companies already in list")
        print()
        
        results = {
            "total": len(companies),
            "added": 0,
            "existing": 0,
            "failed": 0,
            "companies_added": []
        }
        
        for i, company in enumerate(companies, 1):
            name = company["name"]
            success, status, record_id = self.sync_company(company, existing_in_list)
            
            if success:
                if status == "already_in_list":
                    results["existing"] += 1
                    print(f"   [{i}/{len(companies)}] ⏭️  {name} - already in list")
                else:
                    results["added"] += 1
                    results["companies_added"].append(name)
                    print(f"   [{i}/{len(companies)}] ✅ {name} - added")
            else:
                results["failed"] += 1
                print(f"   [{i}/{len(companies)}] ❌ {name} - {status}")
            
            time.sleep(delay)
        
        return results


def test_connection():
    """Test Attio API connection."""
    print("🔗 Testing Attio connection...")
    
    if not ATTIO_API_KEY:
        print("❌ ATTIO_API_KEY not set in .env")
        return False
    
    print(f"   API key: {ATTIO_API_KEY[:20]}...")
    
    sync = AttioCompanySync()
    response = sync._request("POST", "/objects/companies/records/query", {"limit": 1})
    
    if response is not None:
        print("✅ Attio connection successful!")
        return True
    else:
        print("❌ Attio connection failed")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sync companies to Attio")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--limit", type=int, help="Limit number of companies to sync")
    parser.add_argument("--priority", choices=["HIGH", "MEDIUM-HIGH", "MEDIUM", "all"], 
                        default="all", help="Filter by priority")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
        return
    
    if not test_connection():
        return
    
    # Filter companies by priority
    companies = COMPANIES_DATA
    if args.priority != "all":
        if args.priority == "HIGH":
            companies = [c for c in companies if c["priority"] == "HIGH"]
        elif args.priority == "MEDIUM-HIGH":
            companies = [c for c in companies if c["priority"] in ["HIGH", "MEDIUM-HIGH"]]
        elif args.priority == "MEDIUM":
            companies = [c for c in companies if c["priority"] in ["HIGH", "MEDIUM-HIGH", "MEDIUM"]]
    
    print(f"\n📊 Companies to sync: {len(companies)}")
    
    # Sync
    sync = AttioCompanySync()
    results = sync.sync_all(companies, limit=args.limit)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYNC COMPLETE")
    print("=" * 60)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Added: {results['added']}")
    print(f"   ⏭️  Already existed: {results['existing']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    if results['companies_added']:
        print(f"\n   New companies added:")
        for company in results['companies_added'][:20]:
            print(f"      • {company}")
        if len(results['companies_added']) > 20:
            print(f"      ... and {len(results['companies_added']) - 20} more")
    
    print(f"\n🔗 View in Attio: https://app.attio.com/{ATTIO_WORKSPACE_SLUG}/collection/{ATTIO_LIST_ID}")


if __name__ == "__main__":
    main()

