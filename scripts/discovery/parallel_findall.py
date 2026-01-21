"""
Parallel FindAll API Integration

A client for the Parallel FindAll API - a web-scale entity discovery system
that turns natural language queries into structured, enriched databases.

Documentation: https://docs.parallel.ai/findall-api/findall-quickstart
"""

import os
import time
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

# API Configuration
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
BASE_URL = "https://api.parallel.ai/v1beta/findall"
BETA_HEADER = "findall-2025-09-15"


@dataclass
class MatchCondition:
    """A condition that candidates must satisfy to be matched."""
    name: str
    description: str


@dataclass
class Citation:
    """A source citation for a data point."""
    title: str
    url: str
    excerpts: List[str] = field(default_factory=list)


@dataclass
class Basis:
    """Reasoning and citations for a matched field."""
    field: str
    citations: List[Citation]
    reasoning: str
    confidence: str


@dataclass
class Candidate:
    """A discovered entity candidate."""
    candidate_id: str
    name: str
    url: str
    description: str
    match_status: str
    output: Dict[str, Any]
    basis: List[Basis]

    @classmethod
    def from_dict(cls, data: dict) -> "Candidate":
        basis_list = []
        for b in data.get("basis", []):
            citations = [
                Citation(
                    title=c.get("title", ""),
                    url=c.get("url", ""),
                    excerpts=c.get("excerpts", [])
                )
                for c in b.get("citations", [])
            ]
            basis_list.append(Basis(
                field=b.get("field", ""),
                citations=citations,
                reasoning=b.get("reasoning", ""),
                confidence=b.get("confidence", "")
            ))
        
        return cls(
            candidate_id=data.get("candidate_id", ""),
            name=data.get("name", ""),
            url=data.get("url", ""),
            description=data.get("description", ""),
            match_status=data.get("match_status", ""),
            output=data.get("output", {}),
            basis=basis_list
        )


