"""
Quick test script for Parallel FindAll API

Run this after setting your PARALLEL_API_KEY in .env
"""

from parallel_findall import ParallelFindAllClient
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test that the API key is valid by running the ingest endpoint."""
    
    api_key = os.getenv("PARALLEL_API_KEY")
    
    if not api_key or api_key == "your-api-key-here":
        print("❌ Error: Please set your PARALLEL_API_KEY in .env file")
        print("\n   1. Get your API key from https://parallel.ai")
        print("   2. Edit .env and replace 'your-api-key-here' with your key")
        return False
    
    print("✓ API key found")
    print(f"  Key prefix: {api_key[:8]}...")
    
    try:
        client = ParallelFindAllClient()
        
        # Test with a simple ingest call (cheapest operation)
        print("\n→ Testing API connection with ingest endpoint...")
        
        schema = client.ingest("FindAll AI companies in San Francisco")
        
        print("✓ API connection successful!\n")
        print("Parsed schema:")
        print(f"  Entity type: {schema['entity_type']}")
        print(f"  Match conditions:")
        for mc in schema['match_conditions']:
            print(f"    - {mc['name']}: {mc['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False


def run_sample_query():
    """Run a sample FindAll query relevant to your Chroma GTM project."""
    
    client = ParallelFindAllClient()
    
    # Query relevant to your project - finding companies using vector databases
    query = "FindAll companies that are building AI applications with vector databases like Chroma or Pinecone"
    
    print("=" * 60)
    print("Running Sample FindAll Query")
    print("=" * 60)
    print(f"\nQuery: {query}\n")
    
    candidates = client.find_all(
        query=query,
        generator="base",  # Use 'base' for testing (faster, cheaper)
        match_limit=5,     # Limit results for testing
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print(f"Found {len(candidates)} companies")
    print("=" * 60)
    
    for i, c in enumerate(candidates, 1):
        print(f"\n{i}. {c.name}")
        print(f"   URL: {c.url}")
        print(f"   {c.description}")
    
    return candidates


if __name__ == "__main__":
    print("=" * 60)
    print("Parallel FindAll API - Connection Test")
    print("=" * 60 + "\n")
    
    if test_connection():
        print("\n" + "-" * 60)
        response = input("\nWould you like to run a sample query? (y/n): ")
        
        if response.lower() == 'y':
            run_sample_query()
    else:
        print("\nPlease fix the API key issue and try again.")




