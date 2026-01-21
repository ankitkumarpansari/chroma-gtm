#!/usr/bin/env python3
"""
Enrich NYC Companies with Domain Names

Uses Sumble API to find domain names for companies in the NYC dinner list,
then updates the company records in Attio.

Usage:
    python scripts/sync/enrich_nyc_domains.py
    python scripts/sync/enrich_nyc_domains.py --dry-run
    python scripts/sync/enrich_nyc_domains.py --limit 20
"""

import os
import requests
import time
import argparse
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
ATTIO_API_KEY = os.getenv("ATTIO_API_KEY")
SUMBLE_API_KEY = None

# Try to load Sumble API key
sumble_key_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "credentials/sumble_api_key.txt")
if os.path.exists(sumble_key_path):
    with open(sumble_key_path, 'r') as f:
        SUMBLE_API_KEY = f.read().strip()

ATTIO_BASE_URL = "https://api.attio.com/v2"
SUMBLE_BASE_URL = "https://api.sumble.com/v1"

# NYC list ID
NYC_LIST_ID = "830b2e34-a75c-45b9-9070-651c2714c0f6"

RATE_LIMIT_DELAY = 0.3


class DomainEnricher:
    """Enrich companies with domain names."""
    
    def __init__(self):
        self.attio_headers = {
            "Authorization": f"Bearer {ATTIO_API_KEY}",
            "Content-Type": "application/json"
        }
        self.sumble_headers = {
            "Authorization": f"Bearer {SUMBLE_API_KEY}",
            "Content-Type": "application/json"
        }
        self.last_request_time = 0
        self.stats = {
            "total": 0,
            "already_has_domain": 0,
            "enriched": 0,
            "not_found": 0,
            "failed": 0,
        }
        
        # Known domain mappings for common companies
        self.known_domains = {
            "blackrock": "blackrock.com",
            "morgan stanley": "morganstanley.com",
            "bloomberg": "bloomberg.com",
            "jane street": "janestreet.com",
            "honeyhive": "honeyhive.ai",
            "monk.io": "monk.io",
            "datafold": "datafold.com",
            "shaped": "shaped.ai",
            "general intelligence": "generalintelligence.com",
            "gushwork": "gushwork.ai",
            "sandbar": "sandbar.ai",
            "peloton": "onepeloton.com",
            "superblocks": "superblocks.com",
            "connatix": "connatix.com",
            "rightway": "rightwayhealthcare.com",
            "termsheet": "termsheet.io",
            "browser company": "thebrowser.company",
            "ramp": "ramp.com",
            "complex media": "complex.com",
            "medidata": "medidata.com",
            "xai": "x.ai",
            "novo": "novo.co",
            "1uphealth": "1up.health",
            "able": "able.co",
            "ibm": "ibm.com",
            "opentrons": "opentrons.com",
            "sj innovation": "sjinnovation.com",
            "halo media": "halomedia.com",
            "accenture": "accenture.com",
            "deloitte": "deloitte.com",
            "mintlify": "mintlify.com",
            "warp": "warp.dev",
            "triple whale": "triplewhale.com",
            "compound vc": "compound.vc",
            "lux capital": "luxcapital.com",
            "every": "every.to",
            "travelers": "travelers.com",
            "salesforce": "salesforce.com",
            "optum": "optum.com",
            "stubhub": "stubhub.com",
            "berkadia": "berkadia.com",
            "pelago": "pelagohealth.com",
            "farmevo": "farmevo.io",
            "infuy": "infuy.com",
            "tinycloud": "tiny.cloud",
            "sportsrecruits": "sportsrecruits.com",
            "brownstone": "brownstoneinvestmentgroup.com",
            "rab lighting": "rablighting.com",
            "sutra": "sutra.co",
            "cubby law": "cubbylaw.com",
            "hellohero": "hellohero.co",
            "gostork": "gostork.com",
            "storytime": "storytime.ai",
            "latham": "lw.com",
            "theirstory": "theirstory.io",
            "octane lending": "octane.co",
            "hexaview": "hexaviewtech.com",
            "larroude": "larroude.com",
            "famous allstars": "famousallstars.com",
            "promptlayer": "promptlayer.com",
            "arize": "arize.com",
            "brightwave": "brightwave.io",
            "mongodb": "mongodb.com",
            "nx1 capital": "nx1capital.com",
            "two sigma": "twosigma.com",
            "d.e. shaw": "deshaw.com",
            "citadel": "citadel.com",
            "point72": "point72.com",
            "bridgewater": "bridgewater.com",
            "qube research": "qube-rt.com",
            "quantamind": "quantamind.com",
            "quantstruct": "quantstruct.com",
            "irage": "iragecapital.com",
            "quantit": "quantit.io",
            "quantly": "quantly.ai",
            "quantiphi": "quantiphi.com",
            "justworks": "justworks.com",
            "brex": "brex.com",
            "hebbia": "hebbia.ai",
            "mastercard": "mastercard.com",
            "perplexity": "perplexity.ai",
            "hex": "hex.tech",
            "hasura": "hasura.io",
            "tinder": "tinder.com",
            "nixtla": "nixtla.io",
            "humanloop": "humanloop.com",
            "galileo": "rungalileo.io",
            "ionic commerce": "ioniccommerce.com",
            "writer": "writer.com",
            "datadog": "datadoghq.com",
            "method financial": "methodfi.com",
            "clerk": "clerk.com",
            "browserbase": "browserbase.com",
            "south park commons": "southparkcommons.com",
            "clay": "clay.com",
            "neon": "neon.tech",
            "letta": "letta.ai",
            "vercel": "vercel.com",
            "stride": "stride.build",
            "jp morgan": "jpmorgan.com",
            "rogo": "rogodata.com",
            "koyfin": "koyfin.com",
            "spotnana": "spotnana.com",
            "harvey": "harvey.ai",
            "digitalocean": "digitalocean.com",
            "lemonade": "lemonade.com",
            "notion": "notion.so",
            "attentive": "attentive.com",
            "sprinklr": "sprinklr.com",
            "oscar health": "hioscar.com",
            "spring health": "springhealth.com",
            "compass": "compass.com",
            "alphasense": "alpha-sense.com",
            "dataminr": "dataminr.com",
            "yipitdata": "yipitdata.com",
        }
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def get_nyc_companies(self) -> List[Dict]:
        """Get all companies from NYC list."""
        self._rate_limit()
        
        response = requests.post(
            f"{ATTIO_BASE_URL}/lists/{NYC_LIST_ID}/entries/query",
            headers=self.attio_headers,
            json={"limit": 200}
        )
        
        if response.status_code != 200:
            print(f"Error fetching list: {response.status_code}")
            return []
        
        entries = response.json().get("data", [])
        companies = []
        
        for entry in entries:
            record_id = entry.get("parent_record_id")
            if record_id:
                # Fetch full company record
                self._rate_limit()
                resp = requests.get(
                    f"{ATTIO_BASE_URL}/objects/companies/records/{record_id}",
                    headers=self.attio_headers
                )
                if resp.status_code == 200:
                    record = resp.json().get("data", {})
                    values = record.get("values", {})
                    name_list = values.get("name", [])
                    name = name_list[0].get("value", "") if name_list else ""
                    domains = values.get("domains", [])
                    domain = domains[0].get("domain", "") if domains else ""
                    
                    companies.append({
                        "record_id": record_id,
                        "name": name,
                        "domain": domain
                    })
        
        return companies
    
    def lookup_domain_locally(self, company_name: str) -> Optional[str]:
        """Look up domain from known mappings."""
        name_lower = company_name.lower()
        
        for key, domain in self.known_domains.items():
            if key in name_lower:
                return domain
        
        return None
    
    def lookup_domain_sumble(self, company_name: str) -> Optional[str]:
        """Look up domain using Sumble API."""
        if not SUMBLE_API_KEY:
            return None
        
        self._rate_limit()
        
        try:
            response = requests.post(
                f"{SUMBLE_BASE_URL}/organizations/enrich",
                headers=self.sumble_headers,
                json={
                    "name": company_name,
                    "filters": {
                        "min_employees": 1
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                org = data.get("organization", {})
                domain = org.get("domain")
                if domain:
                    return domain
        except Exception as e:
            pass
        
        return None
    
    def update_company_domain(self, record_id: str, domain: str) -> bool:
        """Update company domain in Attio."""
        self._rate_limit()
        
        response = requests.patch(
            f"{ATTIO_BASE_URL}/objects/companies/records/{record_id}",
            headers=self.attio_headers,
            json={
                "data": {
                    "values": {
                        "domains": [{"domain": domain}]
                    }
                }
            }
        )
        
        return response.status_code == 200
    
    def enrich_all(self, dry_run: bool = False, limit: int = None) -> Dict:
        """Enrich all companies with domains."""
        print("\n" + "=" * 60)
        print("🌐 ENRICHING NYC COMPANIES WITH DOMAINS")
        print("=" * 60)
        
        print("\n📂 Fetching companies from NYC list...")
        companies = self.get_nyc_companies()
        print(f"   Found {len(companies)} companies")
        
        if limit:
            companies = companies[:limit]
            print(f"   Limited to {limit} companies")
        
        self.stats["total"] = len(companies)
        
        # Separate companies with and without domains
        needs_enrichment = []
        for c in companies:
            if c.get("domain"):
                self.stats["already_has_domain"] += 1
            else:
                needs_enrichment.append(c)
        
        print(f"\n   ✅ Already have domain: {self.stats['already_has_domain']}")
        print(f"   ❌ Need enrichment: {len(needs_enrichment)}")
        
        if not needs_enrichment:
            print("\n✅ All companies already have domains!")
            return self.stats
        
        print(f"\n{'🧪 DRY RUN' if dry_run else '🔄 Enriching'}...\n")
        
        for i, company in enumerate(needs_enrichment, 1):
            name = company.get("name", "Unknown")
            record_id = company.get("record_id")
            
            # Try local lookup first
            domain = self.lookup_domain_locally(name)
            source = "local"
            
            # If not found locally, try Sumble
            if not domain and SUMBLE_API_KEY:
                domain = self.lookup_domain_sumble(name)
                source = "sumble"
            
            if domain:
                if dry_run:
                    print(f"   [{i:3d}/{len(needs_enrichment)}] 🧪 {name[:30]:<30} → {domain} ({source})")
                else:
                    if self.update_company_domain(record_id, domain):
                        print(f"   [{i:3d}/{len(needs_enrichment)}] ✅ {name[:30]:<30} → {domain} ({source})")
                        self.stats["enriched"] += 1
                    else:
                        print(f"   [{i:3d}/{len(needs_enrichment)}] ❌ {name[:30]:<30} (update failed)")
                        self.stats["failed"] += 1
            else:
                print(f"   [{i:3d}/{len(needs_enrichment)}] ⚠️  {name[:30]:<30} (not found)")
                self.stats["not_found"] += 1
        
        return self.stats
    
    def print_summary(self):
        """Print enrichment summary."""
        print("\n" + "=" * 60)
        print("📊 ENRICHMENT SUMMARY")
        print("=" * 60)
        print(f"   📋 Total companies:      {self.stats['total']}")
        print(f"   ✅ Already had domain:   {self.stats['already_has_domain']}")
        print(f"   🌐 Enriched:             {self.stats['enriched']}")
        print(f"   ⚠️  Not found:            {self.stats['not_found']}")
        print(f"   ❌ Failed:               {self.stats['failed']}")


def main():
    parser = argparse.ArgumentParser(description="Enrich NYC companies with domains")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--limit", type=int, help="Limit number of companies")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🌐 NYC COMPANY DOMAIN ENRICHMENT")
    print("=" * 60)
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Sumble API: {'✅ Available' if SUMBLE_API_KEY else '❌ Not configured'}")
    
    enricher = DomainEnricher()
    enricher.enrich_all(dry_run=args.dry_run, limit=args.limit)
    
    if not args.dry_run:
        enricher.print_summary()


if __name__ == "__main__":
    main()

