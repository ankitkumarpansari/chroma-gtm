#!/usr/bin/env python3
"""
Attio CRM - Universal Field Structure for Chroma
=================================================
Comprehensive, scalable field structure that works for ALL customers.
These fields are designed to scale across any B2B SaaS GTM motion.

Field Categories:
1. Company Basics - Fundamental company information
2. Technographics - Technology stack and technical details
3. Firmographics - Company demographics and characteristics
4. Intent & Engagement - Buying signals and interaction tracking
5. Relationship - Contact and relationship mapping
6. Commercial - Deal size, pricing, revenue potential
7. Product Fit - Specific to Chroma's value proposition
8. Competition - Competitive landscape
9. GTM Motion - Sales and marketing process
10. Operations - Internal tracking and workflow

Usage:
    python scripts/sync/attio_universal_fields.py setup     # Create all fields
    python scripts/sync/attio_universal_fields.py summary   # View planned structure
"""

import os
import json
import requests
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import time

load_dotenv()

class AttioUniversalFields:
    """Create universal field structure for Attio CRM."""

    def __init__(self):
        self.api_key = os.getenv("ATTIO_API_KEY")
        if not self.api_key:
            print("❌ ATTIO_API_KEY not found in .env file")
            exit(1)

        self.base_url = "https://api.attio.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Define universal field structure
        self.field_categories = self.define_universal_fields()
        self.created_fields = {}

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to Attio."""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data
            )

            if response.status_code == 429:
                print("⏳ Rate limited, waiting 5 seconds...")
                time.sleep(5)
                return self._request(method, endpoint, data)

            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            print(f"❌ API Error: {e}")
            print(f"Response: {e.response.text}")
            return {}
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {}

    def define_universal_fields(self) -> Dict[str, List[Dict]]:
        """Define comprehensive field structure for any B2B SaaS customer."""

        return {
            # ==========================================
            # 1. COMPANY BASICS
            # ==========================================
            "company_basics": [
                {
                    "api_slug": "company_domain",
                    "title": "Primary Domain",
                    "type": "domain",
                    "description": "Primary company domain (auto-enriches data)"
                },
                {
                    "api_slug": "company_linkedin_url",
                    "title": "LinkedIn URL",
                    "type": "text",
                    "description": "Company LinkedIn profile URL"
                },
                {
                    "api_slug": "company_description",
                    "title": "Company Description",
                    "type": "text",
                    "description": "What the company does in 1-2 sentences"
                },
                {
                    "api_slug": "year_founded",
                    "title": "Year Founded",
                    "type": "number",
                    "description": "Year company was founded"
                },
                {
                    "api_slug": "headquarters_location",
                    "title": "HQ Location",
                    "type": "location",
                    "description": "Company headquarters location"
                },
                {
                    "api_slug": "company_type",
                    "title": "Company Type",
                    "type": "select",
                    "description": "Type of company",
                    "config": {
                        "options": [
                            {"title": "B2B SaaS", "color": "blue"},
                            {"title": "B2C SaaS", "color": "green"},
                            {"title": "Enterprise Software", "color": "purple"},
                            {"title": "Platform/Infrastructure", "color": "orange"},
                            {"title": "Marketplace", "color": "yellow"},
                            {"title": "Agency/Consultancy", "color": "pink"},
                            {"title": "Hardware + Software", "color": "red"},
                            {"title": "Non-Profit", "color": "gray"},
                            {"title": "Government", "color": "black"}
                        ]
                    }
                }
            ],

            # ==========================================
            # 2. TECHNOGRAPHICS
            # ==========================================
            "technographics": [
                {
                    "api_slug": "tech_stack_category",
                    "title": "Tech Stack Category",
                    "type": "select",
                    "description": "Primary technology category",
                    "config": {
                        "options": [
                            {"title": "AI/ML Platform", "color": "purple"},
                            {"title": "Data Infrastructure", "color": "blue"},
                            {"title": "Developer Tools", "color": "orange"},
                            {"title": "Analytics/BI", "color": "green"},
                            {"title": "MarTech", "color": "pink"},
                            {"title": "SalesTech", "color": "red"},
                            {"title": "FinTech", "color": "yellow"},
                            {"title": "HealthTech", "color": "teal"},
                            {"title": "EdTech", "color": "indigo"},
                            {"title": "LegalTech", "color": "brown"},
                            {"title": "HR Tech", "color": "gray"},
                            {"title": "Security", "color": "black"},
                            {"title": "Other", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "uses_ai_ml",
                    "title": "Uses AI/ML",
                    "type": "checkbox",
                    "description": "Company uses AI/ML in their product"
                },
                {
                    "api_slug": "ai_ml_use_cases",
                    "title": "AI/ML Use Cases",
                    "type": "text",
                    "description": "Specific AI/ML use cases (search, recommendations, NLP, vision, etc.)"
                },
                {
                    "api_slug": "vector_db_status",
                    "title": "Vector DB Status",
                    "type": "select",
                    "description": "Current vector database usage",
                    "config": {
                        "options": [
                            {"title": "Active Chroma User", "color": "green"},
                            {"title": "Evaluating Chroma", "color": "blue"},
                            {"title": "Using Competitor", "color": "orange"},
                            {"title": "Building In-House", "color": "red"},
                            {"title": "No Vector DB", "color": "gray"},
                            {"title": "Needs Vector DB", "color": "yellow"},
                            {"title": "Unknown", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "vector_db_competitor",
                    "title": "Vector DB Competitor",
                    "type": "select",
                    "description": "Which competitor they use (if any)",
                    "config": {
                        "options": [
                            {"title": "Pinecone", "color": "blue"},
                            {"title": "Weaviate", "color": "purple"},
                            {"title": "Qdrant", "color": "orange"},
                            {"title": "Milvus", "color": "red"},
                            {"title": "Vespa", "color": "yellow"},
                            {"title": "Elasticsearch", "color": "green"},
                            {"title": "OpenSearch", "color": "teal"},
                            {"title": "pgvector", "color": "indigo"},
                            {"title": "MongoDB Atlas", "color": "green"},
                            {"title": "Redis", "color": "red"},
                            {"title": "Other", "color": "gray"},
                            {"title": "None", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "cloud_provider",
                    "title": "Cloud Provider",
                    "type": "select",
                    "description": "Primary cloud infrastructure provider",
                    "config": {
                        "options": [
                            {"title": "AWS", "color": "orange"},
                            {"title": "Google Cloud", "color": "blue"},
                            {"title": "Azure", "color": "blue"},
                            {"title": "Multi-Cloud", "color": "purple"},
                            {"title": "On-Premise", "color": "gray"},
                            {"title": "Hybrid", "color": "green"},
                            {"title": "Unknown", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "open_source_presence",
                    "title": "Open Source Presence",
                    "type": "checkbox",
                    "description": "Has open source projects"
                },
                {
                    "api_slug": "github_stars",
                    "title": "GitHub Stars",
                    "type": "number",
                    "description": "Total GitHub stars across repos"
                }
            ],

            # ==========================================
            # 3. FIRMOGRAPHICS
            # ==========================================
            "firmographics": [
                {
                    "api_slug": "employee_count",
                    "title": "Employee Count",
                    "type": "number",
                    "description": "Current number of employees"
                },
                {
                    "api_slug": "employee_range",
                    "title": "Employee Range",
                    "type": "select",
                    "description": "Employee count range",
                    "config": {
                        "options": [
                            {"title": "1-10", "color": "gray"},
                            {"title": "11-50", "color": "green"},
                            {"title": "51-200", "color": "blue"},
                            {"title": "201-500", "color": "orange"},
                            {"title": "501-1000", "color": "purple"},
                            {"title": "1001-5000", "color": "red"},
                            {"title": "5000+", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "engineering_team_size",
                    "title": "Engineering Team Size",
                    "type": "number",
                    "description": "Number of engineers/developers"
                },
                {
                    "api_slug": "annual_revenue",
                    "title": "Annual Revenue",
                    "type": "currency",
                    "description": "Annual revenue (if known)"
                },
                {
                    "api_slug": "revenue_range",
                    "title": "Revenue Range",
                    "type": "select",
                    "description": "Annual revenue range",
                    "config": {
                        "options": [
                            {"title": "< $1M", "color": "gray"},
                            {"title": "$1M - $10M", "color": "green"},
                            {"title": "$10M - $50M", "color": "blue"},
                            {"title": "$50M - $100M", "color": "orange"},
                            {"title": "$100M - $500M", "color": "purple"},
                            {"title": "$500M - $1B", "color": "red"},
                            {"title": "> $1B", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "funding_stage",
                    "title": "Funding Stage",
                    "type": "select",
                    "description": "Latest funding stage",
                    "config": {
                        "options": [
                            {"title": "Pre-Seed", "color": "gray"},
                            {"title": "Seed", "color": "green"},
                            {"title": "Series A", "color": "blue"},
                            {"title": "Series B", "color": "orange"},
                            {"title": "Series C", "color": "purple"},
                            {"title": "Series D+", "color": "red"},
                            {"title": "IPO", "color": "black"},
                            {"title": "Acquired", "color": "pink"},
                            {"title": "Bootstrapped", "color": "yellow"}
                        ]
                    }
                },
                {
                    "api_slug": "total_funding",
                    "title": "Total Funding",
                    "type": "currency",
                    "description": "Total funding raised to date"
                },
                {
                    "api_slug": "last_funding_date",
                    "title": "Last Funding Date",
                    "type": "date",
                    "description": "Date of last funding round"
                },
                {
                    "api_slug": "valuation",
                    "title": "Valuation",
                    "type": "currency",
                    "description": "Latest valuation"
                },
                {
                    "api_slug": "growth_rate",
                    "title": "Growth Rate",
                    "type": "text",
                    "description": "YoY growth rate (if known)"
                },
                {
                    "api_slug": "industry",
                    "title": "Industry",
                    "type": "select",
                    "description": "Primary industry vertical",
                    "config": {
                        "options": [
                            {"title": "Technology", "color": "blue"},
                            {"title": "Financial Services", "color": "green"},
                            {"title": "Healthcare", "color": "red"},
                            {"title": "Retail/E-commerce", "color": "orange"},
                            {"title": "Education", "color": "purple"},
                            {"title": "Media/Entertainment", "color": "pink"},
                            {"title": "Manufacturing", "color": "brown"},
                            {"title": "Real Estate", "color": "teal"},
                            {"title": "Transportation", "color": "indigo"},
                            {"title": "Energy", "color": "yellow"},
                            {"title": "Government", "color": "black"},
                            {"title": "Non-Profit", "color": "gray"},
                            {"title": "Other", "color": "gray"}
                        ]
                    }
                }
            ],

            # ==========================================
            # 4. INTENT & ENGAGEMENT
            # ==========================================
            "intent_engagement": [
                {
                    "api_slug": "buying_stage",
                    "title": "Buying Stage",
                    "type": "select",
                    "description": "Current stage in buying journey",
                    "config": {
                        "options": [
                            {"title": "Awareness", "color": "gray"},
                            {"title": "Interest", "color": "blue"},
                            {"title": "Consideration", "color": "orange"},
                            {"title": "Evaluation", "color": "purple"},
                            {"title": "Decision", "color": "green"},
                            {"title": "Closed Won", "color": "green"},
                            {"title": "Closed Lost", "color": "red"},
                            {"title": "Churned", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "engagement_score",
                    "title": "Engagement Score",
                    "type": "number",
                    "description": "Overall engagement score (0-100)"
                },
                {
                    "api_slug": "intent_signals",
                    "title": "Intent Signals",
                    "type": "text",
                    "description": "Buying intent signals observed"
                },
                {
                    "api_slug": "website_visits",
                    "title": "Website Visits",
                    "type": "number",
                    "description": "Number of website visits tracked"
                },
                {
                    "api_slug": "content_engagement",
                    "title": "Content Engagement",
                    "type": "text",
                    "description": "Content pieces engaged with"
                },
                {
                    "api_slug": "last_engagement_date",
                    "title": "Last Engagement",
                    "type": "date",
                    "description": "Date of last engagement"
                },
                {
                    "api_slug": "engagement_channel",
                    "title": "Engagement Channel",
                    "type": "select",
                    "description": "Primary engagement channel",
                    "config": {
                        "options": [
                            {"title": "Email", "color": "blue"},
                            {"title": "LinkedIn", "color": "blue"},
                            {"title": "Website", "color": "green"},
                            {"title": "Slack", "color": "purple"},
                            {"title": "Phone", "color": "orange"},
                            {"title": "In-Person", "color": "red"},
                            {"title": "Partner", "color": "yellow"},
                            {"title": "Community", "color": "pink"},
                            {"title": "None", "color": "gray"}
                        ]
                    }
                }
            ],

            # ==========================================
            # 5. RELATIONSHIP
            # ==========================================
            "relationship": [
                {
                    "api_slug": "champion_identified",
                    "title": "Champion Identified",
                    "type": "checkbox",
                    "description": "Internal champion has been identified"
                },
                {
                    "api_slug": "champion_name",
                    "title": "Champion Name",
                    "type": "text",
                    "description": "Name of internal champion"
                },
                {
                    "api_slug": "decision_maker",
                    "title": "Decision Maker",
                    "type": "text",
                    "description": "Key decision maker(s)"
                },
                {
                    "api_slug": "relationship_strength",
                    "title": "Relationship Strength",
                    "type": "select",
                    "description": "Strength of relationship",
                    "config": {
                        "options": [
                            {"title": "Strong", "color": "green"},
                            {"title": "Good", "color": "blue"},
                            {"title": "Developing", "color": "orange"},
                            {"title": "Weak", "color": "red"},
                            {"title": "None", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "stakeholder_count",
                    "title": "Stakeholder Count",
                    "type": "number",
                    "description": "Number of stakeholders engaged"
                },
                {
                    "api_slug": "executive_engagement",
                    "title": "Executive Engagement",
                    "type": "checkbox",
                    "description": "C-level or VP engaged"
                }
            ],

            # ==========================================
            # 6. COMMERCIAL
            # ==========================================
            "commercial": [
                {
                    "api_slug": "deal_size",
                    "title": "Deal Size",
                    "type": "currency",
                    "description": "Expected or actual deal size"
                },
                {
                    "api_slug": "acv",
                    "title": "ACV",
                    "type": "currency",
                    "description": "Annual Contract Value"
                },
                {
                    "api_slug": "ltv",
                    "title": "LTV",
                    "type": "currency",
                    "description": "Lifetime Value"
                },
                {
                    "api_slug": "payment_terms",
                    "title": "Payment Terms",
                    "type": "select",
                    "description": "Payment frequency",
                    "config": {
                        "options": [
                            {"title": "Monthly", "color": "green"},
                            {"title": "Quarterly", "color": "blue"},
                            {"title": "Annual", "color": "orange"},
                            {"title": "Multi-Year", "color": "purple"},
                            {"title": "Usage-Based", "color": "yellow"},
                            {"title": "Unknown", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "budget_confirmed",
                    "title": "Budget Confirmed",
                    "type": "checkbox",
                    "description": "Budget has been confirmed"
                },
                {
                    "api_slug": "procurement_process",
                    "title": "Procurement Process",
                    "type": "text",
                    "description": "Notes on procurement process"
                },
                {
                    "api_slug": "contract_start_date",
                    "title": "Contract Start Date",
                    "type": "date",
                    "description": "Contract start date"
                },
                {
                    "api_slug": "renewal_date",
                    "title": "Renewal Date",
                    "type": "date",
                    "description": "Contract renewal date"
                }
            ],

            # ==========================================
            # 7. PRODUCT FIT (Chroma Specific)
            # ==========================================
            "product_fit": [
                {
                    "api_slug": "use_case_category",
                    "title": "Use Case Category",
                    "type": "select",
                    "description": "Primary use case for vector DB",
                    "config": {
                        "options": [
                            {"title": "Semantic Search", "color": "blue"},
                            {"title": "RAG (Retrieval Augmented Generation)", "color": "purple"},
                            {"title": "Recommendation Systems", "color": "green"},
                            {"title": "Knowledge Management", "color": "orange"},
                            {"title": "Similarity Matching", "color": "yellow"},
                            {"title": "Anomaly Detection", "color": "red"},
                            {"title": "Personalization", "color": "pink"},
                            {"title": "Question Answering", "color": "teal"},
                            {"title": "Document Processing", "color": "indigo"},
                            {"title": "Other", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "data_volume_estimate",
                    "title": "Data Volume",
                    "type": "select",
                    "description": "Estimated vector data volume",
                    "config": {
                        "options": [
                            {"title": "< 100K vectors", "color": "green"},
                            {"title": "100K - 1M vectors", "color": "blue"},
                            {"title": "1M - 10M vectors", "color": "orange"},
                            {"title": "10M - 100M vectors", "color": "purple"},
                            {"title": "100M - 1B vectors", "color": "red"},
                            {"title": "> 1B vectors", "color": "black"},
                            {"title": "Unknown", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "embedding_model",
                    "title": "Embedding Model",
                    "type": "text",
                    "description": "Embedding model they use/plan to use"
                },
                {
                    "api_slug": "technical_fit_score",
                    "title": "Technical Fit Score",
                    "type": "number",
                    "description": "Technical fit score (0-100)"
                },
                {
                    "api_slug": "implementation_complexity",
                    "title": "Implementation Complexity",
                    "type": "select",
                    "description": "Expected implementation complexity",
                    "config": {
                        "options": [
                            {"title": "Simple", "color": "green"},
                            {"title": "Moderate", "color": "orange"},
                            {"title": "Complex", "color": "red"},
                            {"title": "Unknown", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "chroma_advantages",
                    "title": "Chroma Advantages",
                    "type": "text",
                    "description": "Why Chroma is a good fit"
                }
            ],

            # ==========================================
            # 8. COMPETITION
            # ==========================================
            "competition": [
                {
                    "api_slug": "competitor_mentioned",
                    "title": "Competitor Mentioned",
                    "type": "text",
                    "description": "Competitors being evaluated"
                },
                {
                    "api_slug": "competitive_position",
                    "title": "Competitive Position",
                    "type": "select",
                    "description": "Our position vs competition",
                    "config": {
                        "options": [
                            {"title": "Leading", "color": "green"},
                            {"title": "Strong", "color": "blue"},
                            {"title": "Equal", "color": "orange"},
                            {"title": "Behind", "color": "red"},
                            {"title": "Unknown", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "switching_from",
                    "title": "Switching From",
                    "type": "text",
                    "description": "Solution they're switching from"
                },
                {
                    "api_slug": "win_loss_reason",
                    "title": "Win/Loss Reason",
                    "type": "text",
                    "description": "Reason for winning or losing deal"
                }
            ],

            # ==========================================
            # 9. GTM MOTION
            # ==========================================
            "gtm_motion": [
                {
                    "api_slug": "lead_source",
                    "title": "Lead Source",
                    "type": "select",
                    "description": "Original source of lead",
                    "config": {
                        "options": [
                            {"title": "Inbound - Website", "color": "green"},
                            {"title": "Inbound - Content", "color": "blue"},
                            {"title": "Outbound - Email", "color": "orange"},
                            {"title": "Outbound - LinkedIn", "color": "blue"},
                            {"title": "Partner Referral", "color": "purple"},
                            {"title": "Customer Referral", "color": "green"},
                            {"title": "Event/Conference", "color": "pink"},
                            {"title": "Open Source Community", "color": "yellow"},
                            {"title": "Investor Intro", "color": "red"},
                            {"title": "Other", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "campaign_name",
                    "title": "Campaign Name",
                    "type": "text",
                    "description": "Marketing campaign that sourced lead"
                },
                {
                    "api_slug": "sales_owner",
                    "title": "Sales Owner",
                    "type": "actor",
                    "description": "Sales rep owner"
                },
                {
                    "api_slug": "customer_segment",
                    "title": "Customer Segment",
                    "type": "select",
                    "description": "ICP segment classification",
                    "config": {
                        "options": [
                            {"title": "Enterprise", "color": "purple"},
                            {"title": "Mid-Market", "color": "blue"},
                            {"title": "SMB", "color": "green"},
                            {"title": "Startup", "color": "orange"},
                            {"title": "Strategic", "color": "red"},
                            {"title": "Long-Tail", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "sales_stage",
                    "title": "Sales Stage",
                    "type": "select",
                    "description": "Current sales pipeline stage",
                    "config": {
                        "options": [
                            {"title": "Prospecting", "color": "gray"},
                            {"title": "Qualified", "color": "blue"},
                            {"title": "Discovery", "color": "orange"},
                            {"title": "Demo/POC", "color": "purple"},
                            {"title": "Proposal", "color": "yellow"},
                            {"title": "Negotiation", "color": "pink"},
                            {"title": "Closed Won", "color": "green"},
                            {"title": "Closed Lost", "color": "red"}
                        ]
                    }
                },
                {
                    "api_slug": "next_steps",
                    "title": "Next Steps",
                    "type": "text",
                    "description": "Next action items"
                },
                {
                    "api_slug": "blockers",
                    "title": "Blockers",
                    "type": "text",
                    "description": "Current blockers or risks"
                }
            ],

            # ==========================================
            # 10. OPERATIONS
            # ==========================================
            "operations": [
                {
                    "api_slug": "account_tier",
                    "title": "Account Tier",
                    "type": "select",
                    "description": "Account prioritization tier",
                    "config": {
                        "options": [
                            {"title": "Tier 1 - Strategic", "color": "purple"},
                            {"title": "Tier 2 - Growth", "color": "blue"},
                            {"title": "Tier 3 - Standard", "color": "green"},
                            {"title": "Tier 4 - Long-tail", "color": "orange"},
                            {"title": "Untiered", "color": "gray"}
                        ]
                    }
                },
                {
                    "api_slug": "health_score",
                    "title": "Health Score",
                    "type": "number",
                    "description": "Account health score (0-100)"
                },
                {
                    "api_slug": "risk_level",
                    "title": "Risk Level",
                    "type": "select",
                    "description": "Account risk level",
                    "config": {
                        "options": [
                            {"title": "Low", "color": "green"},
                            {"title": "Medium", "color": "orange"},
                            {"title": "High", "color": "red"},
                            {"title": "Critical", "color": "black"}
                        ]
                    }
                },
                {
                    "api_slug": "last_touch_date",
                    "title": "Last Touch Date",
                    "type": "date",
                    "description": "Date of last contact"
                },
                {
                    "api_slug": "days_since_last_touch",
                    "title": "Days Since Last Touch",
                    "type": "number",
                    "description": "Days since last interaction"
                },
                {
                    "api_slug": "data_quality_score",
                    "title": "Data Quality Score",
                    "type": "number",
                    "description": "Completeness of data (0-100)"
                },
                {
                    "api_slug": "enrichment_status",
                    "title": "Enrichment Status",
                    "type": "select",
                    "description": "Data enrichment status",
                    "config": {
                        "options": [
                            {"title": "Fully Enriched", "color": "green"},
                            {"title": "Partially Enriched", "color": "orange"},
                            {"title": "Needs Enrichment", "color": "red"},
                            {"title": "Manual Review", "color": "purple"}
                        ]
                    }
                },
                {
                    "api_slug": "tags",
                    "title": "Tags",
                    "type": "text",
                    "description": "Custom tags for filtering"
                },
                {
                    "api_slug": "internal_notes",
                    "title": "Internal Notes",
                    "type": "text",
                    "description": "Internal team notes"
                },
                {
                    "api_slug": "created_date",
                    "title": "Created Date",
                    "type": "date",
                    "description": "Date record was created"
                },
                {
                    "api_slug": "updated_date",
                    "title": "Updated Date",
                    "type": "date",
                    "description": "Last update date"
                }
            ]
        }

    def create_fields(self):
        """Create all universal fields in Attio."""
        print("\n🚀 Creating Universal Field Structure in Attio...")

        endpoint = "objects/companies/attributes"
        total_created = 0
        total_skipped = 0

        for category_name, fields in self.field_categories.items():
            print(f"\n📁 {category_name.upper().replace('_', ' ')}")
            print("=" * 50)

            for field in fields:
                print(f"  Creating: {field['title']}...", end="")

                # Check if attribute already exists
                existing = self._request("GET", endpoint)
                exists = False

                if existing and 'data' in existing:
                    for existing_attr in existing['data']:
                        if existing_attr.get('api_slug') == field['api_slug']:
                            print(f" ✓ Already exists")
                            self.created_fields[field['api_slug']] = existing_attr['id']
                            total_skipped += 1
                            exists = True
                            break

                if not exists:
                    # Build the request data
                    data = {
                        "api_slug": field["api_slug"],
                        "title": field["title"],
                        "type": field["type"],
                        "description": field.get("description", "")
                    }

                    # Add config for select fields
                    if "config" in field:
                        data["config"] = field["config"]

                    result = self._request("POST", endpoint, {"data": data})

                    if result and 'data' in result:
                        self.created_fields[field['api_slug']] = result['data']['id']
                        print(f" ✅ Created")
                        total_created += 1
                    else:
                        print(f" ❌ Failed")

                time.sleep(0.3)  # Rate limiting

        print("\n" + "=" * 60)
        print(f"📊 SUMMARY:")
        print(f"  ✅ Created: {total_created} fields")
        print(f"  ⏭️  Skipped (existing): {total_skipped} fields")
        print(f"  📋 Total fields: {total_created + total_skipped}")
        print("=" * 60)

    def display_field_structure(self):
        """Display the complete field structure."""
        print("\n" + "=" * 60)
        print("📊 UNIVERSAL FIELD STRUCTURE FOR ATTIO")
        print("=" * 60)

        total_fields = 0
        for category_name, fields in self.field_categories.items():
            print(f"\n📁 {category_name.upper().replace('_', ' ')} ({len(fields)} fields)")
            print("-" * 40)

            for field in fields:
                field_type = field['type']
                if field['type'] == 'select':
                    options_count = len(field['config']['options'])
                    field_type = f"select ({options_count} options)"

                print(f"  • {field['title']:<30} [{field_type}]")
                if field.get('description'):
                    print(f"    └─ {field['description'][:60]}...")

            total_fields += len(fields)

        print("\n" + "=" * 60)
        print(f"📈 TOTAL: {total_fields} fields across {len(self.field_categories)} categories")
        print("=" * 60)

        print("\n💡 This structure is designed to:")
        print("  1. Scale across any B2B SaaS customer")
        print("  2. Support all GTM motions (inbound, outbound, PLG)")
        print("  3. Enable advanced segmentation and scoring")
        print("  4. Track full customer lifecycle")
        print("  5. Integrate with sales, marketing, and CS tools")


def main():
    parser = argparse.ArgumentParser(description="Create universal Attio field structure")
    parser.add_argument("command",
                       choices=["setup", "summary", "test"],
                       help="Command to execute")

    args = parser.parse_args()

    setup = AttioUniversalFields()

    if args.command == "test":
        # Test connection
        endpoint = "objects/companies/records/query"
        data = {"limit": 1}
        result = setup._request("POST", endpoint, data)
        if result:
            print("✅ Connected to Attio successfully!")
        else:
            print("❌ Failed to connect to Attio")

    elif args.command == "summary":
        setup.display_field_structure()

    elif args.command == "setup":
        # Confirm before creating
        setup.display_field_structure()
        print("\n⚠️  This will create all these fields in your Attio workspace.")
        response = input("Continue? (yes/no): ")

        if response.lower() == 'yes':
            setup.create_fields()
            print("\n✅ Setup complete! Next steps:")
            print("  1. Create custom lists in Attio UI")
            print("  2. Run import scripts to populate data")
            print("  3. Set up views and pipelines")
        else:
            print("❌ Setup cancelled")


if __name__ == "__main__":
    main()