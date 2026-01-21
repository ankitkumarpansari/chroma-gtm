#!/usr/bin/env python3
"""
Send all existing leads to #gtm-signal Slack channel.

This is a one-time script to backfill the production channel
with all leads from Chroma.
"""

import os
import time
import chromadb
from dotenv import load_dotenv

load_dotenv(override=True)

from slack_lead_notifier import (
    SlackLeadNotifier, 
    is_hot_lead,
    should_ignore_company,
    should_ignore_large_enterprise
)
from attio_sync import AttioSync

# Initialize
slack = SlackLeadNotifier()
attio = AttioSync()

# Chroma connection
client = chromadb.CloudClient(
    api_key='ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm',
    tenant='aa8f571e-03dc-4cd8-b888-723bd00b83f0',
    database='customer'
)


def send_hiring_leads():
    """Send all job posting leads to Slack."""
    print("=" * 60)
    print("📤 SENDING JOB POSTING LEADS TO #gtm-signal")
    print("=" * 60)
    
    collection = client.get_collection('hiring_leads')
    results = collection.get(include=['metadatas'])
    leads = results.get('metadatas', [])
    
    print(f"Total in Chroma: {len(leads)}")
    
    sent = 0
    skipped_competitor = 0
    skipped_enterprise = 0
    hot_leads = 0
    
    for i, lead in enumerate(leads, 1):
        company = lead.get('company_name', 'Unknown')
        
        # Filter competitors
        if should_ignore_company(company):
            skipped_competitor += 1
            continue
        
        # Filter large enterprises
        if should_ignore_large_enterprise(company):
            skipped_enterprise += 1
            continue
        
        # Get Attio record ID for button
        attio_id = attio.find_company_record_id(company) if attio.enabled else None
        
        # Check if hot lead
        is_hot, reason = is_hot_lead(lead)
        
        if is_hot:
            slack.notify_hot_lead(lead, reason, attio_record_id=attio_id)
            hot_leads += 1
            print(f"[{i}/{len(leads)}] 🔥 {company}")
        else:
            slack.notify_new_lead(lead, attio_record_id=attio_id)
            print(f"[{i}/{len(leads)}] 🎯 {company}")
        
        sent += 1
        time.sleep(1)  # Rate limit - 1 msg/sec to avoid Slack throttling
    
    print()
    print(f"✅ Sent: {sent}")
    print(f"🔥 Hot leads: {hot_leads}")
    print(f"🚫 Skipped competitors: {skipped_competitor}")
    print(f"🏢 Skipped enterprises: {skipped_enterprise}")
    
    return sent


def send_competitor_intel():
    """Send competitor intel signals to Slack."""
    import requests
    
    print()
    print("=" * 60)
    print("📤 SENDING COMPETITOR INTEL TO #gtm-signal")
    print("=" * 60)
    
    collection = client.get_collection('customers')
    results = collection.get(include=['metadatas'])
    customers = results.get('metadatas', [])
    
    print(f"Total in Chroma: {len(customers)}")
    
    # Filter for companies with competitor signals
    webhook = os.getenv('SLACK_WEBHOOK_URL')
    sent = 0
    skipped = 0
    
    # Competitors we track
    competitors = ['pinecone', 'weaviate', 'qdrant', 'milvus']
    
    for i, customer in enumerate(customers, 1):
        company = customer.get('company_name', customer.get('name', 'Unknown'))
        
        # Skip if it's a competitor company itself
        if should_ignore_company(company):
            skipped += 1
            continue
        
        # Skip large enterprises
        if should_ignore_large_enterprise(company):
            skipped += 1
            continue
        
        # Check if they use a competitor
        tech_stack = customer.get('tech_stack', '').lower()
        vector_db = customer.get('vector_db', customer.get('vector_db_mentioned', '')).lower()
        description = customer.get('description', '').lower()
        
        competitor_used = None
        for comp in competitors:
            if comp in tech_stack or comp in vector_db or comp in description:
                competitor_used = comp.title()
                break
        
        # Only send if competitor signal found
        if not competitor_used:
            continue
        
        # Get Attio record ID
        attio_id = attio.find_company_record_id(company) if attio.enabled else None
        attio_url = f"https://app.attio.com/chromadb/companies/{attio_id}" if attio_id else None
        
        # Build competitor intel message
        website = customer.get('website', customer.get('url', ''))
        industry = customer.get('industry', 'Technology')
        
        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f'🔔 Competitor Intel: {company}',
                    'emoji': True
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*<{website}|{company}>*\n{customer.get('description', '')[:200]}"
                }
            },
            {
                'type': 'section',
                'fields': [
                    {'type': 'mrkdwn', 'text': f'*🎯 Competitor:*\n{competitor_used}'},
                    {'type': 'mrkdwn', 'text': f'*🏢 Industry:*\n{industry}'}
                ]
            }
        ]
        
        # Action buttons
        buttons = []
        if website:
            buttons.append({
                'type': 'button',
                'text': {'type': 'plain_text', 'text': '🌐 Website'},
                'url': website,
                'style': 'primary'
            })
        
        if attio_url:
            buttons.append({
                'type': 'button',
                'text': {'type': 'plain_text', 'text': '📊 View in Attio'},
                'url': attio_url
            })
        
        if buttons:
            blocks.append({
                'type': 'actions',
                'elements': buttons
            })
        
        blocks.append({'type': 'divider'})
        blocks.append({
            'type': 'context',
            'elements': [{'type': 'mrkdwn', 'text': f'🔔 Competitor Intel • {competitor_used} user detected'}]
        })
        
        requests.post(webhook, json={'blocks': blocks})
        print(f"[{sent+1}] 🔔 {company} (uses {competitor_used})")
        
        sent += 1
        time.sleep(1)  # Rate limit
        
        # Limit to avoid overwhelming Slack
        if sent >= 50:
            print(f"\n⚠️ Pausing after {sent} messages. Run again to continue.")
            break
    
    print()
    print(f"✅ Sent: {sent} competitor intel signals")
    print(f"⏭️ Skipped: {skipped}")
    
    return sent


def main():
    print("🚀 BACKFILLING #gtm-signal CHANNEL")
    print("=" * 60)
    print()
    
    if not slack.enabled:
        print("❌ Slack not configured")
        return
    
    # Send hiring leads first
    hiring_sent = send_hiring_leads()
    
    print("\n" + "=" * 60)
    print("⏳ Waiting 5 seconds before competitor intel...")
    print("=" * 60)
    time.sleep(5)
    
    # Then competitor intel
    intel_sent = send_competitor_intel()
    
    # Summary
    print()
    print("=" * 60)
    print("✅ BACKFILL COMPLETE")
    print("=" * 60)
    print(f"   Job posting leads sent: {hiring_sent}")
    print(f"   Competitor intel sent: {intel_sent}")
    print(f"   Total messages: {hiring_sent + intel_sent}")


if __name__ == "__main__":
    main()

