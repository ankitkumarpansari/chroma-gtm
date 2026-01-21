# 📜 Script Registry - Chroma GTM

> **Purpose**: This file documents ALL automation scripts in this project.
> **Rule**: Before creating a new script, run `python query_workspace.py "your task"`!

---

## 🔍 How to Find Scripts

Instead of reading this file, use the semantic search:

```bash
# Search for scripts by description
python query_workspace.py "sync companies to HubSpot" --type scripts

# Search all content
python query_workspace.py "LinkedIn automation"

# Show index stats
python query_workspace.py --stats
```

---

## 🔗 LinkedIn Automation (`scripts/linkedin/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `linkedin_sales_nav_automation.py` | Main Sales Navigator automation | `python scripts/linkedin/linkedin_sales_nav_automation.py` |
| `linkedin_sales_nav_playwright.py` | Playwright-based LinkedIn automation | `python scripts/linkedin/linkedin_sales_nav_playwright.py` |
| `linkedin_profile_agent.py` | AI agent for LinkedIn profile analysis | `python scripts/linkedin/linkedin_profile_agent.py` |
| `find_linkedin_profiles.py` | Find LinkedIn profiles for leads | `python scripts/linkedin/find_linkedin_profiles.py` |
| `parallel_linkedin_search.py` | Parallel LinkedIn search (faster) | `python scripts/linkedin/parallel_linkedin_search.py` |
| `parallel_linkedin_individual.py` | Individual parallel searches | `python scripts/linkedin/parallel_linkedin_individual.py` |
| `parallel_linkedin_full_search.py` | Full parallel search | `python scripts/linkedin/parallel_linkedin_full_search.py` |
| `linkedin_automation_final.py` | Final working automation version | `python scripts/linkedin/linkedin_automation_final.py` |

**Chrome Extension**: `linkedin-sales-nav-extension/` - Browser extension for Sales Nav

---

## 💼 CRM Sync - HubSpot (`scripts/hubspot/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `sync_companies_to_hubspot.py` | Sync companies to HubSpot | `python scripts/hubspot/sync_companies_to_hubspot.py` |
| `sync_chroma_signal_to_hubspot.py` | Sync Chroma Signal data | `python scripts/hubspot/sync_chroma_signal_to_hubspot.py` |
| `hubspot_master_sync.py` | Master HubSpot sync orchestration | `python scripts/hubspot/hubspot_master_sync.py` |
| `hubspot_setup_properties.py` | Set up custom HubSpot properties | `python scripts/hubspot/hubspot_setup_properties.py` |
| `hubspot_cohort_setup.py` | Set up cohort-based properties | `python scripts/hubspot/hubspot_cohort_setup.py` |
| `hubspot_import_cohorts.py` | Import companies by cohort | `python scripts/hubspot/hubspot_import_cohorts.py` |
| `hubspot_sync_contacts.py` | Sync contacts to HubSpot | `python scripts/hubspot/hubspot_sync_contacts.py` |
| `hubspot_delete_all_companies.py` | Delete all companies (careful!) | `python scripts/hubspot/hubspot_delete_all_companies.py` |
| `create_vector_db_property.py` | Create vector DB tracking property | `python scripts/hubspot/create_vector_db_property.py` |

---

## 🔍 Lead Discovery (`scripts/discovery/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `chroma_signal_list.py` | Main signal discovery | `python scripts/discovery/chroma_signal_list.py` |
| `findall_vector_db_leads.py` | Find companies using vector DBs | `python scripts/discovery/findall_vector_db_leads.py` |
| `findall_expanded_leads.py` | Expand lead lists with enrichment | `python scripts/discovery/findall_expanded_leads.py` |
| `run_lead_discovery.py` | Automated daily pipeline | `python scripts/discovery/run_lead_discovery.py` |
| `parallel_findall.py` | Parallel lead discovery | `python scripts/discovery/parallel_findall.py` |
| `ai_engineer_speakers.py` | Find AI conference speakers | `python scripts/discovery/ai_engineer_speakers.py` |

---

## 🎬 Customer Extraction (`scripts/extraction/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `extract_customers_llm.py` | LLM-based customer extraction | `python scripts/extraction/extract_customers_llm.py --provider openai` |
| `extract_customers_improved.py` | Improved extraction logic | `python scripts/extraction/extract_customers_improved.py` |
| `extract_customers.py` | Base extraction script | `python scripts/extraction/extract_customers.py` |

---

## 📈 Data Enrichment (`scripts/enrichment/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `enrich_competitor_customers.py` | Enrich competitor customer data | `python scripts/enrichment/enrich_competitor_customers.py` |
| `enrich_isaac_zooxsmart_to_hubspot.py` | Enrich specific account | `python scripts/enrichment/enrich_isaac_zooxsmart_to_hubspot.py` |
| `enrich_ping_identity_to_hubspot.py` | Enrich specific account | `python scripts/enrichment/enrich_ping_identity_to_hubspot.py` |
| `add_company_urls.py` | Add URLs to company data | `python scripts/enrichment/add_company_urls.py` |
| `add_claude_research.py` | Add Claude research data | `python scripts/enrichment/add_claude_research.py` |
| `add_mercor.py` | Add Mercor data | `python scripts/enrichment/add_mercor.py` |
| `deduplicate_companies.py` | Deduplicate company lists | `python scripts/enrichment/deduplicate_companies.py` |

