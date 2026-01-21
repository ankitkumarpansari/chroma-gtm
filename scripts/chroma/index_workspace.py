"""
Workspace Indexer for Chroma GTM

Purpose: Index all scripts, docs, and data files into Chroma for semantic search.
         This enables AI agents to find relevant existing code before creating new scripts.

Usage:
    python scripts/chroma/index_workspace.py              # Full index
    python scripts/chroma/index_workspace.py --scripts    # Index only scripts
    python scripts/chroma/index_workspace.py --docs       # Index only docs
    python scripts/chroma/index_workspace.py --data       # Index only data

Requires:
    pip install chromadb
"""

import os
import sys
import glob
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

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
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Default sentence-transformers model

# Collection names
COLLECTIONS = {
    "scripts": "gtm_scripts",
    "docs": "gtm_docs", 
    "data": "gtm_data",
    "meetings": "gtm_meetings"
}


def get_client():
    """Get or create Chroma client with persistent storage"""
    return chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False)
    )


def extract_docstring(content: str) -> str:
    """Extract docstring from Python file"""
    # Match triple-quoted docstrings at the start of file
    match = re.search(r'^"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r"^'''(.*?)'''", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return "No docstring"


def extract_functions(content: str) -> list:
    """Extract function names from Python file"""
    return re.findall(r'def (\w+)\s*\(', content)


def extract_classes(content: str) -> list:
    """Extract class names from Python file"""
    return re.findall(r'class (\w+)\s*[\(:]', content)


def extract_imports(content: str) -> list:
    """Extract import statements"""
    imports = re.findall(r'^import (\w+)', content, re.MULTILINE)
    from_imports = re.findall(r'^from (\w+)', content, re.MULTILINE)
    return list(set(imports + from_imports))


def chunk_markdown(content: str, max_chunk_size: int = 2000) -> list:
    """Split markdown into chunks by headers"""
    chunks = []
    current_heading = "Introduction"
    current_content = []
    current_size = 0
    
    for line in content.split("\n"):
        # Check for headers
        if line.startswith("## "):
            if current_content:
                chunks.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content)
                })
            current_heading = line[3:].strip()
            current_content = [line]
            current_size = len(line)
        elif line.startswith("# "):
            if current_content:
                chunks.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content)
                })
            current_heading = line[2:].strip()
            current_content = [line]
            current_size = len(line)
        else:
            # Check if adding this line would exceed max size
            if current_size + len(line) > max_chunk_size and current_content:
                chunks.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content)
                })
                current_content = [line]
                current_size = len(line)
            else:
                current_content.append(line)
                current_size += len(line)
    
    # Don't forget the last chunk
    if current_content:
        chunks.append({
            "heading": current_heading,
            "content": "\n".join(current_content)
        })
    
    return chunks


def get_category_from_path(filepath: str) -> str:
    """Extract category from file path"""
    parts = Path(filepath).parts
    if "scripts" in parts:
        idx = parts.index("scripts")
        if idx + 1 < len(parts) and not parts[idx + 1].endswith(".py"):
            return parts[idx + 1]
    if "docs" in parts:
        idx = parts.index("docs")
        if idx + 1 < len(parts) and not parts[idx + 1].endswith(".md"):
            return parts[idx + 1]
    if "data" in parts:
        idx = parts.index("data")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return "general"


def index_scripts(client, force_reindex: bool = False):
    """Index all Python scripts"""
    print("\n📜 Indexing Python scripts...")
    
    collection = client.get_or_create_collection(
        name=COLLECTIONS["scripts"],
        metadata={"description": "GTM automation scripts"}
    )
    
    # Find all Python files in scripts/
    script_patterns = [
        str(PROJECT_ROOT / "scripts" / "**" / "*.py"),
        str(PROJECT_ROOT / "*.py"),  # Root level scripts
    ]
    
    documents = []
    metadatas = []
    ids = []
    
    for pattern in script_patterns:
        for filepath in glob.glob(pattern, recursive=True):
            # Skip __pycache__ and test files
            if "__pycache__" in filepath or "test_" in filepath:
                continue
            
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"  ⚠️  Could not read {rel_path}: {e}")
                continue
            
            if not content.strip():
                continue
            
            # Extract metadata
            docstring = extract_docstring(content)
            functions = extract_functions(content)
            classes = extract_classes(content)
            imports = extract_imports(content)
            category = get_category_from_path(filepath)
            
            # Create searchable document
            doc = f"""
Script: {rel_path}
Category: {category}
Purpose: {docstring[:500]}
Functions: {', '.join(functions[:15])}
Classes: {', '.join(classes[:10])}
Imports: {', '.join(imports[:15])}

Code Preview:
{content[:3000]}
"""
            
            documents.append(doc)
            metadatas.append({
                "type": "script",
                "path": rel_path,
                "category": category,
                "purpose": docstring[:300] if docstring != "No docstring" else "",
                "functions": ", ".join(functions[:10]),
                "classes": ", ".join(classes[:5]),
                "imports": ", ".join(imports[:10]),
                "lines": len(content.split("\n")),
                "indexed_at": datetime.now().isoformat()
            })
            ids.append(rel_path)
    
    if documents:
        # Upsert to handle updates
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"  ✅ Indexed {len(documents)} scripts")
    else:
        print("  ⚠️  No scripts found to index")
    
    return len(documents)


def index_docs(client, force_reindex: bool = False):
    """Index all documentation files"""
    print("\n📚 Indexing documentation...")
    
    collection = client.get_or_create_collection(
        name=COLLECTIONS["docs"],
        metadata={"description": "GTM documentation and guides"}
    )
    
    # Find all markdown files
    doc_patterns = [
        str(PROJECT_ROOT / "docs" / "**" / "*.md"),
        str(PROJECT_ROOT / "context" / "*.md"),
        str(PROJECT_ROOT / "customer-calls" / "**" / "*.md"),
        str(PROJECT_ROOT / "*.md"),  # Root level docs
    ]
    
    documents = []
    metadatas = []
    ids = []
    
    for pattern in doc_patterns:
        for filepath in glob.glob(pattern, recursive=True):
            # Skip templates
            if "_TEMPLATE" in filepath:
                continue
            
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"  ⚠️  Could not read {rel_path}: {e}")
                continue
            
            if not content.strip():
                continue
            
            category = get_category_from_path(filepath)
            
            # Chunk large documents
            chunks = chunk_markdown(content)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{rel_path}#chunk{i}" if len(chunks) > 1 else rel_path
                
                documents.append(chunk["content"])
                metadatas.append({
                    "type": "documentation",
                    "path": rel_path,
                    "category": category,
                    "section": chunk["heading"][:100],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "indexed_at": datetime.now().isoformat()
                })
                ids.append(chunk_id)
    
    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"  ✅ Indexed {len(documents)} document chunks")
    else:
        print("  ⚠️  No documents found to index")
    
    return len(documents)


def index_data_files(client, force_reindex: bool = False):
    """Index data files (JSON company lists, etc.)"""
    print("\n📊 Indexing data files...")
    
    collection = client.get_or_create_collection(
        name=COLLECTIONS["data"],
        metadata={"description": "GTM data files and company lists"}
    )
    
    # Find JSON files in data/
    data_patterns = [
        str(PROJECT_ROOT / "data" / "**" / "*.json"),
    ]
    
    documents = []
    metadatas = []
    ids = []
    
    for pattern in data_patterns:
        for filepath in glob.glob(pattern, recursive=True):
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"  ⚠️  Could not read {rel_path}: {e}")
                continue
            
            category = get_category_from_path(filepath)
            
            # Create summary of the data file
            if isinstance(data, list):
                count = len(data)
                sample = data[:3] if data else []
                summary = f"List of {count} items"
            elif isinstance(data, dict):
                count = len(data)
                sample = {k: data[k] for k in list(data.keys())[:3]}
                summary = f"Dictionary with {count} keys"
            else:
                count = 1
                sample = str(data)[:500]
                summary = "Single value"
            
            doc = f"""
Data File: {rel_path}
Category: {category}
Type: {summary}
Count: {count}
Sample: {json.dumps(sample, indent=2, default=str)[:1500]}
"""
            
            documents.append(doc)
            metadatas.append({
                "type": "data",
                "path": rel_path,
                "category": category,
                "item_count": count,
                "data_type": "list" if isinstance(data, list) else "dict",
                "indexed_at": datetime.now().isoformat()
            })
            ids.append(rel_path)
    
    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"  ✅ Indexed {len(documents)} data files")
    else:
        print("  ⚠️  No data files found to index")
    
    return len(documents)


def index_meetings(client, force_reindex: bool = False):
    """Index meeting notes"""
    print("\n📅 Indexing meeting notes...")
    
    collection = client.get_or_create_collection(
        name=COLLECTIONS["meetings"],
        metadata={"description": "Meeting notes and decisions"}
    )
    
    # Find meeting notes
    meeting_pattern = str(PROJECT_ROOT / "meetings" / "notes" / "*.md")
    
    documents = []
    metadatas = []
    ids = []
    
    for filepath in glob.glob(meeting_pattern):
        # Skip templates
        if "_TEMPLATE" in filepath:
            continue
        
        rel_path = os.path.relpath(filepath, PROJECT_ROOT)
        filename = Path(filepath).stem
        
        # Extract date from filename (format: YYYY-MM-DD_topic)
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        date = date_match.group(1) if date_match else "unknown"
        topic = filename.split("_", 1)[1] if "_" in filename else filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ⚠️  Could not read {rel_path}: {e}")
            continue
        
        if not content.strip():
            continue
        
        documents.append(content[:5000])
        metadatas.append({
            "type": "meeting",
            "path": rel_path,
            "date": date,
            "topic": topic.replace("-", " ").replace("_", " "),
            "indexed_at": datetime.now().isoformat()
        })
        ids.append(rel_path)
    
    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"  ✅ Indexed {len(documents)} meeting notes")
    else:
        print("  ⚠️  No meeting notes found to index")
    
    return len(documents)


def show_stats(client):
    """Show indexing statistics"""
    print("\n📈 Index Statistics:")
    print("-" * 50)
    
    for name, collection_name in COLLECTIONS.items():
        try:
            collection = client.get_collection(collection_name)
            count = collection.count()
            print(f"  {name.capitalize():12} : {count:5} items")
        except Exception:
            print(f"  {name.capitalize():12} : Not indexed")
    
    print("-" * 50)
    print(f"  Index path: {CHROMA_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Index GTM workspace for semantic search")
    parser.add_argument("--scripts", action="store_true", help="Index only scripts")
    parser.add_argument("--docs", action="store_true", help="Index only documentation")
    parser.add_argument("--data", action="store_true", help="Index only data files")
    parser.add_argument("--meetings", action="store_true", help="Index only meeting notes")
    parser.add_argument("--force", action="store_true", help="Force reindex all")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    args = parser.parse_args()
    
    print("🔍 Chroma GTM Workspace Indexer")
    print("=" * 50)
    
    client = get_client()
    
    if args.stats:
        show_stats(client)
        return
    
    # If no specific flag, index everything
    index_all = not (args.scripts or args.docs or args.data or args.meetings)
    
    total = 0
    
    if index_all or args.scripts:
        total += index_scripts(client, args.force)
    
    if index_all or args.docs:
        total += index_docs(client, args.force)
    
    if index_all or args.data:
        total += index_data_files(client, args.force)
    
    if index_all or args.meetings:
        total += index_meetings(client, args.force)
    
    print("\n" + "=" * 50)
    print(f"✅ Total indexed: {total} items")
    print(f"📁 Index location: {CHROMA_PATH}")
    print("\nRun 'python scripts/chroma/query_workspace.py \"your query\"' to search")


if __name__ == "__main__":
    main()
