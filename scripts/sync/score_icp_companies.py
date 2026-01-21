#!/usr/bin/env python3
"""
ICP Scoring and Prioritization for Deep Research Companies
===========================================================
Scores companies based on multiple factors to identify highest-value targets.

Scoring Factors:
1. Company Fit (40%)
   - Company size (sweet spot: 50-500 employees)
   - Funding stage (Series A/B are ideal)
   - Growth rate

2. Technical Fit (30%)
   - Use case alignment (RAG, search, recommendations)
   - Data volume
   - Current tech stack

3. Timing Signals (30%)
   - Recent funding
   - Hiring AI engineers
   - Product launches
   - Competitor switching

Usage:
    python scripts/sync/score_icp_companies.py analyze    # Score all companies
    python scripts/sync/score_icp_companies.py export     # Export to CSV
"""

import os
import json
import csv
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

class ICPScorer:
    """Score and prioritize companies based on ICP criteria."""

    def __init__(self):
        # Load company data
        self.companies_file = "data/companies/deep_research_companies.json"
        self.companies_data = self.load_companies()
        self.scored_companies = []

    def load_companies(self) -> Dict:
        """Load deep research companies."""
        filepath = os.path.join(os.path.dirname(__file__), '../../', self.companies_file)

        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def calculate_company_fit_score(self, company: Dict) -> Tuple[int, List[str]]:
        """Calculate company fit score (0-40)."""
        score = 0
        reasons = []

        valuation = company.get("valuation", "")

        # Company size scoring
        if "$50M" in valuation or "$100M" in valuation or "$200M" in valuation:
            score += 15
            reasons.append("Ideal company size (Series A/B)")
        elif "$500M" in valuation or "$1B" in valuation:
            score += 10
            reasons.append("Large but viable (Late stage)")
        elif "$10M" in valuation or "$20M" in valuation or "$30M" in valuation:
            score += 12
            reasons.append("Early stage with potential")
        else:
            score += 5

        # Funding recency (assume recent if Series A/B)
        if "Series A" in str(valuation) or "Series B" in str(valuation):
            score += 10
            reasons.append("Recent funding likely")

        # Growth potential
        if "AI" in company.get("description", "") or "ML" in company.get("description", ""):
            score += 10
            reasons.append("AI-first company")

        # Market position
        if company.get("name") in ["Clay", "Gong", "Glean", "AlphaSense", "Databricks"]:
            score += 5
            reasons.append("Market leader")

        return min(score, 40), reasons

    def calculate_technical_fit_score(self, company: Dict, category: str) -> Tuple[int, List[str]]:
        """Calculate technical fit score (0-30)."""
        score = 0
        reasons = []

        research_feature = company.get("research_feature", "")

        # Use case alignment
        high_value_use_cases = ["RAG", "semantic search", "knowledge", "embeddings", "recommendations"]
        for use_case in high_value_use_cases:
            if use_case.lower() in research_feature.lower():
                score += 10
                reasons.append(f"Perfect use case: {use_case}")
                break

        # Category scoring
        high_value_categories = ["enterprise_search", "sales_intelligence", "financial_research"]
        if category in high_value_categories:
            score += 10
            reasons.append(f"High-value category: {category}")

        # Technical complexity
        if "real-time" in research_feature.lower() or "scale" in research_feature.lower():
            score += 5
            reasons.append("Complex technical requirements")

        # Data volume implications
        if category in ["financial_research", "sales_intelligence", "data_analytics"]:
            score += 5
            reasons.append("High data volume likely")

        return min(score, 30), reasons

    def calculate_timing_score(self, company: Dict) -> Tuple[int, List[str]]:
        """Calculate timing score (0-30)."""
        score = 0
        reasons = []

        # Companies likely building AI features now
        ai_forward_companies = [
            "Clay", "Gong", "Glean", "AlphaSense", "Hebbia",
            "Vectara", "Perplexity AI", "You", "Mintlify"
        ]

        if company.get("name") in ai_forward_companies:
            score += 15
            reasons.append("Actively building AI features")

        # Fast-growing companies
        if "Bootstrapped" not in company.get("valuation", ""):
            score += 10
            reasons.append("VC-backed (growth pressure)")

        # Market timing
        if company.get("name") in ["Perplexity AI", "Hebbia", "Vectara"]:
            score += 5
            reasons.append("In hypergrowth phase")

        return min(score, 30), reasons

    def score_company(self, company: Dict, category: str) -> Dict:
        """Calculate total ICP score for a company."""
        # Calculate component scores
        company_fit, company_reasons = self.calculate_company_fit_score(company)
        technical_fit, technical_reasons = self.calculate_technical_fit_score(company, category)
        timing, timing_reasons = self.calculate_timing_score(company)

        total_score = company_fit + technical_fit + timing

        # Determine tier
        if total_score >= 70:
            tier = "Tier 1 - Immediate Priority"
        elif total_score >= 50:
            tier = "Tier 2 - High Priority"
        elif total_score >= 30:
            tier = "Tier 3 - Medium Priority"
        else:
            tier = "Tier 4 - Low Priority"

        return {
            "name": company.get("name", ""),
            "category": category.replace("_", " ").title(),
            "description": company.get("description", ""),
            "valuation": company.get("valuation", "Unknown"),
            "research_feature": company.get("research_feature", ""),
            "total_score": total_score,
            "company_fit_score": company_fit,
            "technical_fit_score": technical_fit,
            "timing_score": timing,
            "tier": tier,
            "reasons": company_reasons + technical_reasons + timing_reasons
        }

    def analyze_all_companies(self):
        """Score all companies and rank them."""
        print("\n🎯 ANALYZING ICP FIT FOR ALL COMPANIES")
        print("=" * 60)

        categories = self.companies_data.get("categories", {})

        for category, category_data in categories.items():
            companies = category_data.get("companies", [])

            for company in companies:
                scored = self.score_company(company, category)
                self.scored_companies.append(scored)

        # Sort by score
        self.scored_companies.sort(key=lambda x: x["total_score"], reverse=True)

        # Print top companies by tier
        self.print_tier_summary()

    def print_tier_summary(self):
        """Print companies grouped by tier."""
        tiers = {}
        for company in self.scored_companies:
            tier = company["tier"]
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(company)

        for tier in ["Tier 1 - Immediate Priority", "Tier 2 - High Priority",
                     "Tier 3 - Medium Priority", "Tier 4 - Low Priority"]:
            if tier in tiers:
                print(f"\n🎯 {tier} ({len(tiers[tier])} companies)")
                print("-" * 60)

                for company in tiers[tier][:10]:  # Show top 10 per tier
                    print(f"\n  📊 {company['name']} (Score: {company['total_score']})")
                    print(f"     Category: {company['category']}")
                    print(f"     Valuation: {company['valuation']}")
                    print(f"     Why prioritized:")
                    for reason in company['reasons'][:3]:
                        print(f"       • {reason}")

                if len(tiers[tier]) > 10:
                    print(f"\n     ... and {len(tiers[tier]) - 10} more")

    def export_to_csv(self, filename: str = "icp_scored_companies.csv"):
        """Export scored companies to CSV."""
        filepath = os.path.join(os.path.dirname(__file__), '../../data/companies/', filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'name', 'tier', 'total_score', 'category',
                'company_fit_score', 'technical_fit_score', 'timing_score',
                'valuation', 'description', 'research_feature', 'reasons'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for company in self.scored_companies:
                # Convert reasons list to string
                company_copy = company.copy()
                company_copy['reasons'] = ' | '.join(company_copy['reasons'])
                writer.writerow(company_copy)

        print(f"\n✅ Exported to: {filepath}")

    def get_target_personas(self, tier: str = "Tier 1"):
        """Get target personas for outreach."""
        print(f"\n👥 TARGET PERSONAS FOR {tier.upper()}")
        print("=" * 60)

        # Technical Champions
        print("\n🎯 PRIMARY TARGETS (Technical Champions):")
        print("-" * 40)
        technical_titles = [
            "ML Engineer",
            "Machine Learning Engineer",
            "AI Engineer",
            "Staff Engineer - AI/ML",
            "Principal Engineer - AI",
            "Senior ML Engineer",
            "Head of AI",
            "Head of Machine Learning",
            "Director of AI/ML"
        ]
        for title in technical_titles:
            print(f"  • {title}")

        # Decision Makers
        print("\n💼 DECISION MAKERS:")
        print("-" * 40)
        decision_titles = [
            "CTO",
            "VP Engineering",
            "VP of AI",
            "Director of Engineering",
            "Head of Engineering",
            "Engineering Manager - AI/ML"
        ]
        for title in decision_titles:
            print(f"  • {title}")

        # LinkedIn Search Queries
        print("\n🔍 LINKEDIN SEARCH QUERIES:")
        print("-" * 40)

        tier_companies = [c for c in self.scored_companies if c['tier'] == tier][:5]

        for company in tier_companies:
            print(f"\n  Company: {company['name']}")
            print(f"  Search: (company:\"{company['name']}\") AND (title:\"ML Engineer\" OR title:\"AI Engineer\" OR title:\"CTO\")")


def main():
    parser = argparse.ArgumentParser(description="Score and prioritize ICP companies")
    parser.add_argument("command",
                       choices=["analyze", "export", "personas"],
                       help="analyze: Score all | export: Export CSV | personas: Show target personas")

    args = parser.parse_args()
    scorer = ICPScorer()

    if args.command == "analyze":
        scorer.analyze_all_companies()

        print("\n" + "=" * 60)
        print("💡 RECOMMENDATIONS:")
        print("=" * 60)
        print("\n1. Focus on Tier 1 companies first (highest ROI)")
        print("2. Find ML Engineers and CTOs at these companies")
        print("3. Look for timing signals (hiring, funding, product launches)")
        print("4. Personalize outreach based on their use case")
        print("5. Export to CSV for CRM import")

    elif args.command == "export":
        scorer.analyze_all_companies()
        scorer.export_to_csv()
        print("\n📊 Use this CSV to:")
        print("  • Import scoring into Attio")
        print("  • Prioritize outreach")
        print("  • Track conversion by tier")

    elif args.command == "personas":
        scorer.analyze_all_companies()
        scorer.get_target_personas("Tier 1 - Immediate Priority")


if __name__ == "__main__":
    main()