// Company data from research pipeline - 200+ verified companies
// Expanded AI-Powered Deep Research Market Pipeline
// Last updated: December 2025

const COMPANIES_DATA = [
  // ============================================================
  // TIER 1 - HIGHEST PRIORITY (Immediate Need + Budget)
  // ============================================================
  {"name": "Mintlify", "category": "Tier 1 Priority", "valuation": "Acquired Trieve", "signal": "Hiring RAG engineers, explicit search infrastructure need", "priority": "HIGH"},
  {"name": "Clay", "category": "Tier 1 Priority", "valuation": "$3.1B", "signal": "1B+ Claygent research tasks, natural buyer", "priority": "HIGH"},
  {"name": "Apollo.io", "category": "Tier 1 Priority", "valuation": "$110M+ funding", "signal": "AI gap, LinkedIn delisting pressure", "priority": "HIGH"},
  {"name": "Zendesk", "category": "Tier 1 Priority", "valuation": "$10.2B (private)", "signal": "Third-party LLM dependence", "priority": "HIGH"},
  {"name": "Jasper", "category": "Tier 1 Priority", "valuation": "$125M Series A", "signal": "Struggling, valuation down, CEO replaced", "priority": "HIGH"},

  // ============================================================
  // TIER 2 - STRONG CANDIDATES
  // ============================================================
  {"name": "Pieces for Developers", "category": "Tier 2 Priority", "valuation": "Growing", "signal": "Security-focused, workflow memory", "priority": "HIGH"},
  {"name": "GitBook", "category": "Tier 2 Priority", "valuation": "Bootstrapped/Profitable", "signal": "2M+ users, basic AI search", "priority": "HIGH"},
  {"name": "ReadMe", "category": "Tier 2 Priority", "valuation": "$9M Series A", "signal": "18K+ companies, basic AI features", "priority": "HIGH"},
  {"name": "Forethought", "category": "Tier 2 Priority", "valuation": "~$500M", "signal": "$25M Series D, 61 employees", "priority": "HIGH"},
  {"name": "Qualified", "category": "Tier 2 Priority", "valuation": "$100M+ funding", "signal": "Piper AI SDR needs research", "priority": "HIGH"},

  // ============================================================
  // TIER 3 - HIGH-VALUE TARGETS (Larger, More Complex)
  // ============================================================
  {"name": "Glean", "category": "Tier 3 Priority", "valuation": "$7.2B", "signal": "$100M+ ARR, might build vs. buy", "priority": "HIGH"},
  {"name": "Cursor", "category": "Tier 3 Priority", "valuation": "$29.3B", "signal": "Acquired Supermaven, focus on code not general research", "priority": "HIGH"},
  {"name": "Harvey", "category": "Tier 3 Priority", "valuation": "$8B (Dec 2025)", "signal": "$760M raised in 2025, 45 of AmLaw 100", "priority": "HIGH"},
  {"name": "Abridge", "category": "Tier 3 Priority", "valuation": "$5.3B", "signal": "$100M ARR, Epic partnership, 150+ health systems", "priority": "HIGH"},
  {"name": "n8n", "category": "Tier 3 Priority", "valuation": "$2.5B (Oct 2025)", "signal": "75% of workflows use AI/LLM", "priority": "HIGH"},

  // ============================================================
  // 1. DOCUMENTATION & API PLATFORMS (25+ companies)
  // ============================================================
  {"name": "Postman", "category": "Documentation & API", "valuation": "$5.6B", "signal": "Facing backlash, cloud migration issues", "priority": "HIGH"},
  {"name": "Swagger", "category": "Documentation & API", "valuation": "SmartBear owned", "signal": "Design-first approach, limited AI", "priority": "MEDIUM"},
  {"name": "SwaggerHub", "category": "Documentation & API", "valuation": "SmartBear owned", "signal": "Design-first approach, limited AI", "priority": "MEDIUM"},
  {"name": "Stoplight", "category": "Documentation & API", "valuation": "$40M+ funding", "signal": "API design platform", "priority": "MEDIUM-HIGH"},
  {"name": "APIdog", "category": "Documentation & API", "valuation": "Growing", "signal": "Postman alternative, full lifecycle", "priority": "MEDIUM"},
  {"name": "Hoppscotch", "category": "Documentation & API", "valuation": "Open-source", "signal": "Lightweight, REST/GraphQL/WebSocket", "priority": "MEDIUM"},
  {"name": "EchoAPI", "category": "Documentation & API", "valuation": "Early stage", "signal": "Zero-config, semantic search capabilities", "priority": "MEDIUM"},
  {"name": "Bruno", "category": "Documentation & API", "valuation": "Open-source", "signal": "Git-integrated, offline-first, privacy-focused", "priority": "MEDIUM"},
  {"name": "Kong Insomnia", "category": "Documentation & API", "valuation": "Kong owned", "signal": "REST/GraphQL testing", "priority": "MEDIUM"},
  {"name": "RapiDoc", "category": "Documentation & API", "valuation": "Open-source", "signal": "API documentation generation", "priority": "LOW"},
  {"name": "Document360", "category": "Documentation & API", "valuation": "$12M+ funding", "signal": "Knowledge base + API docs", "priority": "MEDIUM-HIGH"},
  {"name": "Archbee", "category": "Documentation & API", "valuation": "$4M+ funding", "signal": "Developer documentation", "priority": "MEDIUM"},
  {"name": "Notion", "category": "Documentation & API", "valuation": "$10B", "signal": "Expanding AI, needs research depth", "priority": "MEDIUM"},
  {"name": "Slite", "category": "Documentation & API", "valuation": "$15M+ funding", "signal": "Team knowledge base", "priority": "MEDIUM-HIGH"},
  {"name": "Tettra", "category": "Documentation & API", "valuation": "$4M+ funding", "signal": "Internal wiki platform", "priority": "MEDIUM-HIGH"},
  {"name": "Slab", "category": "Documentation & API", "valuation": "Acquired by Qualtrics", "signal": "Knowledge management", "priority": "MEDIUM"},

  // ============================================================
  // 2. AI CODING ASSISTANTS (20+ companies)
  // ============================================================
  {"name": "Anysphere", "category": "AI Coding Assistants", "valuation": "$29.3B, $2.3B raised (Nov 2025)", "signal": "Fastest-growing, acquired Supermaven", "priority": "HIGH"},
  {"name": "Codeium", "category": "AI Coding Assistants", "valuation": "$2.85B (Feb 2025)", "signal": "$40M ARR, agentic AI focus", "priority": "HIGH"},
  {"name": "Windsurf", "category": "AI Coding Assistants", "valuation": "$2.85B", "signal": "Agentic AI focus", "priority": "HIGH"},
  {"name": "Augment", "category": "AI Coding Assistants", "valuation": "$977M, $252M raised", "signal": "Enterprise focus, large codebases", "priority": "HIGH"},
  {"name": "Poolside AI", "category": "AI Coding Assistants", "valuation": "$500M Series B", "signal": "Deep-learning code assistant", "priority": "HIGH"},
  {"name": "Magic AI", "category": "AI Coding Assistants", "valuation": "$400M+ funding", "signal": "LTM-2-mini model, 10M lines context", "priority": "HIGH"},
  {"name": "Magic", "category": "AI Coding Assistants", "valuation": "$400M+ funding", "signal": "LTM-2-mini model, 10M lines context", "priority": "HIGH"},
  {"name": "Cognition", "category": "AI Coding Assistants", "valuation": "$4B", "signal": "First AI software engineer (Devin)", "priority": "HIGH"},
  {"name": "Devin", "category": "AI Coding Assistants", "valuation": "$4B", "signal": "First AI software engineer", "priority": "HIGH"},
  {"name": "Tabnine", "category": "AI Coding Assistants", "valuation": "$55M+ funding", "signal": "Privacy-focused, enterprise", "priority": "MEDIUM-HIGH"},
  {"name": "Replit", "category": "AI Coding Assistants", "valuation": "$1.16B", "signal": "Ghostwriter + Agent, education focus", "priority": "HIGH"},
  {"name": "Qodo", "category": "AI Coding Assistants", "valuation": "$51M funding", "signal": "Code integrity, testing focus", "priority": "HIGH"},
  {"name": "CodiumAI", "category": "AI Coding Assistants", "valuation": "$51M funding", "signal": "Code integrity, testing focus", "priority": "HIGH"},
  {"name": "Sourcegraph", "category": "AI Coding Assistants", "valuation": "$150M+ funding", "signal": "Code search and intelligence", "priority": "HIGH"},
  {"name": "Warp", "category": "AI Coding Assistants", "valuation": "$73M funding", "signal": "Rust-based terminal", "priority": "MEDIUM-HIGH"},
  {"name": "CodeGPT", "category": "AI Coding Assistants", "valuation": "Growing", "signal": "Multi-model, agent ecosystem", "priority": "MEDIUM"},
  {"name": "Continue.dev", "category": "AI Coding Assistants", "valuation": "Open-source", "signal": "Local model integration", "priority": "MEDIUM"},
  {"name": "Bolt.new", "category": "AI Coding Assistants", "valuation": "Viral growth", "signal": "Full-stack app generation", "priority": "HIGH"},
  {"name": "v0.dev", "category": "AI Coding Assistants", "valuation": "Vercel", "signal": "UI generation from prompts", "priority": "MEDIUM-HIGH"},
  {"name": "Lovable", "category": "AI Coding Assistants", "valuation": "$100M ARR in 8 months", "signal": "Fastest-growing AI startup claim", "priority": "HIGH"},

  // ============================================================
  // 3. SALES INTELLIGENCE (15+ companies)
  // ============================================================
  {"name": "Sumble", "category": "Sales Intelligence", "valuation": "$38.5M (Oct 2025)", "signal": "Kaggle founders, 550% YoY growth", "priority": "HIGH"},
  {"name": "Cognism", "category": "Sales Intelligence", "valuation": "$100M+ funding", "signal": "Clay competitor, European focus", "priority": "HIGH"},
  {"name": "ZoomInfo", "category": "Sales Intelligence", "valuation": "Public ($8B+ market cap)", "signal": "Incumbent, AI enhancement needed", "priority": "HIGH"},
  {"name": "Gong", "category": "Sales Intelligence", "valuation": "$7.25B", "signal": "Revenue intelligence", "priority": "HIGH"},
  {"name": "6sense", "category": "Sales Intelligence", "valuation": "$5.2B", "signal": "Account-based marketing", "priority": "MEDIUM-HIGH"},
  {"name": "Outreach", "category": "Sales Intelligence", "valuation": "$4.4B", "signal": "Sales engagement platform", "priority": "MEDIUM-HIGH"},
  {"name": "Salesloft", "category": "Sales Intelligence", "valuation": "Acquired by Vista Equity", "signal": "Sales engagement", "priority": "MEDIUM-HIGH"},
  {"name": "Lusha", "category": "Sales Intelligence", "valuation": "$205M funding", "signal": "Contact data platform", "priority": "MEDIUM"},
  {"name": "Seamless.AI", "category": "Sales Intelligence", "valuation": "Growing", "signal": "Real-time lead verification", "priority": "MEDIUM"},
  {"name": "LeadIQ", "category": "Sales Intelligence", "valuation": "$30M+ funding", "signal": "Prospecting platform", "priority": "MEDIUM"},
  {"name": "Clearbit", "category": "Sales Intelligence", "valuation": "Acquired by HubSpot", "signal": "Data enrichment", "priority": "MEDIUM"},
  {"name": "Demandbase", "category": "Sales Intelligence", "valuation": "$400M+ funding", "signal": "ABM platform", "priority": "MEDIUM-HIGH"},

  // ============================================================
  // 4. CUSTOMER SUPPORT AI (20+ companies)
  // ============================================================
  {"name": "Sierra", "category": "Customer Support AI", "valuation": "$104M ARR (Nov 2025)", "signal": "4x growth, voice > text shift", "priority": "HIGH"},
  {"name": "Sierra AI", "category": "Customer Support AI", "valuation": "$104M ARR", "signal": "4x growth, voice > text shift", "priority": "HIGH"},
  {"name": "Decagon", "category": "Customer Support AI", "valuation": "$1.5B, $17M ARR", "signal": "131M Series C (June 2025), a16z/Accel", "priority": "HIGH"},
  {"name": "Intercom", "category": "Customer Support AI", "valuation": "$1.3B+", "signal": "Growing AI agent (Fin) within platform", "priority": "HIGH"},
  {"name": "Freshworks", "category": "Customer Support AI", "valuation": "Public ($4B+ market cap)", "signal": "Freddy AI, enterprise focus", "priority": "MEDIUM-HIGH"},
  {"name": "Crescendo.ai", "category": "Customer Support AI", "valuation": "$500M, $91M ARR", "signal": "100% ticket resolution model", "priority": "HIGH"},
  {"name": "Ada", "category": "Customer Support AI", "valuation": "$190M+ funding", "signal": "Automated customer service", "priority": "HIGH"},
  {"name": "Kustomer", "category": "Customer Support AI", "valuation": "Acquired by Meta/spun out", "signal": "CRM + AI support", "priority": "MEDIUM"},
  {"name": "Gladly", "category": "Customer Support AI", "valuation": "$90M+ funding", "signal": "People-centered support", "priority": "MEDIUM-HIGH"},
  {"name": "Gorgias", "category": "Customer Support AI", "valuation": "$60M+ funding", "signal": "E-commerce focus", "priority": "MEDIUM-HIGH"},
  {"name": "Help Scout", "category": "Customer Support AI", "valuation": "Growing", "signal": "SMB customer support", "priority": "MEDIUM"},
  {"name": "Voiceflow", "category": "Customer Support AI", "valuation": "$45M+ funding", "signal": "Conversational AI platform", "priority": "MEDIUM-HIGH"},
  {"name": "Kore.ai", "category": "Customer Support AI", "valuation": "$150M+ funding", "signal": "Enterprise voice/multi-channel", "priority": "MEDIUM-HIGH"},
  {"name": "Cognigy", "category": "Customer Support AI", "valuation": "Acquired by NICE ($955M)", "signal": "Conversational AI platform", "priority": "MEDIUM-HIGH"},
  {"name": "Rasa", "category": "Customer Support AI", "valuation": "$70M+ funding", "signal": "Open-source conversational AI", "priority": "MEDIUM-HIGH"},
  {"name": "GPTBots", "category": "Customer Support AI", "valuation": "Growing", "signal": "No-code platform", "priority": "MEDIUM"},
  {"name": "Gumloop", "category": "Customer Support AI", "valuation": "Growing", "signal": "AI agent builder", "priority": "MEDIUM"},
  {"name": "Moveworks", "category": "Customer Support AI", "valuation": "Acquired by ServiceNow ($2.1B)", "signal": "Enterprise AI support", "priority": "HIGH"},

  // ============================================================
  // 5. HEALTHCARE AI - CLINICAL DOCUMENTATION (25+ companies)
  // ============================================================
  {"name": "Nabla", "category": "Healthcare AI", "valuation": "~$300M, $120M funding", "signal": "Kaiser deployment, $119/month pricing", "priority": "HIGH"},
  {"name": "Ambience Healthcare", "category": "Healthcare AI", "valuation": "$1.25B, $243M Series C", "signal": "Cleveland Clinic exclusive", "priority": "HIGH"},
  {"name": "Suki", "category": "Healthcare AI", "valuation": "$500M, $70M funding", "signal": "AI physician assistant", "priority": "HIGH"},
  {"name": "Suki AI", "category": "Healthcare AI", "valuation": "$500M", "signal": "AI physician assistant", "priority": "HIGH"},
  {"name": "DeepScribe", "category": "Healthcare AI", "valuation": "$50M+ funding", "signal": "Lower-cost, smaller clinics", "priority": "MEDIUM-HIGH"},
  {"name": "Freed", "category": "Healthcare AI", "valuation": "$30M+ funding", "signal": "AI clinician assistant", "priority": "MEDIUM-HIGH"},
  {"name": "Regard", "category": "Healthcare AI", "valuation": "$81M+ funding", "signal": "AI physician note-taking", "priority": "HIGH"},
  {"name": "CodaMetrix", "category": "Healthcare AI", "valuation": "$95M+ funding", "signal": "AI medical coding", "priority": "HIGH"},
  {"name": "Tennr", "category": "Healthcare AI", "valuation": "$605M, $101M Series C", "signal": "Healthcare workflow automation", "priority": "HIGH"},
  {"name": "OpenEvidence", "category": "Healthcare AI", "valuation": "$6B, $200M Series C", "signal": "AI medical chatbot", "priority": "HIGH"},
  {"name": "Eleos Health", "category": "Healthcare AI", "valuation": "$50M+ funding", "signal": "Behavioral/post-acute scribing", "priority": "MEDIUM-HIGH"},
  {"name": "Predoc", "category": "Healthcare AI", "valuation": "$30M Series A", "signal": "700% YoY growth, health info management", "priority": "HIGH"},
  {"name": "Attuned Intelligence", "category": "Healthcare AI", "valuation": "$13M funding", "signal": "Hospital call center AI", "priority": "MEDIUM"},
  {"name": "Honey Health", "category": "Healthcare AI", "valuation": "$7.8M seed", "signal": "AI agents for EHR workflows", "priority": "MEDIUM"},
  {"name": "Tandem Health", "category": "Healthcare AI", "valuation": "Recent funding", "signal": "Clinical documentation", "priority": "MEDIUM"},
  {"name": "Commure", "category": "Healthcare AI", "valuation": "Acquired Augmedix ($139M)", "signal": "Healthcare platform consolidator", "priority": "HIGH"},
  {"name": "Notable Health", "category": "Healthcare AI", "valuation": "$100M+ funding", "signal": "Healthcare automation", "priority": "MEDIUM-HIGH"},
  {"name": "Pieces Technologies", "category": "Healthcare AI", "valuation": "$30M+ funding", "signal": "Clinical AI platform", "priority": "MEDIUM-HIGH"},
  {"name": "Cohere Health", "category": "Healthcare AI", "valuation": "$50M+ funding", "signal": "Prior authorization AI", "priority": "HIGH"},
  {"name": "Viz.ai", "category": "Healthcare AI", "valuation": "$250M+ funding", "signal": "AI disease detection", "priority": "HIGH"},
  {"name": "Hippocratic AI", "category": "Healthcare AI", "valuation": "$3.5B", "signal": "Healthcare AI agents", "priority": "HIGH"},

  // ============================================================
  // 6. LEGAL TECH (30+ companies)
  // ============================================================
  {"name": "Harvey AI", "category": "Legal Tech", "valuation": "$8B (Dec 2025)", "signal": "$760M raised in 2025, 45 of AmLaw 100", "priority": "HIGH"},
  {"name": "EvenUp", "category": "Legal Tech", "valuation": "$2B+", "signal": "$150M Series E, PI law specialist", "priority": "HIGH"},
  {"name": "Clio", "category": "Legal Tech", "valuation": "$5B", "signal": "Acquired vLex, Clio Duo AI", "priority": "HIGH"},
  {"name": "Spellbook", "category": "Legal Tech", "valuation": "$350M", "signal": "$50M Series B, contract AI copilot", "priority": "HIGH"},
  {"name": "Eve", "category": "Legal Tech", "valuation": "$47M Series A", "signal": "Plaintiff firm AI, a16z led", "priority": "HIGH"},
  {"name": "Filevine", "category": "Legal Tech", "valuation": "$400M funding", "signal": "Case management platform", "priority": "HIGH"},
  {"name": "Eudia", "category": "Legal Tech", "valuation": "$105M Series A", "signal": "Buy-and-build legal services", "priority": "HIGH"},
  {"name": "Luminance", "category": "Legal Tech", "valuation": "Strong growth", "signal": "Legal-Grade™ AI, European presence", "priority": "HIGH"},
  {"name": "Supio", "category": "Legal Tech", "valuation": "$91M funding", "signal": "4x YoY growth, personal injury", "priority": "HIGH"},
  {"name": "Legora", "category": "Legal Tech", "valuation": "Growing fast", "signal": "+3133% search volume, European", "priority": "MEDIUM-HIGH"},
  {"name": "Darrow", "category": "Legal Tech", "valuation": "$35M+ funding", "signal": "AI legal services", "priority": "MEDIUM-HIGH"},
  {"name": "Ironclad", "category": "Legal Tech", "valuation": "$150M+ funding", "signal": "Contract lifecycle management", "priority": "HIGH"},
  {"name": "LinkSquares", "category": "Legal Tech", "valuation": "$130M+ funding", "signal": "Contract analytics", "priority": "HIGH"},
  {"name": "Lexion", "category": "Legal Tech", "valuation": "$30M+ funding", "signal": "AI contract management", "priority": "MEDIUM-HIGH"},
  {"name": "Kira Systems", "category": "Legal Tech", "valuation": "Acquired by Litera", "signal": "ML contract analysis", "priority": "MEDIUM"},
  {"name": "Eigen Technologies", "category": "Legal Tech", "valuation": "$55M+ funding", "signal": "Document intelligence", "priority": "MEDIUM-HIGH"},
  {"name": "Evisort", "category": "Legal Tech", "valuation": "Acquired by Workday", "signal": "Contract intelligence", "priority": "MEDIUM-HIGH"},
  {"name": "Aracor AI", "category": "Legal Tech", "valuation": "$4.5M pre-seed", "signal": "Due diligence + contract review", "priority": "MEDIUM"},
  {"name": "iPNOTE", "category": "Legal Tech", "valuation": "$1M seed", "signal": "AI-powered IP management", "priority": "MEDIUM"},
  {"name": "Valla", "category": "Legal Tech", "valuation": "£3M seed", "signal": "Employment rights AI", "priority": "MEDIUM"},
  {"name": "Ankar", "category": "Legal Tech", "valuation": "£3M seed", "signal": "IP discovery/protection", "priority": "MEDIUM"},
  {"name": "Justpoint", "category": "Legal Tech", "valuation": "Growing", "signal": "Biomedical science + AI legal", "priority": "MEDIUM"},
  {"name": "NewCode.ai", "category": "Legal Tech", "valuation": "No outside funding", "signal": "DLA Piper European selection", "priority": "MEDIUM"},
  {"name": "Relativity", "category": "Legal Tech", "valuation": "Private equity owned", "signal": "E-discovery leader", "priority": "MEDIUM-HIGH"},
  {"name": "Onna", "category": "Legal Tech", "valuation": "$80M+ funding", "signal": "Knowledge integration", "priority": "MEDIUM-HIGH"},
  {"name": "CS Disco", "category": "Legal Tech", "valuation": "Public", "signal": "E-discovery platform", "priority": "MEDIUM-HIGH"},
  {"name": "ContractPodAi", "category": "Legal Tech", "valuation": "~$500M", "signal": "Contract lifecycle management", "priority": "MEDIUM-HIGH"},
  {"name": "Ontra", "category": "Legal Tech", "valuation": "~$500M", "signal": "Legal automation for PE", "priority": "MEDIUM"},
  {"name": "Juro", "category": "Legal Tech", "valuation": "~$150M", "signal": "Contract collaboration", "priority": "MEDIUM"},

  // ============================================================
  // 7. AI WORKFLOW AUTOMATION & AGENTS (25+ companies)
  // ============================================================
  {"name": "Zapier", "category": "AI Workflow Automation", "valuation": "$5B+", "signal": "8,000+ integrations, AI agents launched", "priority": "HIGH"},
  {"name": "Make", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "7,500+ templates, budget-friendly", "priority": "MEDIUM-HIGH"},
  {"name": "Integromat", "category": "AI Workflow Automation", "valuation": "Now Make", "signal": "7,500+ templates", "priority": "MEDIUM-HIGH"},
  {"name": "Lindy.ai", "category": "AI Workflow Automation", "valuation": "~$200M", "signal": "AI 'employees', natural language", "priority": "HIGH"},
  {"name": "Lindy AI", "category": "AI Workflow Automation", "valuation": "~$200M", "signal": "AI 'employees', natural language", "priority": "HIGH"},
  {"name": "Relevance AI", "category": "AI Workflow Automation", "valuation": "$150M", "signal": "40K agents created Jan 2025 alone", "priority": "HIGH"},
  {"name": "Workato", "category": "AI Workflow Automation", "valuation": "$5.7B", "signal": "Enterprise automation", "priority": "MEDIUM-HIGH"},
  {"name": "Relay.app", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "Human-in-the-loop, used by Cursor", "priority": "MEDIUM-HIGH"},
  {"name": "Pipedream", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "Developer-grade scripting", "priority": "MEDIUM"},
  {"name": "Airbyte", "category": "AI Workflow Automation", "valuation": "$200M+ funding", "signal": "Data integration specialist", "priority": "MEDIUM-HIGH"},
  {"name": "Tray.io", "category": "AI Workflow Automation", "valuation": "$150M+ funding", "signal": "General automation platform", "priority": "MEDIUM-HIGH"},
  {"name": "Activepieces", "category": "AI Workflow Automation", "valuation": "Open-source", "signal": "Zapier alternative", "priority": "MEDIUM"},
  {"name": "MESA", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "E-commerce automation", "priority": "MEDIUM"},
  {"name": "Lleverage", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "'Vibe Automation' natural language", "priority": "MEDIUM"},
  {"name": "AgentX", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "Multi-agent, RAG support", "priority": "MEDIUM"},
  {"name": "AirOps", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "Sales/marketing specialization", "priority": "MEDIUM-HIGH"},
  {"name": "Bardeen", "category": "AI Workflow Automation", "valuation": "$15M+ funding", "signal": "Browser automation", "priority": "MEDIUM-HIGH"},
  {"name": "Parabola", "category": "AI Workflow Automation", "valuation": "$40M+ funding", "signal": "Data workflow automation", "priority": "MEDIUM-HIGH"},
  {"name": "Alloy", "category": "AI Workflow Automation", "valuation": "$100M+ funding", "signal": "E-commerce automation", "priority": "MEDIUM-HIGH"},
  {"name": "Merge", "category": "AI Workflow Automation", "valuation": "$75M+ funding", "signal": "Unified API platform", "priority": "MEDIUM-HIGH"},
  {"name": "Latenode", "category": "AI Workflow Automation", "valuation": "Growing", "signal": "Advanced data workflows", "priority": "MEDIUM"},
  {"name": "StackStorm", "category": "AI Workflow Automation", "valuation": "Open-source", "signal": "Event-driven automation", "priority": "LOW"},

  // ============================================================
  // 8. ENTERPRISE SEARCH & KNOWLEDGE MANAGEMENT (20+ companies)
  // ============================================================
  {"name": "Guru", "category": "Enterprise Search", "valuation": "$100M+ funding", "signal": "Knowledge cards, workflow integration", "priority": "HIGH"},
  {"name": "Coveo", "category": "Enterprise Search", "valuation": "Public (TSX: CVO)", "signal": "Enterprise AI relevance", "priority": "MEDIUM-HIGH"},
  {"name": "Elastic", "category": "Enterprise Search", "valuation": "Public (NYSE: ESTC)", "signal": "Open-source search", "priority": "MEDIUM"},
  {"name": "Algolia", "category": "Enterprise Search", "valuation": "$2.25B", "signal": "Search & discovery API", "priority": "MEDIUM-HIGH"},
  {"name": "Lucidworks", "category": "Enterprise Search", "valuation": "$100M+ funding", "signal": "Enterprise search platform", "priority": "HIGH"},
  {"name": "Sinequa", "category": "Enterprise Search", "valuation": "Growing", "signal": "Enterprise search AI", "priority": "MEDIUM-HIGH"},
  {"name": "Yext", "category": "Enterprise Search", "valuation": "Public (NYSE: YEXT)", "signal": "Digital presence platform", "priority": "MEDIUM"},
  {"name": "Capacity", "category": "Enterprise Search", "valuation": "$30M+ funding", "signal": "AI-powered helpdesk", "priority": "MEDIUM-HIGH"},
  {"name": "Bloomfire", "category": "Enterprise Search", "valuation": "$25M+ funding", "signal": "Knowledge sharing platform", "priority": "MEDIUM-HIGH"},
  {"name": "Tanka", "category": "Enterprise Search", "valuation": "Growing", "signal": "AI messenger with memory", "priority": "MEDIUM"},
  {"name": "Docket AI", "category": "Enterprise Search", "valuation": "Growing", "signal": "Enterprise knowledge AI", "priority": "MEDIUM"},
  {"name": "Dashworks", "category": "Enterprise Search", "valuation": "Growing", "signal": "Universal search", "priority": "MEDIUM-HIGH"},
  {"name": "Unify", "category": "Enterprise Search", "valuation": "Growing", "signal": "Unified search platform", "priority": "MEDIUM"},
  {"name": "Hebbia", "category": "Enterprise Search", "valuation": "$130M+ funding", "signal": "AI for knowledge work", "priority": "HIGH"},
  {"name": "Vectara", "category": "Enterprise Search", "valuation": "Growing", "signal": "GenAI search platform", "priority": "MEDIUM-HIGH"},
  {"name": "Pryon", "category": "Enterprise Search", "valuation": "$100M+ funding", "signal": "Enterprise AI answers", "priority": "HIGH"},
  {"name": "Stonly", "category": "Enterprise Search", "valuation": "~$30M", "signal": "Interactive guides", "priority": "MEDIUM-HIGH"},
  {"name": "Shelf.io", "category": "Enterprise Search", "valuation": "~$30M", "signal": "Knowledge automation", "priority": "MEDIUM-HIGH"},
  {"name": "Spekit", "category": "Enterprise Search", "valuation": "~$50M", "signal": "In-app learning", "priority": "MEDIUM"},

  // ============================================================
  // 9. FINANCIAL RESEARCH & INTELLIGENCE (20+ companies)
  // ============================================================
  {"name": "AlphaSense", "category": "Financial Research", "valuation": "$1.4B+ funding", "signal": "Acquired Tegus, market intelligence leader", "priority": "HIGH"},
  {"name": "Koyfin", "category": "Financial Research", "valuation": "Growing", "signal": "Financial data & analytics", "priority": "MEDIUM-HIGH"},
  {"name": "Bloomberg", "category": "Financial Research", "valuation": "Private ($70B+ est.)", "signal": "Terminal incumbent", "priority": "LOW"},
  {"name": "Fintool", "category": "Financial Research", "valuation": "Launched 2024", "signal": "Multi-model AI financial research", "priority": "MEDIUM-HIGH"},
  {"name": "Hudson Labs", "category": "Financial Research", "valuation": "Growing", "signal": "AI fundamental research", "priority": "MEDIUM-HIGH"},
  {"name": "Rogo", "category": "Financial Research", "valuation": "Growing", "signal": "GenAI for financial services", "priority": "MEDIUM-HIGH"},
  {"name": "Kensho", "category": "Financial Research", "valuation": "Acquired (S&P Global)", "signal": "AI analytics", "priority": "MEDIUM"},
  {"name": "Dataminr", "category": "Financial Research", "valuation": "$1.8B", "signal": "Real-time event detection", "priority": "HIGH"},
  {"name": "Sentieo", "category": "Financial Research", "valuation": "Acquired by AlphaSense", "signal": "Financial research platform", "priority": "MEDIUM"},
  {"name": "RavenPack", "category": "Financial Research", "valuation": "Growing", "signal": "AI analytics for finance", "priority": "MEDIUM-HIGH"},
  {"name": "Thinknum", "category": "Financial Research", "valuation": "Growing", "signal": "Alternative data", "priority": "MEDIUM"},
  {"name": "Visible Alpha", "category": "Financial Research", "valuation": "Growing", "signal": "Consensus data platform", "priority": "MEDIUM-HIGH"},
  {"name": "YCharts", "category": "Financial Research", "valuation": "Growing", "signal": "Investment research", "priority": "MEDIUM"},
  {"name": "CFRA", "category": "Financial Research", "valuation": "Growing", "signal": "Independent research", "priority": "MEDIUM"},
  {"name": "Atom Finance", "category": "Financial Research", "valuation": "$65M+ funding", "signal": "Modern investment platform", "priority": "MEDIUM-HIGH"},
  {"name": "Generative Alpha", "category": "Financial Research", "valuation": "Growing", "signal": "AI + finance intersection", "priority": "MEDIUM"},
  {"name": "Farsight", "category": "Financial Research", "valuation": "Growing", "signal": "AI automations for finance", "priority": "MEDIUM"},
  {"name": "Auquan", "category": "Financial Research", "valuation": "Growing", "signal": "AI investment workflows", "priority": "MEDIUM"},
  {"name": "Street Context", "category": "Financial Research", "valuation": "Growing", "signal": "Email intelligence for capital markets", "priority": "MEDIUM"},
  {"name": "Daloopa", "category": "Financial Research", "valuation": "~$100M", "signal": "Financial data extraction", "priority": "HIGH"},
  {"name": "YipitData", "category": "Financial Research", "valuation": "$1B+", "signal": "Alternative data provider", "priority": "HIGH"},
  {"name": "Toggle AI", "category": "Financial Research", "valuation": "~$200M", "signal": "AI investment insights", "priority": "MEDIUM-HIGH"},
  {"name": "Reflexivity", "category": "Financial Research", "valuation": "~$200M", "signal": "AI-powered research", "priority": "MEDIUM-HIGH"},

  // ============================================================
  // 10. HR & RECRUITING AI (20+ companies)
  // ============================================================
  {"name": "Eightfold AI", "category": "HR & Recruiting AI", "valuation": "$2B+", "signal": "Talent intelligence platform leader", "priority": "HIGH"},
  {"name": "Paradox", "category": "HR & Recruiting AI", "valuation": "Growing fast", "signal": "Conversational ATS, SAP partner", "priority": "HIGH"},
  {"name": "Olivia", "category": "HR & Recruiting AI", "valuation": "Paradox product", "signal": "Conversational recruiting assistant", "priority": "HIGH"},
  {"name": "Phenom", "category": "HR & Recruiting AI", "valuation": "$1.7B", "signal": "Talent experience platform", "priority": "HIGH"},
  {"name": "Beamery", "category": "HR & Recruiting AI", "valuation": "$800M", "signal": "Talent lifecycle management", "priority": "HIGH"},
  {"name": "HireVue", "category": "HR & Recruiting AI", "valuation": "Growing", "signal": "AI interviewing and assessments", "priority": "MEDIUM-HIGH"},
  {"name": "Seekout", "category": "HR & Recruiting AI", "valuation": "$115M+ funding", "signal": "Talent intelligence", "priority": "MEDIUM-HIGH"},
  {"name": "Gloat", "category": "HR & Recruiting AI", "valuation": "$190M+ funding", "signal": "Talent marketplace", "priority": "HIGH"},
  {"name": "Findem", "category": "HR & Recruiting AI", "valuation": "$50M+ funding", "signal": "AI talent acquisition", "priority": "MEDIUM-HIGH"},
  {"name": "Moonhub", "category": "HR & Recruiting AI", "valuation": "$50M+ funding", "signal": "AI recruiting", "priority": "MEDIUM-HIGH"},
  {"name": "Mercor", "category": "HR & Recruiting AI", "valuation": "$133M funding", "signal": "AI hiring platform", "priority": "HIGH"},
  {"name": "hireEZ", "category": "HR & Recruiting AI", "valuation": "Growing", "signal": "Outbound recruiting", "priority": "MEDIUM"},
  {"name": "Turing", "category": "HR & Recruiting AI", "valuation": "$159M funding", "signal": "Remote developer hiring", "priority": "MEDIUM-HIGH"},
  {"name": "Textio", "category": "HR & Recruiting AI", "valuation": "$42M+ funding", "signal": "Augmented writing for recruiting", "priority": "MEDIUM-HIGH"},
  {"name": "Humanly", "category": "HR & Recruiting AI", "valuation": "Growing", "signal": "Conversational hiring", "priority": "MEDIUM"},
  {"name": "Sense", "category": "HR & Recruiting AI", "valuation": "$90M+ funding", "signal": "Talent engagement", "priority": "MEDIUM-HIGH"},
  {"name": "Checkr", "category": "HR & Recruiting AI", "valuation": "$500M+ funding", "signal": "Background verification", "priority": "MEDIUM-HIGH"},
  {"name": "Alex", "category": "HR & Recruiting AI", "valuation": "$17M (2025)", "signal": "Voice-based AI screening", "priority": "MEDIUM-HIGH"},
  {"name": "Tezi", "category": "HR & Recruiting AI", "valuation": "$9M funding", "signal": "Automated hiring", "priority": "MEDIUM"},
  {"name": "Vora AI", "category": "HR & Recruiting AI", "valuation": "Growing", "signal": "Full-process automation", "priority": "MEDIUM"},
  {"name": "iCIMS", "category": "HR & Recruiting AI", "valuation": "Growing", "signal": "ATS with AI Digital Assistant", "priority": "MEDIUM-HIGH"},
  {"name": "Greenhouse", "category": "HR & Recruiting AI", "valuation": "~$500M", "signal": "ATS platform", "priority": "MEDIUM"},
  {"name": "Lever", "category": "HR & Recruiting AI", "valuation": "N/A", "signal": "ATS + CRM", "priority": "MEDIUM"},
  {"name": "Ashby", "category": "HR & Recruiting AI", "valuation": "~$100M", "signal": "All-in-one recruiting", "priority": "MEDIUM"},
  {"name": "Gem", "category": "HR & Recruiting AI", "valuation": "~$300M", "signal": "Talent engagement platform", "priority": "MEDIUM"},
  {"name": "Rippling", "category": "HR & Recruiting AI", "valuation": "$13.5B", "signal": "HR platform with recruiting", "priority": "MEDIUM"},

  // ============================================================
  // 11. CONTENT & SEO AI (15+ companies)
  // ============================================================
  {"name": "Surfer SEO", "category": "Content & SEO AI", "valuation": "Growing", "signal": "Content optimization leader", "priority": "MEDIUM-HIGH"},
  {"name": "Clearscope", "category": "Content & SEO AI", "valuation": "Growing", "signal": "Content optimization", "priority": "MEDIUM-HIGH"},
  {"name": "Frase", "category": "Content & SEO AI", "valuation": "Growing", "signal": "AI content briefs", "priority": "MEDIUM"},
  {"name": "MarketMuse", "category": "Content & SEO AI", "valuation": "Growing", "signal": "Content strategy AI", "priority": "MEDIUM"},
  {"name": "Writesonic", "category": "Content & SEO AI", "valuation": "$26M+ funding", "signal": "Content + SEO platform", "priority": "MEDIUM"},
  {"name": "Copy.ai", "category": "Content & SEO AI", "valuation": "$60M+ funding", "signal": "Marketing copy AI", "priority": "MEDIUM-HIGH"},
  {"name": "Writer", "category": "Content & SEO AI", "valuation": "$100M+ funding", "signal": "Enterprise AI writing", "priority": "HIGH"},
  {"name": "Writer.com", "category": "Content & SEO AI", "valuation": "$100M+ funding", "signal": "Enterprise AI writing", "priority": "HIGH"},
  {"name": "SEO.AI", "category": "Content & SEO AI", "valuation": "Growing", "signal": "AI-native SEO tool", "priority": "MEDIUM"},
  {"name": "GrowthBar", "category": "Content & SEO AI", "valuation": "Growing", "signal": "SEO content tool", "priority": "MEDIUM"},
  {"name": "Scalenut", "category": "Content & SEO AI", "valuation": "Growing", "signal": "AI content research", "priority": "MEDIUM"},
  {"name": "NeuronWriter", "category": "Content & SEO AI", "valuation": "Growing", "signal": "Content optimization", "priority": "MEDIUM"},
  {"name": "Outranking", "category": "Content & SEO AI", "valuation": "Growing", "signal": "AI SEO content", "priority": "MEDIUM"},
  {"name": "Semrush", "category": "Content & SEO AI", "valuation": "Public (NYSE: SEMR)", "signal": "SEO platform with AI", "priority": "MEDIUM"},
  {"name": "Ahrefs", "category": "Content & SEO AI", "valuation": "Growing", "signal": "SEO tools, AI features", "priority": "MEDIUM"},
  {"name": "Grammarly", "category": "Content & SEO AI", "valuation": "$13B", "signal": "Writing assistant", "priority": "MEDIUM"},
  {"name": "AI21 Labs", "category": "Content & SEO AI", "valuation": "$1.4B", "signal": "AI language models", "priority": "MEDIUM-HIGH"},
  {"name": "Typeface", "category": "Content & SEO AI", "valuation": "~$1B", "signal": "Enterprise content generation", "priority": "HIGH"},
  {"name": "Anyword", "category": "Content & SEO AI", "valuation": "~$100M", "signal": "Predictive copy AI", "priority": "MEDIUM"},

  // ============================================================
  // 12. REAL ESTATE & PROPTECH AI (15+ companies)
  // ============================================================
  {"name": "EliseAI", "category": "Real Estate & PropTech", "valuation": "$75M+ funding", "signal": "Conversational AI for multifamily", "priority": "HIGH"},
  {"name": "Dealpath", "category": "Real Estate & PropTech", "valuation": "Growing", "signal": "Deal management platform", "priority": "MEDIUM-HIGH"},
  {"name": "CompStak", "category": "Real Estate & PropTech", "valuation": "$70M+ funding", "signal": "CRE data analytics", "priority": "MEDIUM-HIGH"},
  {"name": "VTS", "category": "Real Estate & PropTech", "valuation": "$100M+ funding", "signal": "CRE leasing platform", "priority": "MEDIUM-HIGH"},
  {"name": "Measurabl", "category": "Real Estate & PropTech", "valuation": "$100M+ funding", "signal": "ESG for real estate", "priority": "MEDIUM-HIGH"},
  {"name": "Mapped", "category": "Real Estate & PropTech", "valuation": "Growing", "signal": "AI data layer for CRE", "priority": "MEDIUM"},
  {"name": "Built AI", "category": "Real Estate & PropTech", "valuation": "Growing", "signal": "AI for CRE investors", "priority": "MEDIUM"},
  {"name": "Prop-AI", "category": "Real Estate & PropTech", "valuation": "$1.5M pre-seed (2025)", "signal": "Property valuation AI", "priority": "MEDIUM"},
  {"name": "Lofty AI", "category": "Real Estate & PropTech", "valuation": "Growing", "signal": "Neighborhood growth prediction", "priority": "MEDIUM"},
  {"name": "Brickwise", "category": "Real Estate & PropTech", "valuation": "YC-backed", "signal": "AI property manager", "priority": "MEDIUM-HIGH"},
  {"name": "PARES", "category": "Real Estate & PropTech", "valuation": "YC-backed", "signal": "CRE broker workflow", "priority": "MEDIUM-HIGH"},
  {"name": "ArchiLabs", "category": "Real Estate & PropTech", "valuation": "YC-backed", "signal": "AI co-pilot for architecture", "priority": "MEDIUM-HIGH"},
  {"name": "Assembly", "category": "Real Estate & PropTech", "valuation": "YC-backed", "signal": "AI HOA management", "priority": "MEDIUM"},
  {"name": "LeaseAI", "category": "Real Estate & PropTech", "valuation": "$50M Series B", "signal": "Predictive leasing analytics", "priority": "HIGH"},
  {"name": "Cherre", "category": "Real Estate & PropTech", "valuation": "$50M+ funding", "signal": "Real estate data platform", "priority": "HIGH"},
  {"name": "Placer.ai", "category": "Real Estate & PropTech", "valuation": "$1.5B", "signal": "Location analytics", "priority": "HIGH"},
  {"name": "Crexi", "category": "Real Estate & PropTech", "valuation": "~$300M", "signal": "CRE marketplace", "priority": "MEDIUM-HIGH"},
  {"name": "CoStar", "category": "Real Estate & PropTech", "valuation": "~$30B", "signal": "CRE data incumbent", "priority": "LOW"},

  // ============================================================
  // 13. RESEARCH & ACADEMIC TOOLS
  // ============================================================
  {"name": "Elicit", "category": "Research Tools", "valuation": "$100M", "signal": "AI research assistant", "priority": "HIGH"},
  {"name": "Semantic Scholar", "category": "Research Tools", "valuation": "Allen Institute", "signal": "AI-powered academic search", "priority": "HIGH"},
  {"name": "Consensus", "category": "Research Tools", "valuation": "~$20M", "signal": "AI research synthesis", "priority": "MEDIUM-HIGH"},
  {"name": "Scite", "category": "Research Tools", "valuation": "Acquired", "signal": "Citation analysis", "priority": "HIGH"},
  {"name": "Iris.ai", "category": "Research Tools", "valuation": "~$30M", "signal": "AI research workspace", "priority": "HIGH"},
  {"name": "ResearchRabbit", "category": "Research Tools", "valuation": "~$5M", "signal": "Paper discovery", "priority": "MEDIUM"},
  {"name": "Connected Papers", "category": "Research Tools", "valuation": "~$5M", "signal": "Visual paper exploration", "priority": "MEDIUM"},
  {"name": "Litmaps", "category": "Research Tools", "valuation": "~$10M", "signal": "Literature mapping", "priority": "MEDIUM"},
  {"name": "Scholarcy", "category": "Research Tools", "valuation": "~$3M", "signal": "Article summarization", "priority": "LOW-MEDIUM"},

  // ============================================================
  // 14. PROCUREMENT & SPEND MANAGEMENT
  // ============================================================
  {"name": "Zip", "category": "Procurement", "valuation": "$2.2B", "signal": "Procurement orchestration", "priority": "HIGH"},
  {"name": "Ramp", "category": "Procurement", "valuation": "$22.5B", "signal": "Corporate cards + spend management", "priority": "HIGH"},
  {"name": "Brex", "category": "Procurement", "valuation": "~$10B", "signal": "Corporate cards + finance", "priority": "MEDIUM"},
  {"name": "Coupa", "category": "Procurement", "valuation": "PE-owned", "signal": "BSM platform", "priority": "MEDIUM"},
  {"name": "Jaggaer", "category": "Procurement", "valuation": "~$500M", "signal": "Procurement platform", "priority": "MEDIUM"},
  {"name": "Airbase", "category": "Procurement", "valuation": "~$600M", "signal": "Spend management", "priority": "MEDIUM-HIGH"},
  {"name": "Spendesk", "category": "Procurement", "valuation": "~$500M", "signal": "Spend management (Europe)", "priority": "MEDIUM-HIGH"},
];

// Remove duplicates by name (case-insensitive)
const uniqueCompanies = [];
const seenNames = new Set();
for (const company of COMPANIES_DATA) {
  const normalizedName = company.name.toLowerCase().trim();
  if (!seenNames.has(normalizedName)) {
    seenNames.add(normalizedName);
    uniqueCompanies.push(company);
  }
}

// Export deduplicated list
const COMPANIES_DATA_FINAL = uniqueCompanies;

// Log count for verification
console.log(`📊 Loaded ${COMPANIES_DATA_FINAL.length} unique companies from 14 categories`);

// For backward compatibility
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { COMPANIES_DATA: COMPANIES_DATA_FINAL };
}
