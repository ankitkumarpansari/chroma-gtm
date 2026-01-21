#!/usr/bin/env python3
"""
Workspace Query Tool for Chroma GTM

Purpose: Search the indexed workspace to find relevant scripts, docs, and data.
         Run this BEFORE creating any new scripts to check what already exists.

Usage:
    python scripts/chroma/query_workspace.py "sync companies to hubspot"
    python scripts/chroma/query_workspace.py "linkedin automation" --type scripts
    python scripts/chroma/query_workspace.py "competitor analysis" --type docs
    python scripts/chroma/query_workspace.py "pinecone customers" --type data

Options:
    --type     Filter by type: scripts, docs, data, meetings, all (default: all)
    --limit    Number of results (default: 5)
    --verbose  Show full content of results

Requires:
    pip install chromadb
    First run: python scripts/chroma/index_workspace.py
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("❌ chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

# Configuration
CHROMA_PATH = PROJECT_ROOT / ".chroma_workspace_index"

# Collection names
COLLECTIONS = {
    "scripts": "gtm_scripts",
    "docs": "gtm_docs",
    "data": "gtm_data",
    "meetings": "gtm_meetings"
}


def get_client():
    """Get Chroma client"""
    if not CHROMA_PATH.exists():
        print("❌ Workspace not indexed yet!")
        print("   Run: python scripts/chroma/index_workspace.py")
        sys.exit(1)
    
    return chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False)
    )


def format_result(result: dict, index: int, verbose: bool = False) -> str:
    """Format a single search result for display"""
    metadata = result.get("metadata", {})
    distance = result.get("distance", 0)
    similarity = max(0, 1 - distance)  # Convert distance to similarity
    
    path = metadata.get("path", "Unknown")
    result_type = metadata.get("type", "unknown")
    category = metadata.get("category", "")
    
    output = []
    output.append(f"\n{'─' * 60}")
    output.append(f"📄 Result {index + 1}: {path}")
    output.append(f"   Type: {result_type} | Category: {category} | Similarity: {similarity:.1%}")
    
    # Type-specific metadata
    if result_type == "script":
        purpose = metadata.get("purpose", "")
        functions = metadata.get("functions", "")
        if purpose:
            output.append(f"   Purpose: {purpose[:150]}...")
        if functions:
            output.append(f"   Functions: {functions[:100]}")
    
    elif result_type == "documentation":
        section = metadata.get("section", "")
        if section:
            output.append(f"   Section: {section}")
    
    elif result_type == "data":
        item_count = metadata.get("item_count", 0)
        data_type = metadata.get("data_type", "")
        output.append(f"   Items: {item_count} | Format: {data_type}")
    
    elif result_type == "meeting":
        date = metadata.get("date", "")
        topic = metadata.get("topic", "")
        output.append(f"   Date: {date} | Topic: {topic}")
    
    if verbose:
        document = result.get("document", "")
        if document:
            output.append(f"\n   Content Preview:")
            output.append("   " + "-" * 40)
            # Indent content
            for line in document[:1000].split("\n")[:20]:
                output.append(f"   {line}")
            if len(document) > 1000:
                output.append("   ...")
    
    return "\n".join(output)


def search_collection(client, collection_name: str, query: str, n_results: int = 5) -> list:
    """Search a specific collection"""
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        return []
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Flatten results
    formatted = []
    if results and results.get("ids") and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i] if results.get("documents") else "",
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else 0
            })
    
    return formatted


def search_all(client, query: str, n_results: int = 5) -> dict:
    """Search all collections"""
    all_results = {}
    
    for name, collection_name in COLLECTIONS.items():
        results = search_collection(client, collection_name, query, n_results)
        if results:
            all_results[name] = results
    
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Search GTM workspace for relevant scripts, docs, and data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "sync companies to hubspot"
  %(prog)s "linkedin automation" --type scripts
  %(prog)s "competitor analysis" --type docs --limit 10
  %(prog)s "pinecone customers" --verbose
        """
    )
    parser.add_argument("query", help="Search query (natural language)")
    parser.add_argument(
        "--type", "-t",
        choices=["scripts", "docs", "data", "meetings", "all"],
        default="all",
        help="Filter by type (default: all)"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=5,
        help="Number of results per type (default: 5)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show full content of results"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    client = get_client()
    
    print(f"\n🔍 Searching for: \"{args.query}\"")
    print("=" * 60)
    
    if args.type == "all":
        all_results = search_all(client, args.query, args.limit)
        
        if args.json:
            import json
            print(json.dumps(all_results, indent=2, default=str))
            return
        
        total_found = 0
        for type_name, results in all_results.items():
            if results:
                print(f"\n{'🔷' * 3} {type_name.upper()} {'🔷' * 3}")
                for i, result in enumerate(results):
                    print(format_result(result, i, args.verbose))
                    total_found += 1
        
        if total_found == 0:
            print("\n❌ No results found. Try a different query.")
            print("   Tip: Use natural language like 'how to sync data to CRM'")
        else:
            print(f"\n{'=' * 60}")
            print(f"✅ Found {total_found} relevant items")
    
    else:
        collection_name = COLLECTIONS.get(args.type)
        results = search_collection(client, collection_name, args.query, args.limit)
        
        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))
            return
        
        if results:
            print(f"\n{'🔷' * 3} {args.type.upper()} {'🔷' * 3}")
            for i, result in enumerate(results):
                print(format_result(result, i, args.verbose))
            print(f"\n{'=' * 60}")
            print(f"✅ Found {len(results)} {args.type}")
        else:
            print(f"\n❌ No {args.type} found matching your query.")
    
    print("\n💡 Tip: Read the top results before creating new scripts!")
    print(f"   Use: cat <path> to view file contents\n")


if __name__ == "__main__":
    main()
