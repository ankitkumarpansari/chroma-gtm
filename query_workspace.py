#!/usr/bin/env python3
"""
Chroma Workspace Query Tool
===========================
Search the indexed workspace to find relevant scripts, docs, and data.

Usage:
    python query_workspace.py "your search query"
    python query_workspace.py "sync companies to HubSpot" --type scripts
    python query_workspace.py "LinkedIn strategy" --type docs
    python query_workspace.py "Pinecone customers" --type companies

Options:
    --type: Filter by type (scripts, docs, companies, meetings, all)
    --limit: Number of results (default: 5)
    --show-content: Show full content of results

⚠️ AI AGENTS: Run this BEFORE creating any new script to check if it exists!
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("❌ chromadb not installed. Run: pip install chromadb")
    exit(1)

# Configuration
WORKSPACE_ROOT = Path(__file__).parent
CHROMA_PATH = WORKSPACE_ROOT / ".chroma_workspace_index"

# Check if index exists
if not CHROMA_PATH.exists():
    print("❌ Workspace not indexed yet. Run: python index_workspace.py")
    exit(1)

# Initialize Chroma client
client = chromadb.PersistentClient(path=str(CHROMA_PATH))
ef = embedding_functions.DefaultEmbeddingFunction()


def get_collection(name: str):
    """Get a collection by name."""
    try:
        return client.get_collection(name, embedding_function=ef)
    except:
        return None


def search_scripts(query: str, n_results: int = 5, show_content: bool = False):
    """Search for scripts matching the query."""
    collection = get_collection("scripts")
    if not collection:
        print("   ⚠️ Scripts collection not found. Run index_workspace.py first.")
        return []
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n🔍 SCRIPTS matching: '{query}'")
    print("-" * 60)
    
    if not results['ids'][0]:
        print("   No matching scripts found.")
        return []
    
    for i, (id, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        similarity = max(0, 1 - distance)  # Convert distance to similarity
        
        print(f"\n{i+1}. 📜 {metadata['path']}")
        print(f"   Category: {metadata['category']}")
        print(f"   Similarity: {similarity:.1%}")
        print(f"   Purpose: {metadata.get('purpose', 'N/A')[:100]}...")
        
        if metadata.get('functions'):
            print(f"   Functions: {metadata['functions'][:80]}...")
        
        if show_content and results['documents']:
            print(f"\n   --- Content Preview ---")
            print(f"   {results['documents'][0][i][:500]}...")
    
    return results


def search_docs(query: str, n_results: int = 5, show_content: bool = False):
    """Search for documentation matching the query."""
    collection = get_collection("docs")
    if not collection:
        print("   ⚠️ Docs collection not found. Run index_workspace.py first.")
        return []
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n📚 DOCUMENTATION matching: '{query}'")
    print("-" * 60)
    
    if not results['ids'][0]:
        print("   No matching documentation found.")
        return []
    
    for i, (id, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        similarity = max(0, 1 - distance)
        
        print(f"\n{i+1}. 📄 {metadata['path']}")
        print(f"   Topic: {metadata['topic']}")
        print(f"   Section: {metadata.get('section', 'N/A')}")
        print(f"   Similarity: {similarity:.1%}")
        
        if show_content and results['documents']:
            print(f"\n   --- Content Preview ---")
            content = results['documents'][0][i][:500]
            print(f"   {content}...")
    
    return results


def search_companies(query: str, n_results: int = 10, show_content: bool = False):
    """Search for companies matching the query."""
    collection = get_collection("companies")
    if not collection:
        print("   ⚠️ Companies collection not found. Run index_workspace.py first.")
        return []
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n🏢 COMPANIES matching: '{query}'")
    print("-" * 60)
    
    if not results['ids'][0]:
        print("   No matching companies found.")
        return []
    
    for i, (id, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        similarity = max(0, 1 - distance)
        
        print(f"\n{i+1}. 🏢 {metadata.get('company_name', 'Unknown')}")
        print(f"   Source: {metadata['source_file']}")
        print(f"   Industry: {metadata.get('industry', 'N/A')}")
        print(f"   Tier: {metadata.get('tier', 'N/A')}")
        print(f"   Similarity: {similarity:.1%}")
    
    return results


def search_meetings(query: str, n_results: int = 5, show_content: bool = False):
    """Search for meeting notes matching the query."""
    collection = get_collection("meetings")
    if not collection:
        print("   ⚠️ Meetings collection not found. Run index_workspace.py first.")
        return []
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n📅 MEETINGS matching: '{query}'")
    print("-" * 60)
    
    if not results['ids'][0]:
        print("   No matching meetings found.")
        return []
    
    for i, (id, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        similarity = max(0, 1 - distance)
        
        print(f"\n{i+1}. 📅 {metadata['path']}")
        print(f"   Date: {metadata['date']}")
        print(f"   Topic: {metadata.get('topic', 'N/A')}")
        print(f"   Similarity: {similarity:.1%}")
        
        if show_content and results['documents']:
            print(f"\n   --- Content Preview ---")
            content = results['documents'][0][i][:500]
            print(f"   {content}...")
    
    return results


def search_all(query: str, n_results: int = 3, show_content: bool = False):
    """Search all collections."""
    search_scripts(query, n_results, show_content)
    search_docs(query, n_results, show_content)
    search_companies(query, n_results, show_content)
    search_meetings(query, n_results, show_content)


def show_stats():
    """Show index statistics."""
    print("\n📊 WORKSPACE INDEX STATS")
    print("=" * 60)
    
    collections = client.list_collections()
    total = 0
    for col in collections:
        count = col.count()
        total += count
        print(f"   {col.name}: {count} items")
    
    print(f"\n   Total indexed items: {total}")
    print(f"   Index location: {CHROMA_PATH}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Search the indexed workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_workspace.py "sync companies to HubSpot"
  python query_workspace.py "LinkedIn automation" --type scripts
  python query_workspace.py "competitor analysis" --type docs
  python query_workspace.py "AI startup" --type companies --limit 10
  python query_workspace.py --stats
        """
    )
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--type", "-t", choices=["scripts", "docs", "companies", "meetings", "all"],
                       default="all", help="Type of content to search")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")
    parser.add_argument("--show-content", "-c", action="store_true", help="Show content preview")
    parser.add_argument("--stats", "-s", action="store_true", help="Show index statistics")
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
        return
    
    if not args.query:
        parser.print_help()
        print("\n⚠️ Please provide a search query or use --stats")
        return
    
    print("\n" + "=" * 60)
    print("🔎 WORKSPACE SEARCH")
    print("=" * 60)
    print(f"   Query: {args.query}")
    print(f"   Type: {args.type}")
    print(f"   Limit: {args.limit}")
    
    if args.type == "all":
        search_all(args.query, args.limit, args.show_content)
    elif args.type == "scripts":
        search_scripts(args.query, args.limit, args.show_content)
    elif args.type == "docs":
        search_docs(args.query, args.limit, args.show_content)
    elif args.type == "companies":
        search_companies(args.query, args.limit, args.show_content)
    elif args.type == "meetings":
        search_meetings(args.query, args.limit, args.show_content)
    
    print("\n" + "=" * 60)
    print("💡 TIP: If you found what you need, READ the file before creating new code!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()


