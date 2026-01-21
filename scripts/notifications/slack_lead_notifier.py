#!/usr/bin/env python3
"""
Slack Lead Notifier

Sends notifications to Slack when new leads are discovered.
Integrates with FindAll queries and Chroma database.

Setup:
1. Create a Slack App at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook to your channel (#chroma-leads)
4. Set SLACK_WEBHOOK_URL in .env
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

# Slack Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Vector database companies to IGNORE (competitors, not prospects)
IGNORE_COMPANIES = {
    # Vector DB companies
    "chroma", "trychroma", "chroma ai",
    "pinecone", "pinecone systems", "pinecone.io",
    "weaviate", "weaviate.io",
    "qdrant", "qdrant.tech",
    "milvus", "zilliz",
    "turbopuffer",
    "vespa", "vespa.ai",
    "marqo",
    "vald",
    "activeloop", "deeplake",
    # Embedding/AI infrastructure companies
    "cohere", "cohere.ai",
    "voyage", "voyage ai", "voyageai",
    "jina", "jina ai",
    "nomic", "nomic ai",
    # Cloud DB with vector features
    "mongodb", "mongo",
    "redis", "redis labs",
    "elasticsearch", "elastic",
    "postgresql", "postgres",
    "supabase",
    "neon",
    "cockroachdb", "cockroach labs",
    "singlestore",
    "clickhouse",
    "rockset",
    "tigris",
}


def should_ignore_company(company_name: str) -> bool:
    """Check if company should be ignored (vector DB competitor)."""
    company_lower = company_name.lower().strip()
    return any(ignore in company_lower for ignore in IGNORE_COMPANIES)


# Large enterprise companies to IGNORE (unlikely to buy from startups)
IGNORE_LARGE_ENTERPRISES = {
    # Big Tech
    "amazon", "amazon.com", "aws", "amazon web services",
    "microsoft", "microsoft corporation", "azure",
    "google", "google llc", "alphabet", "deepmind",
    "meta", "meta platforms", "facebook",
    "apple", "apple inc",
    "oracle", "oracle corporation",
    "ibm", "international business machines",
    "salesforce", "salesforce inc",
    "adobe", "adobe inc",
    "nvidia", "nvidia corporation",
    "intel", "intel corporation",
    # Data/Cloud Giants
    "databricks", "databricks inc",
    "snowflake", "snowflake inc",
    "palantir", "palantir technologies",
    # Consulting Giants
    "accenture", "accenture plc", "accenture españa", "accenture india", "accenture services",
    "deloitte",
    "mckinsey", "mckinsey & company",
    "bcg", "boston consulting",
    "pwc", "pricewaterhousecoopers",
    "ey", "ernst & young", "ernst young",
    "kpmg",
    "tcs", "tata consultancy", "tata consultancy services",
    "infosys", "infosys ltd",
    "wipro",
    "cognizant",
    "capgemini",
    "ntt data",
    "booz allen", "booz allen hamilton",
    # Large Retailers/Consumer
    "walmart", "walmart inc",
    "target",
    "costco",
    "home depot", "the home depot",
    "kroger",
    # Large Finance
    "jpmorgan", "jp morgan", "chase",
    "goldman sachs",
    "morgan stanley",
    "bank of america",
    "wells fargo",
    "capital one",
    "citi", "citibank", "citigroup",
    "geico",
    # Large Healthcare/Pharma
    "johnson & johnson", "j&j",
    "pfizer",
    "merck",
    "eli lilly",
    "bristol-myers", "bristol myers",
    "abbvie",
    "amgen",
    "cvs", "cvs health",
    # Other Large Enterprises
    "disney", "walt disney",
    "comcast",
    "at&t", "att",
    "verizon",
    "general motors", "gm",
    "ford",
    "boeing",
    "3m",
    "ge", "general electric",
    "honeywell",
    "lockheed martin",
    "raytheon",
    "northrop grumman",
    "bosch",
    "siemens",
    "bytedance",
    "openai",
}


def should_ignore_large_enterprise(company_name: str) -> bool:
    """Check if company is a large enterprise we should ignore."""
    company_lower = company_name.lower().strip()
    return any(enterprise in company_lower for enterprise in IGNORE_LARGE_ENTERPRISES)


class SlackLeadNotifier:
    """Send lead notifications to Slack."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or SLACK_WEBHOOK_URL
        if not self.webhook_url:
            print("⚠️  SLACK_WEBHOOK_URL not set - notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_message(self, payload: dict) -> bool:
        """Send a message to Slack."""
        if not self.enabled:
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Slack error: {e}")
            return False
    
    def notify_new_lead(self, lead: dict, attio_record_id: str = None) -> bool:
        """
        Send a notification for a single new lead.
        
        Args:
            lead: Dictionary with lead info
            attio_record_id: Optional Attio record ID for "View in Attio" button
        """
        if not self.enabled:
            return False
            
        company = lead.get("company_name", "Unknown Company")
        website = lead.get("website", "")
        description = lead.get("description", "")[:200]
        vector_db = lead.get("vector_db_mentioned", "")
        job_titles = lead.get("job_titles", "")
        industry = lead.get("industry", "")
        funding = lead.get("funding_stage", "")
        hq = lead.get("headquarters", "")
        job_urls = lead.get("job_posting_urls", "")
        query_source = lead.get("query_name", lead.get("query_source", ""))
        
        # Build fields for Slack block
        fields = []
        
        if vector_db:
            fields.append({
                "type": "mrkdwn",
                "text": f"*🗄️ Vector DB:*\n{vector_db[:50]}"
            })
        
        if job_titles:
            fields.append({
                "type": "mrkdwn",
                "text": f"*💼 Hiring:*\n{job_titles[:50]}"
            })
        
        if industry:
            fields.append({
                "type": "mrkdwn",
                "text": f"*🏢 Industry:*\n{industry}"
            })
        
        if funding:
            fields.append({
                "type": "mrkdwn",
                "text": f"*💰 Funding:*\n{funding}"
            })
        
        if hq:
            fields.append({
                "type": "mrkdwn",
                "text": f"*📍 Location:*\n{hq}"
            })
        
        if query_source:
            fields.append({
                "type": "mrkdwn",
                "text": f"*🔍 Source:*\n{query_source}"
            })
        
        # Build Slack message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 New Lead: {company}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{website}|{company}>*\n{description}..."
                }
            }
        ]
        
        # Add fields if we have any
        if fields:
            blocks.append({
                "type": "section",
                "fields": fields[:6]
            })
        
        # Add job posting link if available
        if job_urls:
            first_url = job_urls.split(";")[0].strip()
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📄 *Job Posting:* <{first_url}|View posting>"
                }
            })
        
        # Add action buttons
        buttons = []
        if website:
            buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "🌐 Website"},
                "url": website,
                "style": "primary"
            })
        
        # LinkedIn search
        linkedin_query = company.lower().replace(' ', '-').replace(',', '').replace('.', '').replace("'", "")
        buttons.append({
            "type": "button",
            "text": {"type": "plain_text", "text": "🔍 LinkedIn"},
            "url": f"https://www.linkedin.com/company/{linkedin_query}"
        })
        
        # View in Attio button (if record_id provided)
        if attio_record_id:
            attio_url = f"https://app.attio.com/chromadb/companies/{attio_record_id}"
            buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 View in Attio"},
                "url": attio_url
            })
        
        if buttons:
            blocks.append({
                "type": "actions",
                "elements": buttons
            })
        
        # Add divider and timestamp
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"Found via Parallel FindAll • {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }]
        })
        
        return self.send_message({"blocks": blocks})
    
    def notify_batch_summary(
        self,
        new_leads: List[dict],
        query_name: str,
        total_in_db: int
    ) -> bool:
        """
        Send a summary notification for a batch of new leads.
        """
        if not self.enabled or not new_leads:
            return False
        
        # Build company list
        company_list = "\n".join([
            f"• *{lead.get('company_name', 'Unknown')}* - {lead.get('industry', lead.get('description', ''))[:40]}..."
            for lead in new_leads[:10]
        ])
        
        if len(new_leads) > 10:
            company_list += f"\n_...and {len(new_leads) - 10} more_"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 {len(new_leads)} New Leads Found!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Query:* {query_name}\n*New leads:* {len(new_leads)}\n*Total in DB:* {total_in_db}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Companies:*\n{company_list}"
                }
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"Parallel FindAll • {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }]
            }
        ]
        
        return self.send_message({"blocks": blocks})
    
    def notify_hot_lead(self, lead: dict, reason: str, attio_record_id: str = None) -> bool:
        """
        Send a HIGH PRIORITY notification for a hot lead.
        
        Use for leads mentioning Chroma or showing strong buying signals.
        
        Args:
            lead: Dictionary with lead info
            reason: Why this is a hot lead
            attio_record_id: Optional Attio record ID for "View in Attio" button
        """
        if not self.enabled:
            return False
            
        company = lead.get("company_name", "Unknown")
        website = lead.get("website", "")
        
        # Build action buttons
        action_buttons = []
        
        if website:
            action_buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "🚀 Visit Website"},
                "url": website,
                "style": "danger"
            })
        
        # View in Attio button (if record_id provided)
        if attio_record_id:
            attio_url = f"https://app.attio.com/chromadb/companies/{attio_record_id}"
            action_buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 View in Attio"},
                "url": attio_url,
                "style": "primary"
            })
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔥🔥🔥 HOT LEAD ALERT 🔥🔥🔥",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{website}|{company}>*\n\n*Why it's hot:* {reason}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Vector DB:*\n{lead.get('vector_db_mentioned', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Hiring:*\n{lead.get('job_titles', 'N/A')}"
                    }
                ]
            }
        ]
        
        if action_buttons:
            blocks.append({
                "type": "actions",
                "elements": action_buttons
            })
        
        return self.send_message({"blocks": blocks})


