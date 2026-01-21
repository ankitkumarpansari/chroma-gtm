#!/usr/bin/env python3
"""
HubSpot Cohort-Based Setup for Chroma GTM

Sets up HubSpot to reflect the 4 customer cohorts:
1. Current Chroma Customers (HIGHEST PRIORITY - Q1 Revenue)
2. In-Market Companies (AI hiring signals, AI-native companies)
3. Competitor Customers (Keep warm, follow up)
4. SI Partners (Partnership program)

Usage:
    python hubspot_cohort_setup.py          # Full setup
    python hubspot_cohort_setup.py --test   # Test connection only
    python hubspot_cohort_setup.py --list   # List existing properties
"""

import os
import requests
import argparse
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

# =============================================================================
# COHORT DEFINITIONS
# =============================================================================
"""
COHORT PRIORITY (for Q1 $2M goal):

┌─────────────────────────────────────────────────────────────────────────────┐
│  COHORT 1: CURRENT CHROMA CUSTOMERS                    🔴 HIGHEST PRIORITY  │
│  - Already tried Chroma / have instances                                    │
│  - In pipeline                                                              │
│  - Fastest path to revenue                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  COHORT 2: IN-MARKET COMPANIES                         🟠 HIGH PRIORITY     │
│  - Hiring AI engineers (Applied AI, ML experts)                             │
│  - Building AI products                                                     │
│  - AI-native companies building RAG applications                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  COHORT 3: COMPETITOR CUSTOMERS                        🟡 MEDIUM PRIORITY   │
│  - Using Pinecone, Weaviate, Qdrant, Elasticsearch, etc.                   │
│  - Keep warm, follow up regularly                                           │
│  - Longer sales cycle                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  COHORT 4: SI PARTNERS                                 🟢 STRATEGIC         │
│  - Implementing AI solutions for their customers                            │
│  - Partnership program                                                      │
│  - Multiplier effect on revenue                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""

# =============================================================================
# PROPERTY GROUP DEFINITIONS
# =============================================================================

PROPERTY_GROUPS = [
    {
        "name": "chroma_cohort",
        "label": "Chroma Cohort & Segmentation",
        "displayOrder": 1,
    },
    {
        "name": "chroma_signals",
        "label": "Chroma Signals & Intent",
        "displayOrder": 2,
    },
    {
        "name": "chroma_product",
        "label": "Chroma Product Usage",
        "displayOrder": 3,
    },
    {
        "name": "chroma_competitor",
        "label": "Competitor Intelligence",
        "displayOrder": 4,
    },
    {
        "name": "chroma_partnership",
        "label": "Partnership & SI Program",
        "displayOrder": 5,
    },
]

# =============================================================================
# COMPANY PROPERTIES - COHORT FOCUSED
# =============================================================================

COMPANY_PROPERTIES = [
    # =========================================================================
    # CORE COHORT PROPERTY (MOST IMPORTANT)
    # =========================================================================
    {
        "name": "customer_cohort",
        "label": "Customer Cohort",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_cohort",
        "description": "Primary customer segment for GTM prioritization",
        "displayOrder": 1,
        "options": [
            {"label": "🔴 Cohort 1: Current Chroma Customer", "value": "cohort_1_current_customer", "displayOrder": 1},
            {"label": "🟠 Cohort 2: In-Market", "value": "cohort_2_in_market", "displayOrder": 2},
            {"label": "🟡 Cohort 3: Competitor Customer", "value": "cohort_3_competitor", "displayOrder": 3},
            {"label": "🟢 Cohort 4: SI Partner", "value": "cohort_4_si_partner", "displayOrder": 4},
            {"label": "⚪ Unassigned", "value": "unassigned", "displayOrder": 5},
        ]
    },
    {
        "name": "cohort_priority_score",
        "label": "Cohort Priority Score",
        "type": "number",
        "fieldType": "number",
        "groupName": "chroma_cohort",
        "description": "Calculated priority score (100 = highest, 0 = lowest)",
        "displayOrder": 2,
    },
    {
        "name": "q1_revenue_potential",
        "label": "Q1 Revenue Potential",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_cohort",
        "description": "Likelihood to close in Q1 2026",
        "displayOrder": 3,
        "options": [
            {"label": "High - Likely Q1 Close", "value": "high", "displayOrder": 1},
            {"label": "Medium - Possible Q1", "value": "medium", "displayOrder": 2},
            {"label": "Low - Q2+ Timeline", "value": "low", "displayOrder": 3},
        ]
    },
    
    # =========================================================================
    # COHORT 1: CURRENT CHROMA CUSTOMER PROPERTIES
    # =========================================================================
    {
        "name": "chroma_customer_status",
        "label": "Chroma Customer Status",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_product",
        "description": "Current status with Chroma Cloud",
        "displayOrder": 1,
        "options": [
            {"label": "Active Paid Customer", "value": "active_paid", "displayOrder": 1},
            {"label": "Active Free Tier", "value": "active_free", "displayOrder": 2},
            {"label": "In Trial", "value": "trial", "displayOrder": 3},
            {"label": "In Pipeline (Evaluating)", "value": "pipeline", "displayOrder": 4},
            {"label": "Dormant (Was Active)", "value": "dormant", "displayOrder": 5},
            {"label": "Churned", "value": "churned", "displayOrder": 6},
            {"label": "OSS Only", "value": "oss_only", "displayOrder": 7},
            {"label": "Never Used", "value": "never_used", "displayOrder": 8},
        ]
    },
    {
        "name": "chroma_cloud_mrr",
        "label": "Chroma Cloud MRR",
        "type": "number",
        "fieldType": "number",
        "groupName": "chroma_product",
        "description": "Current monthly recurring revenue from this account",
        "displayOrder": 2,
    },
    {
        "name": "chroma_expansion_potential",
        "label": "Expansion Potential",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_product",
        "description": "Potential for upsell/expansion",
        "displayOrder": 3,
        "options": [
            {"label": "High - Ready to Expand", "value": "high", "displayOrder": 1},
            {"label": "Medium - Some Potential", "value": "medium", "displayOrder": 2},
            {"label": "Low - Maxed Out", "value": "low", "displayOrder": 3},
        ]
    },
    {
        "name": "chroma_instances",
        "label": "Chroma Instances",
        "type": "number",
        "fieldType": "number",
        "groupName": "chroma_product",
        "description": "Number of Chroma instances/collections",
        "displayOrder": 4,
    },
    {
        "name": "chroma_usage_tier",
        "label": "Usage Tier",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_product",
        "description": "Current usage level",
        "displayOrder": 5,
        "options": [
            {"label": "Enterprise (High Volume)", "value": "enterprise", "displayOrder": 1},
            {"label": "Growth", "value": "growth", "displayOrder": 2},
            {"label": "Starter", "value": "starter", "displayOrder": 3},
            {"label": "Free/Trial", "value": "free", "displayOrder": 4},
        ]
    },
    {
        "name": "pipeline_stage",
        "label": "Pipeline Stage",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_product",
        "description": "Current stage in sales pipeline",
        "displayOrder": 6,
        "options": [
            {"label": "Awareness", "value": "awareness", "displayOrder": 1},
            {"label": "Interest/Evaluating", "value": "evaluating", "displayOrder": 2},
            {"label": "Demo Scheduled", "value": "demo_scheduled", "displayOrder": 3},
            {"label": "POC/Technical Eval", "value": "poc", "displayOrder": 4},
            {"label": "Proposal Sent", "value": "proposal", "displayOrder": 5},
            {"label": "Negotiation", "value": "negotiation", "displayOrder": 6},
            {"label": "Closed Won", "value": "closed_won", "displayOrder": 7},
            {"label": "Closed Lost", "value": "closed_lost", "displayOrder": 8},
        ]
    },
    
    # =========================================================================
    # COHORT 2: IN-MARKET SIGNALS
    # =========================================================================
    {
        "name": "in_market_signals",
        "label": "In-Market Signals",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "chroma_signals",
        "description": "What signals indicate they are in-market",
        "displayOrder": 1,
        "options": [
            {"label": "Hiring AI Engineers", "value": "hiring_ai_engineers", "displayOrder": 1},
            {"label": "Hiring Applied AI Engineers", "value": "hiring_applied_ai", "displayOrder": 2},
            {"label": "Hiring ML Engineers", "value": "hiring_ml", "displayOrder": 3},
            {"label": "Building AI Products", "value": "building_ai_products", "displayOrder": 4},
            {"label": "AI-Native Company", "value": "ai_native", "displayOrder": 5},
            {"label": "Building RAG Application", "value": "building_rag", "displayOrder": 6},
            {"label": "Vector DB in Job Posts", "value": "vector_db_jobs", "displayOrder": 7},
            {"label": "LLM/GenAI in Job Posts", "value": "llm_jobs", "displayOrder": 8},
        ]
    },
    {
        "name": "ai_hiring_status",
        "label": "AI Hiring Status",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_signals",
        "description": "Current AI hiring activity",
        "displayOrder": 2,
        "options": [
            {"label": "Actively Hiring (5+ AI roles)", "value": "actively_hiring_high", "displayOrder": 1},
            {"label": "Hiring (1-4 AI roles)", "value": "hiring", "displayOrder": 2},
            {"label": "Recently Hired", "value": "recently_hired", "displayOrder": 3},
            {"label": "Job Posts Detected", "value": "jobs_detected", "displayOrder": 4},
            {"label": "No AI Hiring Signal", "value": "no_signal", "displayOrder": 5},
        ]
    },
    {
        "name": "ai_job_count",
        "label": "AI Job Count",
        "type": "number",
        "fieldType": "number",
        "groupName": "chroma_signals",
        "description": "Number of AI-related job postings",
        "displayOrder": 3,
    },
    {
        "name": "company_type",
        "label": "Company Type",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_signals",
        "description": "Type of company",
        "displayOrder": 4,
        "options": [
            {"label": "AI-Native Startup", "value": "ai_native_startup", "displayOrder": 1},
            {"label": "Tech Company (Adding AI)", "value": "tech_adding_ai", "displayOrder": 2},
            {"label": "Enterprise (AI Transformation)", "value": "enterprise_ai", "displayOrder": 3},
            {"label": "Traditional (Exploring AI)", "value": "traditional", "displayOrder": 4},
            {"label": "SI/Agency", "value": "si_agency", "displayOrder": 5},
        ]
    },
    {
        "name": "use_case_detected",
        "label": "Use Case Detected",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "chroma_signals",
        "description": "AI use cases detected from signals",
        "displayOrder": 5,
        "options": [
            {"label": "RAG / Retrieval", "value": "rag", "displayOrder": 1},
            {"label": "AI Agent / Copilot", "value": "agent", "displayOrder": 2},
            {"label": "Semantic Search", "value": "search", "displayOrder": 3},
            {"label": "Document Analysis", "value": "doc_analysis", "displayOrder": 4},
            {"label": "Chatbot", "value": "chatbot", "displayOrder": 5},
            {"label": "Code Search", "value": "code_search", "displayOrder": 6},
            {"label": "Recommendation", "value": "recommendation", "displayOrder": 7},
        ]
    },
    {
        "name": "signal_source",
        "label": "Signal Source",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "chroma_signals",
        "description": "Where we detected the signal",
        "displayOrder": 6,
        "options": [
            {"label": "Sumble (Job Data)", "value": "sumble", "displayOrder": 1},
            {"label": "Reo.dev (GitHub/OSS)", "value": "reodev", "displayOrder": 2},
            {"label": "LinkedIn", "value": "linkedin", "displayOrder": 3},
            {"label": "Factors.ai (Web)", "value": "factors", "displayOrder": 4},
            {"label": "Conference", "value": "conference", "displayOrder": 5},
            {"label": "Inbound (Website)", "value": "inbound", "displayOrder": 6},
            {"label": "Referral", "value": "referral", "displayOrder": 7},
        ]
    },
    {
        "name": "signal_strength",
        "label": "Signal Strength",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_signals",
        "description": "Overall strength of buying signals",
        "displayOrder": 7,
        "options": [
            {"label": "🔥 Very Strong (Multiple Signals)", "value": "very_strong", "displayOrder": 1},
            {"label": "Strong (Clear Intent)", "value": "strong", "displayOrder": 2},
            {"label": "Medium (Some Signals)", "value": "medium", "displayOrder": 3},
            {"label": "Weak (Limited Data)", "value": "weak", "displayOrder": 4},
        ]
    },
    
    # =========================================================================
    # COHORT 3: COMPETITOR CUSTOMER PROPERTIES
    # =========================================================================
    {
        "name": "current_vector_db",
        "label": "Current Vector DB",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "chroma_competitor",
        "description": "Vector database(s) currently in use",
        "displayOrder": 1,
        "options": [
            {"label": "Pinecone", "value": "pinecone", "displayOrder": 1},
            {"label": "Weaviate", "value": "weaviate", "displayOrder": 2},
            {"label": "Qdrant", "value": "qdrant", "displayOrder": 3},
            {"label": "Milvus", "value": "milvus", "displayOrder": 4},
            {"label": "Vespa", "value": "vespa", "displayOrder": 5},
            {"label": "Elasticsearch", "value": "elasticsearch", "displayOrder": 6},
            {"label": "OpenSearch", "value": "opensearch", "displayOrder": 7},
            {"label": "PGVector", "value": "pgvector", "displayOrder": 8},
            {"label": "MongoDB Atlas", "value": "mongodb", "displayOrder": 9},
            {"label": "Redis", "value": "redis", "displayOrder": 10},
            {"label": "Supabase", "value": "supabase", "displayOrder": 11},
            {"label": "None/Unknown", "value": "none", "displayOrder": 12},
        ]
    },
    {
        "name": "competitor_source_channel",
        "label": "Competitor Source Channel",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_competitor",
        "description": "How we identified competitor usage",
        "displayOrder": 2,
        "options": [
            {"label": "YouTube Video", "value": "youtube", "displayOrder": 1},
            {"label": "Case Study", "value": "case_study", "displayOrder": 2},
            {"label": "Job Posting", "value": "job_posting", "displayOrder": 3},
            {"label": "GitHub", "value": "github", "displayOrder": 4},
            {"label": "Direct Conversation", "value": "conversation", "displayOrder": 5},
            {"label": "Tech Stack Tool", "value": "tech_stack", "displayOrder": 6},
            {"label": "Conference", "value": "conference", "displayOrder": 7},
        ]
    },
    {
        "name": "competitor_pain_points",
        "label": "Competitor Pain Points",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "chroma_competitor",
        "description": "Known pain points with current solution",
        "displayOrder": 3,
        "options": [
            {"label": "Cost Too High", "value": "cost", "displayOrder": 1},
            {"label": "Performance Issues", "value": "performance", "displayOrder": 2},
            {"label": "Accuracy Problems", "value": "accuracy", "displayOrder": 3},
            {"label": "Scaling Challenges", "value": "scaling", "displayOrder": 4},
            {"label": "Operational Burden", "value": "ops_burden", "displayOrder": 5},
            {"label": "Missing Features", "value": "missing_features", "displayOrder": 6},
            {"label": "Vendor Lock-in", "value": "lock_in", "displayOrder": 7},
            {"label": "Unknown", "value": "unknown", "displayOrder": 8},
        ]
    },
    {
        "name": "competitor_relationship_status",
        "label": "Competitor Relationship Status",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_competitor",
        "description": "Current status with competitor",
        "displayOrder": 4,
        "options": [
            {"label": "Actively Evaluating Alternatives", "value": "evaluating", "displayOrder": 1},
            {"label": "Open to Conversation", "value": "open", "displayOrder": 2},
            {"label": "Satisfied (Keep Warm)", "value": "satisfied", "displayOrder": 3},
            {"label": "Locked In (Long Contract)", "value": "locked_in", "displayOrder": 4},
            {"label": "Unknown", "value": "unknown", "displayOrder": 5},
        ]
    },
    {
        "name": "displacement_play",
        "label": "Displacement Play",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_competitor",
        "description": "Which sales play to use",
        "displayOrder": 5,
        "options": [
            {"label": "Elastic Displacement (2x faster, 10x cheaper)", "value": "elastic_displacement", "displayOrder": 1},
            {"label": "Pinecone Migration", "value": "pinecone_migration", "displayOrder": 2},
            {"label": "Open Source Upgrade", "value": "oss_upgrade", "displayOrder": 3},
            {"label": "Cost Reduction", "value": "cost_reduction", "displayOrder": 4},
            {"label": "Performance Improvement", "value": "performance", "displayOrder": 5},
        ]
    },
    {
        "name": "follow_up_cadence",
        "label": "Follow-up Cadence",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_competitor",
        "description": "How often to follow up",
        "displayOrder": 6,
        "options": [
            {"label": "Weekly", "value": "weekly", "displayOrder": 1},
            {"label": "Bi-weekly", "value": "biweekly", "displayOrder": 2},
            {"label": "Monthly", "value": "monthly", "displayOrder": 3},
            {"label": "Quarterly", "value": "quarterly", "displayOrder": 4},
        ]
    },
    {
        "name": "next_follow_up_date",
        "label": "Next Follow-up Date",
        "type": "date",
        "fieldType": "date",
        "groupName": "chroma_competitor",
        "description": "When to follow up next",
        "displayOrder": 7,
    },
    
    # =========================================================================
    # COHORT 4: SI PARTNER PROPERTIES
    # =========================================================================
    {
        "name": "si_partner_status",
        "label": "SI Partner Status",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_partnership",
        "description": "Status in SI partnership program",
        "displayOrder": 1,
        "options": [
            {"label": "Active Partner (Signed)", "value": "active_signed", "displayOrder": 1},
            {"label": "Implementing (In Progress)", "value": "implementing", "displayOrder": 2},
            {"label": "Signed Up (Not Active)", "value": "signed_up", "displayOrder": 3},
            {"label": "In Discussion", "value": "in_discussion", "displayOrder": 4},
            {"label": "Prospect", "value": "prospect", "displayOrder": 5},
            {"label": "Not a Partner", "value": "not_partner", "displayOrder": 6},
        ]
    },
    {
        "name": "si_partner_tier",
        "label": "SI Partner Tier",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_partnership",
        "description": "Partnership tier level",
        "displayOrder": 2,
        "options": [
            {"label": "Platinum", "value": "platinum", "displayOrder": 1},
            {"label": "Gold", "value": "gold", "displayOrder": 2},
            {"label": "Silver", "value": "silver", "displayOrder": 3},
            {"label": "Bronze", "value": "bronze", "displayOrder": 4},
            {"label": "Untiered", "value": "untiered", "displayOrder": 5},
        ]
    },
    {
        "name": "si_customer_count",
        "label": "SI Customer Count",
        "type": "number",
        "fieldType": "number",
        "groupName": "chroma_partnership",
        "description": "Number of customers they've implemented Chroma for",
        "displayOrder": 3,
    },
    {
        "name": "si_revenue_potential",
        "label": "SI Revenue Potential",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_partnership",
        "description": "Potential revenue from this SI's customers",
        "displayOrder": 4,
        "options": [
            {"label": "High ($100K+/year)", "value": "high", "displayOrder": 1},
            {"label": "Medium ($25K-100K/year)", "value": "medium", "displayOrder": 2},
            {"label": "Low (<$25K/year)", "value": "low", "displayOrder": 3},
            {"label": "Unknown", "value": "unknown", "displayOrder": 4},
        ]
    },
    {
        "name": "si_specialization",
        "label": "SI Specialization",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "chroma_partnership",
        "description": "Areas of specialization",
        "displayOrder": 5,
        "options": [
            {"label": "Healthcare AI", "value": "healthcare", "displayOrder": 1},
            {"label": "Financial Services", "value": "financial", "displayOrder": 2},
            {"label": "Legal Tech", "value": "legal", "displayOrder": 3},
            {"label": "Enterprise AI", "value": "enterprise", "displayOrder": 4},
            {"label": "Startups/SMB", "value": "startups", "displayOrder": 5},
            {"label": "General AI/ML", "value": "general", "displayOrder": 6},
        ]
    },
    {
        "name": "si_company_type",
        "label": "SI Company Type",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_partnership",
        "description": "Type of SI/agency",
        "displayOrder": 6,
        "options": [
            {"label": "Global SI (Accenture, Deloitte, etc.)", "value": "global_si", "displayOrder": 1},
            {"label": "Regional SI", "value": "regional_si", "displayOrder": 2},
            {"label": "Boutique AI Agency", "value": "boutique_ai", "displayOrder": 3},
            {"label": "Dev Shop/Agency", "value": "dev_shop", "displayOrder": 4},
            {"label": "ISV (Embedding Chroma)", "value": "isv", "displayOrder": 5},
        ]
    },
    
    # =========================================================================
    # GENERAL TRACKING PROPERTIES
    # =========================================================================
    {
        "name": "lead_source",
        "label": "Lead Source",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "chroma_cohort",
        "description": "Original source of this lead",
        "displayOrder": 10,
        "options": [
            {"label": "Chroma Signal Database", "value": "chroma_signal"},
            {"label": "Competitor Research", "value": "competitor_research"},
            {"label": "LinkedIn Sales Nav", "value": "linkedin"},
            {"label": "Inbound (Website)", "value": "inbound"},
            {"label": "Product Signup", "value": "product_signup"},
            {"label": "Conference", "value": "conference"},
            {"label": "Referral", "value": "referral"},
            {"label": "Outbound", "value": "outbound"},
            {"label": "SI Referral", "value": "si_referral"},
        ]
    },
    {
        "name": "linkedin_company_url",
        "label": "LinkedIn Company URL",
        "type": "string",
        "fieldType": "text",
        "groupName": "chroma_cohort",
        "description": "Company LinkedIn page URL",
        "displayOrder": 11,
    },
    {
        "name": "last_engagement_date",
        "label": "Last Engagement Date",
        "type": "date",
        "fieldType": "date",
        "groupName": "chroma_cohort",
        "description": "Date of last meaningful engagement",
        "displayOrder": 12,
    },
    {
        "name": "engagement_notes",
        "label": "Engagement Notes",
        "type": "string",
        "fieldType": "textarea",
        "groupName": "chroma_cohort",
        "description": "Notes on recent engagement",
        "displayOrder": 13,
    },
]

# =============================================================================
# CONTACT PROPERTIES
# =============================================================================

CONTACT_PROPERTIES = [
    {
        "name": "contact_cohort_role",
        "label": "Role in Cohort",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "contactinformation",
        "description": "This contact's role in the account",
        "options": [
            {"label": "Champion", "value": "champion"},
            {"label": "Decision Maker", "value": "decision_maker"},
            {"label": "Technical Evaluator", "value": "technical_evaluator"},
            {"label": "End User", "value": "end_user"},
            {"label": "Influencer", "value": "influencer"},
            {"label": "Blocker", "value": "blocker"},
        ]
    },
    {
        "name": "developer_persona",
        "label": "Developer Persona",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "contactinformation",
        "description": "Type of developer/technical role",
        "options": [
            {"label": "AI/ML Engineer", "value": "ai_ml_engineer"},
            {"label": "Applied AI Engineer", "value": "applied_ai"},
            {"label": "Backend Engineer", "value": "backend"},
            {"label": "Full Stack", "value": "fullstack"},
            {"label": "Data Engineer", "value": "data_engineer"},
            {"label": "Platform/DevOps", "value": "platform"},
            {"label": "Engineering Manager", "value": "eng_manager"},
            {"label": "CTO/VP Eng", "value": "cto_vp"},
            {"label": "Product", "value": "product"},
            {"label": "Non-Technical", "value": "non_technical"},
        ]
    },
    {
        "name": "github_url",
        "label": "GitHub URL",
        "type": "string",
        "fieldType": "text",
        "groupName": "contactinformation",
        "description": "GitHub profile URL"
    },
    {
        "name": "chroma_interaction_history",
        "label": "Chroma Interaction History",
        "type": "enumeration",
        "fieldType": "checkbox",
        "groupName": "contactinformation",
        "description": "How they've interacted with Chroma",
        "options": [
            {"label": "Signed up for Cloud", "value": "cloud_signup"},
            {"label": "Attended Demo", "value": "demo"},
            {"label": "Downloaded OSS", "value": "oss"},
            {"label": "Starred GitHub", "value": "github_star"},
            {"label": "Attended Webinar", "value": "webinar"},
            {"label": "Met at Conference", "value": "conference"},
            {"label": "Responded to Outreach", "value": "outreach"},
        ]
    },
]

# =============================================================================
# DEAL PROPERTIES
# =============================================================================

DEAL_PROPERTIES = [
    {
        "name": "deal_cohort",
        "label": "Deal Cohort",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "dealinformation",
        "description": "Which cohort this deal came from",
        "options": [
            {"label": "Cohort 1: Current Customer", "value": "cohort_1"},
            {"label": "Cohort 2: In-Market", "value": "cohort_2"},
            {"label": "Cohort 3: Competitor", "value": "cohort_3"},
            {"label": "Cohort 4: SI Partner", "value": "cohort_4"},
        ]
    },
    {
        "name": "deal_type",
        "label": "Deal Type",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "dealinformation",
        "options": [
            {"label": "New Business", "value": "new_business"},
            {"label": "Expansion", "value": "expansion"},
            {"label": "Competitor Displacement", "value": "displacement"},
            {"label": "SI/OEM", "value": "si_oem"},
        ]
    },
    {
        "name": "primary_use_case",
        "label": "Primary Use Case",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "dealinformation",
        "options": [
            {"label": "RAG", "value": "rag"},
            {"label": "AI Agent", "value": "agent"},
            {"label": "Semantic Search", "value": "search"},
            {"label": "Document Analysis", "value": "doc_analysis"},
            {"label": "Chatbot/Copilot", "value": "chatbot"},
            {"label": "Multiple", "value": "multiple"},
        ]
    },
    {
        "name": "competitor_displaced",
        "label": "Competitor Displaced",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "dealinformation",
        "options": [
            {"label": "Pinecone", "value": "pinecone"},
            {"label": "Weaviate", "value": "weaviate"},
            {"label": "Qdrant", "value": "qdrant"},
            {"label": "Elasticsearch", "value": "elasticsearch"},
            {"label": "PGVector", "value": "pgvector"},
            {"label": "None (Greenfield)", "value": "none"},
        ]
    },
    {
        "name": "q1_2026_close",
        "label": "Q1 2026 Close",
        "type": "enumeration",
        "fieldType": "booleancheckbox",
        "groupName": "dealinformation",
        "description": "Expected to close in Q1 2026",
        "options": [
            {"label": "Yes", "value": "true"},
            {"label": "No", "value": "false"},
        ]
    },
]


# =============================================================================
# HubSpot API Client
# =============================================================================

class HubSpotCohortSetup:
    """Set up HubSpot for cohort-based GTM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or HUBSPOT_API_KEY
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("❌ HUBSPOT_API_KEY not set in .env")
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _request(self, method: str, endpoint: str, json_data: dict = None) -> Optional[dict]:
        """Make API request."""
        if not self.enabled:
            return None
            
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
                return {"exists": True}
            else:
                return {"error": response.status_code, "message": response.text[:300]}
                
        except Exception as e:
            return {"error": str(e)}
    
    def test_connection(self) -> bool:
        """Test API connection."""
        response = self._request("GET", "/crm/v3/properties/companies")
        return response is not None and "error" not in response
    
    def create_property_group(self, object_type: str, group: dict) -> tuple:
        """Create a property group."""
        endpoint = f"/crm/v3/properties/{object_type}/groups"
        response = self._request("POST", endpoint, group)
        
        if response is None:
            return False, "Request failed"
        elif response.get("exists"):
            return True, "Already exists"
        elif "error" in response:
            return False, f"Error: {response.get('message', response.get('error'))}"
        else:
            return True, "Created"
    
    def create_property(self, object_type: str, property_def: dict) -> tuple:
        """Create a custom property."""
        endpoint = f"/crm/v3/properties/{object_type}"
        response = self._request("POST", endpoint, property_def)
        
        if response is None:
            return False, "Request failed"
        elif response.get("exists"):
            return True, "Already exists"
        elif "error" in response:
            return False, f"Error: {response.get('message', response.get('error'))}"
        else:
            return True, "Created"
    
    def setup_property_groups(self) -> dict:
        """Create all property groups."""
        results = {"created": 0, "existed": 0, "failed": 0}
        
        print("\n📁 Creating Property Groups...")
        for group in PROPERTY_GROUPS:
            success, message = self.create_property_group("companies", group)
            if success:
                if "exists" in message.lower():
                    results["existed"] += 1
                    print(f"   ⏭️  {group['label']} - already exists")
                else:
                    results["created"] += 1
                    print(f"   ✅ {group['label']} - created")
            else:
                results["failed"] += 1
                print(f"   ❌ {group['label']} - {message}")
        
        return results
    
    def setup_company_properties(self) -> dict:
        """Create all company properties."""
        results = {"created": 0, "existed": 0, "failed": 0}
        
        print("\n🏢 Creating Company Properties...")
        for prop in COMPANY_PROPERTIES:
            success, message = self.create_property("companies", prop)
            if success:
                if "exists" in message.lower():
                    results["existed"] += 1
                    print(f"   ⏭️  {prop['label']} - already exists")
                else:
                    results["created"] += 1
                    print(f"   ✅ {prop['label']} - created")
            else:
                results["failed"] += 1
                print(f"   ❌ {prop['label']} - {message}")
        
        return results
    
    def setup_contact_properties(self) -> dict:
        """Create all contact properties."""
        results = {"created": 0, "existed": 0, "failed": 0}
        
        print("\n👤 Creating Contact Properties...")
        for prop in CONTACT_PROPERTIES:
            success, message = self.create_property("contacts", prop)
            if success:
                if "exists" in message.lower():
                    results["existed"] += 1
                    print(f"   ⏭️  {prop['label']} - already exists")
                else:
                    results["created"] += 1
                    print(f"   ✅ {prop['label']} - created")
            else:
                results["failed"] += 1
                print(f"   ❌ {prop['label']} - {message}")
        
        return results
    
    def setup_deal_properties(self) -> dict:
        """Create all deal properties."""
        results = {"created": 0, "existed": 0, "failed": 0}
        
        print("\n💰 Creating Deal Properties...")
        for prop in DEAL_PROPERTIES:
            success, message = self.create_property("deals", prop)
            if success:
                if "exists" in message.lower():
                    results["existed"] += 1
                    print(f"   ⏭️  {prop['label']} - already exists")
                else:
                    results["created"] += 1
                    print(f"   ✅ {prop['label']} - created")
            else:
                results["failed"] += 1
                print(f"   ❌ {prop['label']} - {message}")
        
        return results
    
    def run_full_setup(self) -> dict:
        """Run complete setup."""
        all_results = {}
        
        all_results["groups"] = self.setup_property_groups()
        all_results["companies"] = self.setup_company_properties()
        all_results["contacts"] = self.setup_contact_properties()
        all_results["deals"] = self.setup_deal_properties()
        
        return all_results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Setup HubSpot for Chroma's 4 Cohorts")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--list", action="store_true", help="List existing properties")
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎯 CHROMA HUBSPOT COHORT SETUP")
    print("=" * 70)
    print("""
    Setting up HubSpot for the 4 Customer Cohorts:
    
    🔴 COHORT 1: Current Chroma Customers (HIGHEST PRIORITY)
       → Already tried Chroma, in pipeline, fastest to revenue
    
    🟠 COHORT 2: In-Market Companies (HIGH PRIORITY)
       → Hiring AI engineers, building AI products, AI-native
    
    🟡 COHORT 3: Competitor Customers (MEDIUM PRIORITY)
       → Using competitors, keep warm, follow up
    
    🟢 COHORT 4: SI Partners (STRATEGIC)
       → Implementing AI for their customers
    """)
    
    setup = HubSpotCohortSetup()
    
    if not setup.enabled:
        return
    
    print(f"   API Key: {setup.api_key[:20]}...")
    
    # Test connection
    print("\n🔗 Testing connection...")
    if not setup.test_connection():
        print("❌ Connection failed")
        return
    print("✅ Connection successful!")
    
    if args.test:
        return
    
    # Run setup
    results = setup.run_full_setup()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SETUP COMPLETE")
    print("=" * 70)
    
    total_created = sum(r["created"] for r in results.values())
    total_existed = sum(r["existed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    
    print(f"\n   Property Groups:")
    print(f"      ✅ Created: {results['groups']['created']}")
    print(f"      ⏭️  Existed: {results['groups']['existed']}")
    print(f"      ❌ Failed: {results['groups']['failed']}")
    
    print(f"\n   Company Properties:")
    print(f"      ✅ Created: {results['companies']['created']}")
    print(f"      ⏭️  Existed: {results['companies']['existed']}")
    print(f"      ❌ Failed: {results['companies']['failed']}")
    
    print(f"\n   Contact Properties:")
    print(f"      ✅ Created: {results['contacts']['created']}")
    print(f"      ⏭️  Existed: {results['contacts']['existed']}")
    print(f"      ❌ Failed: {results['contacts']['failed']}")
    
    print(f"\n   Deal Properties:")
    print(f"      ✅ Created: {results['deals']['created']}")
    print(f"      ⏭️  Existed: {results['deals']['existed']}")
    print(f"      ❌ Failed: {results['deals']['failed']}")
    
    print(f"\n   TOTAL: {total_created} created, {total_existed} existed, {total_failed} failed")
    
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS")
    print("=" * 70)
    print("""
    1. Create Views in HubSpot:
       - "Cohort 1: Current Customers" (filter: customer_cohort = cohort_1)
       - "Cohort 2: In-Market" (filter: customer_cohort = cohort_2)
       - "Cohort 3: Competitors" (filter: customer_cohort = cohort_3)
       - "Cohort 4: SI Partners" (filter: customer_cohort = cohort_4)
    
    2. Create Lists:
       - "Q1 Revenue Targets" (q1_revenue_potential = high)
       - "High Priority This Week" (cohort_priority_score > 70)
    
    3. Set up Workflows:
       - Auto-assign cohort based on properties
       - Alert on high-priority signals
    
    4. Build Dashboard:
       - Companies by Cohort (pie chart)
       - Pipeline by Cohort (funnel)
       - Q1 Revenue Progress (goal tracker)
    """)


if __name__ == "__main__":
    main()

