#!/usr/bin/env python3
"""
Sync Deep Research Pipeline Companies to HubSpot

Syncs all 200+ companies to your HubSpot Companies module.

Usage:
    python sync_companies_to_hubspot.py
    python sync_companies_to_hubspot.py --test  # Test connection only
    python sync_companies_to_hubspot.py --limit 10  # Sync first 10 only
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

# HubSpot Configuration
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")  # Private app access token
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# ============================================================
# COMPANY DATA - 200+ companies from Deep Research Pipeline
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


class HubSpotSync:
    """Sync companies to HubSpot CRM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        if not self.api_key:
            print("❌ HUBSPOT_API_KEY not set in .env")
            print("   Get your private app access token from:")
            print("   https://app.hubspot.com/private-apps/YOUR_PORTAL_ID")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request to HubSpot."""
        url = f"{HUBSPOT_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=json_data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409:
                # Conflict - company already exists
                return {"conflict": True, "response": response.json()}
            else:
                print(f"   ⚠️ API error: {response.status_code} - {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test HubSpot API connection."""
        response = self._request("GET", "/crm/v3/objects/companies?limit=1")
        return response is not None
    
    def find_company_by_domain(self, domain: str) -> Optional[dict]:
        """Search for existing company by domain."""
        response = self._request(
            "POST",
            "/crm/v3/objects/companies/search",
            {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "domain",
                        "operator": "EQ",
                        "value": domain
                    }]
                }],
                "limit": 1
            }
        )
        
        if response and response.get("results"):
            return response["results"][0]
        return None
    
    def create_company(self, company: dict) -> Optional[str]:
        """Create a new company record in HubSpot."""
        properties = {
            "name": company["name"],
            "domain": company.get("domain", ""),
            "description": f"Category: {company.get('category', 'N/A')}\nValuation: {company.get('valuation', 'N/A')}\nPriority: {company.get('priority', 'N/A')}\nSource: Deep Research Pipeline",
            "lifecyclestage": "lead"  # Set as lead initially
        }
        
        # Map priority to HubSpot lead status
        priority = company.get("priority", "MEDIUM")
        if priority == "HIGH":
            properties["hs_lead_status"] = "NEW"
        
        response = self._request(
            "POST",
            "/crm/v3/objects/companies",
            {"properties": properties}
        )
        
        if response:
            if response.get("conflict"):
                # Company already exists, try to find by domain
                existing = self.find_company_by_domain(company.get("domain", ""))
                if existing:
                    return existing.get("id")
                return None
            return response.get("id")
        return None
    
    def get_all_companies(self) -> List[str]:
        """Get all existing company domains."""
        domains = []
        after = None
        
        while True:
            endpoint = "/crm/v3/objects/companies?limit=100&properties=domain"
            if after:
                endpoint += f"&after={after}"
            
            response = self._request("GET", endpoint)
            
            if not response:
                break
            
            for company in response.get("results", []):
                domain = company.get("properties", {}).get("domain", "")
                if domain:
                    domains.append(domain.lower())
            
            # Check for pagination
            paging = response.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")
            
            if not after:
                break
        
        return domains
    
    def sync_company(self, company: dict, existing_domains: List[str]) -> tuple:
        """Sync a single company. Returns (success, status, company_id)."""
        company_name = company["name"]
        company_domain = company.get("domain", "").lower()
        
        # Check if already exists
        if company_domain and company_domain in existing_domains:
            return True, "already_exists", None
        
        # Create company
        company_id = self.create_company(company)
        
        if company_id:
            return True, "created", company_id
        else:
            return False, "create_failed", None
    
    def sync_all(self, companies: List[dict], delay: float = 0.2, limit: int = None) -> dict:
        """Sync all companies to HubSpot."""
        if not self.enabled:
            return {"error": "HubSpot not configured"}
        
        if limit:
            companies = companies[:limit]
        
        print(f"\n📤 Syncing {len(companies)} companies to HubSpot...")
        
        # Get existing companies
        print("   Fetching existing companies...")
        existing_domains = self.get_all_companies()
        print(f"   Found {len(existing_domains)} existing companies")
        
        results = {
            "total": len(companies),
            "created": 0,
            "already_exists": 0,
            "failed": 0,
            "created_companies": [],
            "failed_companies": []
        }
        
        for i, company in enumerate(companies):
            success, status, company_id = self.sync_company(company, existing_domains)
            
            if status == "created":
                results["created"] += 1
                results["created_companies"].append(company["name"])
                print(f"   [{i+1}/{len(companies)}] ✅ {company['name']} - created")
                # Add to existing list to avoid duplicates in same run
                if company.get("domain"):
                    existing_domains.append(company["domain"].lower())
            elif status == "already_exists":
                results["already_exists"] += 1
                print(f"   [{i+1}/{len(companies)}] ⏭️  {company['name']} - already exists")
            else:
                results["failed"] += 1
                results["failed_companies"].append(company["name"])
                print(f"   [{i+1}/{len(companies)}] ❌ {company['name']} - failed")
            
            time.sleep(delay)
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Sync companies to HubSpot")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--limit", type=int, help="Limit number of companies to sync")
    args = parser.parse_args()
    
    print("🔗 Testing HubSpot connection...")
    
    sync = HubSpotSync()
    
    if not sync.enabled:
        return
    
    print(f"   API key: {sync.api_key[:20]}...")
    
    if not sync.test_connection():
        print("❌ HubSpot connection failed")
        print("   Make sure your HUBSPOT_API_KEY is a valid private app access token")
        return
    
    print("✅ HubSpot connection successful!")
    
    if args.test:
        return
    
    # Deduplicate companies by domain
    seen_domains = set()
    unique_companies = []
    for company in COMPANIES_DATA:
        domain = company.get("domain", "").lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique_companies.append(company)
        elif not domain:
            unique_companies.append(company)
    
    print(f"\n📊 Companies to sync: {len(unique_companies)} (deduplicated from {len(COMPANIES_DATA)})")
    
    results = sync.sync_all(unique_companies, limit=args.limit)
    
    if "error" in results:
        print(f"\n❌ Error: {results['error']}")
        return
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SYNC COMPLETE")
    print("=" * 60)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Created: {results['created']}")
    print(f"   ⏭️  Already existed: {results['already_exists']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    if results["created_companies"]:
        print(f"\n   New companies created:")
        for name in results["created_companies"][:20]:
            print(f"      • {name}")
        if len(results["created_companies"]) > 20:
            print(f"      ... and {len(results['created_companies']) - 20} more")
    
    if results["failed_companies"]:
        print(f"\n   Failed companies:")
        for name in results["failed_companies"]:
            print(f"      • {name}")
    
    print(f"\n🔗 View in HubSpot: https://app.hubspot.com/contacts/YOUR_PORTAL_ID/objects/0-2/views/all/list")


if __name__ == "__main__":
    main()