def is_hot_lead(lead: dict) -> tuple[bool, str]:
    """
    Check if a lead is "hot" and should trigger priority alert.
    
    Returns:
        (is_hot, reason)
    """
    company = lead.get("company_name", "").lower()
    description = lead.get("description", "").lower()
    vector_db = lead.get("vector_db_mentioned", "").lower()
    all_text = f"{company} {description} {vector_db}"
    
    # Check for Chroma mentions
    if "chroma" in all_text:
        return True, "Mentions Chroma in job posting!"
    
    # Check for switching signals
    switching_signals = ["alternative", "migration", "replacing", "switching from", "moving away"]
    for signal in switching_signals:
        if signal in all_text:
            return True, f"Shows switching intent: '{signal}'"
    
    # Check for major enterprise companies
    enterprise_signals = ["fortune 500", "enterprise", "global"]
    for signal in enterprise_signals:
        if signal in all_text:
            return True, "Enterprise company with vector DB needs"
    
    return False, ""


def test_slack_connection():
    """Test the Slack webhook connection."""
    print("=" * 60)
    print("Testing Slack Connection")
    print("=" * 60)
    
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        print("\n❌ SLACK_WEBHOOK_URL not set in .env")
        print("\n📋 Setup Instructions:")
        print("   1. Go to https://api.slack.com/apps")
        print("   2. Create New App → From scratch")
        print("   3. Name: 'Chroma Leads Bot'")
        print("   4. Go to 'Incoming Webhooks' → Turn ON")
        print("   5. Click 'Add New Webhook to Workspace'")
        print("   6. Select #chroma-leads channel")
        print("   7. Copy the webhook URL")
        print("   8. Add to .env file:")
        print("      SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../xxx")
        return False
    
    print(f"✓ Webhook URL found: {webhook[:50]}...")
    
    try:
        notifier = SlackLeadNotifier()
        
        test_payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *Chroma Lead Notifier Connected!*\n\nYou'll receive notifications here when new leads are discovered."
                    }
                },
                {
                    "type": "context",
                    "elements": [{
                        "type": "mrkdwn",
                        "text": f"Test sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }]
                }
            ]
        }
        
        if notifier.send_message(test_payload):
            print("✅ Slack connection successful!")
            print("   Check your #chroma-leads channel for the test message.")
            return True
        else:
            print("❌ Failed to send test message")
            print("   Check that the webhook URL is correct.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def send_sample_notification():
    """Send a sample lead notification for testing."""
    notifier = SlackLeadNotifier()
    
    if not notifier.enabled:
        print("Slack not configured")
        return
    
    sample_lead = {
        "company_name": "Acme AI Corp",
        "website": "https://example.com",
        "description": "Acme AI is building next-generation ML infrastructure with vector databases and RAG pipelines for enterprise customers",
        "vector_db_mentioned": "Pinecone, considering alternatives",
        "job_titles": "Senior ML Engineer, AI Platform Lead",
        "industry": "AI/ML",
        "funding_stage": "Series B",
        "headquarters": "San Francisco, CA",
        "query_name": "Pinecone Users"
    }
    
    print("\n--- Sending sample lead notification ---")
    if notifier.notify_new_lead(sample_lead):
        print("✅ Sample lead notification sent!")
    else:
        print("❌ Failed to send")


if __name__ == "__main__":
    if test_slack_connection():
        send_sample_notification()