class ParallelFindAllClient:
    """
    Client for interacting with the Parallel FindAll API.
    
    FindAll is a web-scale entity discovery system that:
    - Generates candidates from web data
    - Evaluates candidates against match conditions
    - Enriches matched candidates with additional data
    
    Common use cases:
    - Market Mapping: "FindAll fintech companies offering earned-wage access in Brazil"
    - Competitive Intelligence: "FindAll AI infrastructure providers that raised Series B"
    - Lead Generation: "FindAll residential roofing companies in Charlotte, NC"
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PARALLEL_API_KEY
        if not self.api_key:
            raise ValueError(
                "PARALLEL_API_KEY not found. Set it as an environment variable "
                "or pass it to the constructor."
            )
        
        self.headers = {
            "x-api-key": self.api_key,
            "parallel-beta": BETA_HEADER,
            "Content-Type": "application/json"
        }
    
    def ingest(self, objective: str) -> Dict[str, Any]:
        """
        Convert a natural language query into a structured schema.
        
        This endpoint automatically extracts:
        - What type of entities to search for (companies, people, products, etc.)
        - Match conditions that must be satisfied
        - Optional enrichment suggestions
        
        Args:
            objective: Natural language query describing what to find
            
        Returns:
            Structured schema with entity_type and match_conditions
            
        Example:
            >>> client.ingest("FindAll AI companies that raised Series A in 2024")
        """
        response = requests.post(
            f"{BASE_URL}/ingest",
            headers=self.headers,
            json={"objective": objective}
        )
        response.raise_for_status()
        return response.json()
    
    def create_run(
        self,
        objective: str,
        entity_type: str,
        match_conditions: List[Dict[str, str]],
        generator: str = "core",
        match_limit: int = 10,
        enrichments: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Start a FindAll run to discover and evaluate candidates.
        
        Args:
            objective: Natural language description of the search
            entity_type: Type of entities to find (e.g., "companies", "people")
            match_conditions: List of conditions candidates must satisfy
            generator: Generator tier - "base", "core", or "pro"
            match_limit: Maximum number of matched candidates to return
            enrichments: Optional additional fields to extract for matches
            
        Returns:
            findall_id for tracking the run
            
        Generator options:
        - base: Fastest, lower quality
        - core: Balanced (recommended)
        - pro: Highest quality, slower
        """
        payload = {
            "objective": objective,
            "entity_type": entity_type,
            "match_conditions": match_conditions,
            "generator": generator,
            "match_limit": match_limit
        }
        
        if enrichments:
            payload["enrichments"] = enrichments
        
        response = requests.post(
            f"{BASE_URL}/runs",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["findall_id"]
    
    def get_status(self, findall_id: str) -> Dict[str, Any]:
        """
        Check the status of a FindAll run.
        
        Args:
            findall_id: The ID returned from create_run
            
        Returns:
            Status object with:
            - status: "running", "completed", "failed"
            - is_active: Whether the run is still processing
            - metrics: Counts of generated and matched candidates
        """
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_results(self, findall_id: str) -> Dict[str, Any]:
        """
        Get the final results of a FindAll run.
        
        Args:
            findall_id: The ID returned from create_run
            
        Returns:
            Results including matched candidates with:
            - candidate_id, name, url, description
            - match_status
            - output: Match condition results
            - basis: Reasoning and citations for each field
        """
        response = requests.get(
            f"{BASE_URL}/runs/{findall_id}/result",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self,
        findall_id: str,
        poll_interval: int = 5,
        timeout: int = 300,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Poll until a FindAll run completes.
        
        Args:
            findall_id: The ID returned from create_run
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            verbose: Print progress updates
            
        Returns:
            Final status object
        """
        start_time = time.time()
        
        while True:
            status = self.get_status(findall_id)
            
            if verbose:
                metrics = status.get("status", {}).get("metrics", {})
                print(f"Status: {status['status']['status']} | "
                      f"Generated: {metrics.get('generated_candidates_count', 0)} | "
                      f"Matched: {metrics.get('matched_candidates_count', 0)}")
            
            if not status["status"]["is_active"]:
                return status
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"FindAll run {findall_id} did not complete within {timeout}s")
            
            time.sleep(poll_interval)
    
    def find_all(
        self,
        query: str,
        generator: str = "core",
        match_limit: int = 10,
        enrichments: Optional[List[Dict[str, str]]] = None,
        poll_interval: int = 5,
        timeout: int = 300,
        verbose: bool = True
    ) -> List[Candidate]:
        """
        Complete workflow: ingest query, run search, and return matched candidates.
        
        This is a convenience method that combines all steps:
        1. Ingest: Convert natural language to structured schema
        2. Create Run: Start the search
        3. Wait: Poll until completion
        4. Get Results: Return matched candidates
        
        Args:
            query: Natural language query (e.g., "FindAll AI startups in SF")
            generator: "base", "core", or "pro"
            match_limit: Maximum matches to return
            enrichments: Optional additional fields to extract
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            verbose: Print progress updates
            
        Returns:
            List of matched Candidate objects
            
        Example:
            >>> candidates = client.find_all(
            ...     "FindAll portfolio companies of a]6z founded after 2020",
            ...     match_limit=20
            ... )
            >>> for c in candidates:
            ...     print(f"{c.name}: {c.url}")
        """
        # Step 1: Ingest
        if verbose:
            print(f"Ingesting query: {query}")
        
        schema = self.ingest(query)
        
        if verbose:
            print(f"Entity type: {schema['entity_type']}")
            print(f"Match conditions: {len(schema['match_conditions'])}")
            for mc in schema['match_conditions']:
                print(f"  - {mc['name']}: {mc['description']}")
        
        # Step 2: Create Run
        findall_id = self.create_run(
            objective=schema["objective"],
            entity_type=schema["entity_type"],
            match_conditions=schema["match_conditions"],
            generator=generator,
            match_limit=match_limit,
            enrichments=enrichments
        )
        
        if verbose:
            print(f"\nStarted run: {findall_id}")
        
        # Step 3: Wait for completion
        self.wait_for_completion(
            findall_id,
            poll_interval=poll_interval,
            timeout=timeout,
            verbose=verbose
        )
        
        # Step 4: Get Results
        results = self.get_results(findall_id)
        
        candidates = [
            Candidate.from_dict(c) 
            for c in results.get("candidates", [])
        ]
        
        if verbose:
            print(f"\nFound {len(candidates)} matched candidates")
        
        return candidates


def save_results_to_json(candidates: List[Candidate], filepath: str):
    """Save candidate results to a JSON file."""
    data = []
    for c in candidates:
        data.append({
            "candidate_id": c.candidate_id,
            "name": c.name,
            "url": c.url,
            "description": c.description,
            "match_status": c.match_status,
            "output": c.output,
            "basis": [
                {
                    "field": b.field,
                    "reasoning": b.reasoning,
                    "confidence": b.confidence,
                    "citations": [
                        {"title": cit.title, "url": cit.url, "excerpts": cit.excerpts}
                        for cit in b.citations
                    ]
                }
                for b in c.basis
            ]
        })
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(data)} candidates to {filepath}")


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ParallelFindAllClient()
    
    # Example: Find companies using Chroma (vector database)
    query = "FindAll companies that are using Chroma vector database in production"
    
    print("=" * 60)
    print("Parallel FindAll API Demo")
    print("=" * 60)
    print(f"\nQuery: {query}\n")
    
    try:
        candidates = client.find_all(
            query=query,
            generator="core",
            match_limit=10,
            verbose=True
        )
        
        print("\n" + "=" * 60)
        print("Results")
        print("=" * 60)
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. {candidate.name}")
            print(f"   URL: {candidate.url}")
            print(f"   Description: {candidate.description}")
            
            if candidate.basis:
                print("   Evidence:")
                for b in candidate.basis:
                    print(f"     - {b.field}: {b.reasoning} (confidence: {b.confidence})")
        
        # Save results
        save_results_to_json(candidates, "parallel_findall_results.json")
        
    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
    except Exception as e:
        print(f"Error: {e}")