---

## 📱 Slack Notifications (`scripts/notifications/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `slack_lead_notifier.py` | Send lead alerts to Slack | `python scripts/notifications/slack_lead_notifier.py` |
| `send_all_to_slack.py` | Batch send to Slack | `python scripts/notifications/send_all_to_slack.py` |

---

## 🔄 External Sync (`scripts/sync/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `google_sheets_sync.py` | Sync data to Google Sheets | `python scripts/sync/google_sheets_sync.py` |
| `google_sheets_events_sync.py` | Sync events calendar to Sheets | `python scripts/sync/google_sheets_events_sync.py` |
| `sync_companies_to_attio.py` | Sync to Attio CRM | `python scripts/sync/sync_companies_to_attio.py` |
| `attio_sync.py` | Attio sync utilities | `python scripts/sync/attio_sync.py` |
| `competitor_intel_sync.py` | Sync competitor intelligence | `python scripts/sync/competitor_intel_sync.py` |

---

## ✉️ Email/Gmail (`scripts/email/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `gmail_client.py` | Gmail API client | Import as module |
| `gmail_draft.py` | Create email drafts | `python scripts/email/gmail_draft.py` |
| `gmail_sync.py` | Sync Gmail | `python scripts/email/gmail_sync.py` |
| `gmail_labels.py` | Manage Gmail labels | `python scripts/email/gmail_labels.py` |
| `draft_outreach_email.py` | Draft outreach emails | `python scripts/email/draft_outreach_email.py` |

---

## 📊 Visualization (`scripts/visualization/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `chroma_viewer.py` | Streamlit app for viewing data | `streamlit run scripts/visualization/chroma_viewer.py` |
| `diagram_generator.py` | Generate strategy diagrams | `python scripts/visualization/diagram_generator.py` |
| `generate_chroma_seo_strategy.py` | Generate SEO strategy diagrams | `python scripts/visualization/generate_chroma_seo_strategy.py` |
| `export_for_looker.py` | Export data for Looker | `python scripts/visualization/export_for_looker.py` |

---

## 🗄️ Chroma DB Operations (`scripts/chroma/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `save_to_chroma.py` | Save data to Chroma | `python scripts/chroma/save_to_chroma.py` |
| `save_hiring_leads_to_chroma.py` | Save hiring leads to Chroma | `python scripts/chroma/save_hiring_leads_to_chroma.py` |
| `update_chroma_data.py` | Update Chroma data | `python scripts/chroma/update_chroma_data.py` |
| `chroma_customer_db.py` | Customer database management | `python scripts/chroma/chroma_customer_db.py` |

---

## 🌐 Browser Automation (`scripts/browser/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `take_screenshot.py` | Take browser screenshots | `python scripts/browser/take_screenshot.py` |
| `capture_state.py` | Capture browser state | `python scripts/browser/capture_state.py` |
| `watch_browser.py` | Watch browser activity | `python scripts/browser/watch_browser.py` |
| `interactive_test.py` | Interactive browser testing | `python scripts/browser/interactive_test.py` |

---

## 🧪 Tests (`tests/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_accuracy.py` | Test extraction accuracy | `python tests/test_accuracy.py` |
| `test_one.py` | Test single item | `python tests/test_one.py` |
| `test_single_company.py` | Test single company | `python tests/test_single_company.py` |
| `test_parallel_api.py` | Test parallel API | `python tests/test_parallel_api.py` |
| `test_dropdown.py` | Test dropdown UI | `python tests/test_dropdown.py` |
| `run_single_test.py` | Run single test | `python tests/run_single_test.py` |

---

## 🔧 Workspace Tools (Root)

| Script | Purpose | Usage |
|--------|---------|-------|
| `index_workspace.py` | Build Chroma search index | `python index_workspace.py` |
| `query_workspace.py` | Search the workspace | `python query_workspace.py "your query"` |

---

## 📓 Jupyter Notebooks (`notebooks/`)

| Notebook | Purpose |
|----------|---------|
| `Chroma Signal.ipynb` | Main signal analysis |
| `chroma_signal_explorer.ipynb` | Interactive signal explorer |
| `dormant_users_analysis.ipynb` | Dormant user reactivation analysis |
| `si_partner_program_analysis.ipynb` | SI partner program analysis |
| `SI program.ipynb` | SI program notebook |

---

## 🆕 Adding a New Script

When you create a new script:

1. **Search first**: `python query_workspace.py "what you want to do"`
2. **Put it in the correct folder**: `scripts/{category}/`
3. **Add a docstring** explaining purpose
4. **Follow naming**: `{verb}_{noun}_{detail}.py`
5. **Re-index**: `python index_workspace.py --quick`

---

*Last Updated: January 2026*
