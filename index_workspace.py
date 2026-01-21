#!/usr/bin/env python3
"""
Chroma Workspace Indexer
========================
Indexes all scripts, documentation, and data files for semantic search.

Usage:
    python index_workspace.py          # Full index
    python index_workspace.py --quick  # Quick index (scripts + docs only)

This creates a local Chroma database at .chroma_workspace_index/
that can be queried by AI agents to find relevant existing files.
"""

import os
import re
import json
import glob
import argparse
from pathlib import Path
from datetime import datetime

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("❌ chromadb not installed. Run: pip install chromadb")
    exit(1)

# Configuration
WORKSPACE_ROOT = Path(__file__).parent
CHROMA_PATH = WORKSPACE_ROOT / ".chroma_workspace_index"

# Initialize Chroma client
client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# Use default embedding function (sentence-transformers)
# For better results, you can use OpenAI embeddings:
# ef = embedding_functions.OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))
ef = embedding_functions.DefaultEmbeddingFunction()


def get_or_create_collection(name: str, description: str):
    """Get or create a collection with metadata."""
    return client.get_or_create_collection(
        name=name,
        embedding_function=ef,
        metadata={"description": description, "indexed_at": datetime.now().isoformat()}
    )


def extract_docstring(content: str) -> str:
    """Extract the first docstring from Python content."""
    # Try triple double quotes
    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()[:500]
    
    # Try triple single quotes
    match = re.search(r"'''(.*?)'''", content, re.DOTALL)
    if match:
        return match.group(1).strip()[:500]
    
    return "No docstring found"


def extract_functions(content: str) -> list:
    """Extract function names from Python content."""
    return re.findall(r'def (\w+)\(', content)


def extract_classes(content: str) -> list:
    """Extract class names from Python content."""
    return re.findall(r'class (\w+)[\(:]', content)


def extract_imports(content: str) -> list:
    """Extract import statements from Python content."""
    imports = re.findall(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE)
    return list(set(imports))[:20]  # Limit to 20 unique imports


def chunk_markdown(content: str) -> list:
    """Chunk markdown content by headers."""
    chunks = []
    current_heading = "Introduction"
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            if current_content:
                chunks.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content)[:3000]  # Limit chunk size
                })
            current_heading = line[3:].strip()
            current_content = [line]
        elif line.startswith("# ") and not current_content:
            current_heading = line[2:].strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    if current_content:
        chunks.append({
            "heading": current_heading,
            "content": "\n".join(current_content)[:3000]
        })
    
    return chunks


def index_scripts():
    """Index all Python scripts by category."""
    print("\n📜 Indexing Python scripts...")
    
    collection = get_or_create_collection(
        "scripts",
        "Python automation scripts organized by category"
    )
    
    # Clear existing data
    try:
        existing = collection.get()
        if existing['ids']:
            collection.delete(ids=existing['ids'])
    except:
        pass
    
    script_dirs = {
        "linkedin": "scripts/linkedin/*.py",
        "hubspot": "scripts/hubspot/*.py",
        "discovery": "scripts/discovery/*.py",
        "extraction": "scripts/extraction/*.py",
        "enrichment": "scripts/enrichment/*.py",
        "notifications": "scripts/notifications/*.py",
        "sync": "scripts/sync/*.py",
        "email": "scripts/email/*.py",
        "visualization": "scripts/visualization/*.py",
        "chroma": "scripts/chroma/*.py",
        "utils": "scripts/utils/*.py",
        "browser": "scripts/browser/*.py",
        "tests": "tests/*.py",
    }
    
    documents = []
    metadatas = []
    ids = []
    
    for category, pattern in script_dirs.items():
        for filepath in glob.glob(str(WORKSPACE_ROOT / pattern)):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            rel_path = os.path.relpath(filepath, WORKSPACE_ROOT)
            docstring = extract_docstring(content)
            functions = extract_functions(content)
            classes = extract_classes(content)
            imports = extract_imports(content)
            
            # Create searchable document
            doc = f"""
Script: {rel_path}
Category: {category}
Purpose: {docstring}
Functions: {', '.join(functions[:15])}
Classes: {', '.join(classes[:10])}
Imports: {', '.join(imports)}

Code Preview:
{content[:2500]}
"""
            
            documents.append(doc)
            metadatas.append({
                "category": category,
                "path": rel_path,
                "filename": os.path.basename(filepath),
                "purpose": docstring[:200],
                "functions": ", ".join(functions[:10]),
                "classes": ", ".join(classes[:5]),
                "type": "script"
            })
            ids.append(rel_path)
    
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"   ✅ Indexed {len(documents)} scripts")
    else:
        print("   ⚠️ No scripts found")
    
    return len(documents)


def index_docs():
    """Index all documentation files."""
    print("\n📚 Indexing documentation...")
    
    collection = get_or_create_collection(
        "docs",
        "Markdown documentation files"
    )
    
    # Clear existing data
    try:
        existing = collection.get()
        if existing['ids']:
            collection.delete(ids=existing['ids'])
    except:
        pass
    
    doc_patterns = {
        "strategy": "docs/strategy/*.md",
        "competitors": "docs/competitors/*.md",
        "linkedin": "docs/linkedin/*.md",
        "hubspot": "docs/hubspot/*.md",
        "events": "docs/events/*.md",
        "case-studies": "docs/case-studies/*.md",
        "guides": "docs/guides/*.md",
        "work-plans": "docs/work-plans/*.md",
        "outreach": "docs/outreach/*.md",
        "meetings": "meetings/notes/*.md",
        "context": "context/*.md",
        "root": "*.md",
    }
    
    documents = []
    metadatas = []
    ids = []
    
    for topic, pattern in doc_patterns.items():
        for filepath in glob.glob(str(WORKSPACE_ROOT / pattern)):
            if "_TEMPLATE" in filepath:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            rel_path = os.path.relpath(filepath, WORKSPACE_ROOT)
            
            # Chunk large documents
            chunks = chunk_markdown(content)
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{rel_path}#chunk{i}" if len(chunks) > 1 else rel_path
                
                documents.append(chunk["content"])
                metadatas.append({
                    "topic": topic,
                    "path": rel_path,
                    "filename": os.path.basename(filepath),
                    "section": chunk["heading"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "type": "documentation"
                })
                ids.append(doc_id)
    
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"   ✅ Indexed {len(documents)} document chunks")
    else:
        print("   ⚠️ No documents found")
    
    return len(documents)


def index_companies():
    """Index company data files."""
    print("\n🏢 Indexing company data...")
    
    collection = get_or_create_collection(
        "companies",
        "Company and lead data"
    )
    
    # Clear existing data
    try:
        existing = collection.get()
        if existing['ids']:
            collection.delete(ids=existing['ids'])
    except:
        pass
    
    company_patterns = [
        "data/companies/*.json",
        "data/competitors/*/*.json",
    ]
    
    documents = []
    metadatas = []
    ids = []
    total_companies = 0
    
    for pattern in company_patterns:
        for filepath in glob.glob(str(WORKSPACE_ROOT / pattern)):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                continue
            
            rel_path = os.path.relpath(filepath, WORKSPACE_ROOT)
            
            # Handle different JSON structures
            companies = []
            if isinstance(data, list):
                companies = data[:500]  # Limit here
            elif isinstance(data, dict):
                companies = data.get("companies", data.get("results", []))
                if not companies and "name" in data:
                    companies = [data]
                if isinstance(companies, list):
                    companies = companies[:500]
                else:
                    companies = []
            
            # Index companies
            for company in companies:
                if not isinstance(company, dict):
                    continue
                
                name = company.get("name", company.get("company_name", company.get("company", "")))
                if not name:
                    continue
                
                description = company.get("description", company.get("use_case", ""))
                industry = company.get("industry", company.get("sector", ""))
                tier = company.get("tier", "")
                
                doc = f"Company: {name}\nDescription: {description}\nIndustry: {industry}"
                
                doc_id = f"{rel_path}#{name.replace(' ', '_')}"
                
                documents.append(doc)
                metadatas.append({
                    "source_file": rel_path,
                    "company_name": name[:100],
                    "industry": str(industry)[:50],
                    "tier": str(tier),
                    "type": "company"
                })
                ids.append(doc_id)
                total_companies += 1
    
    if documents:
        # Add in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            collection.add(documents=batch_docs, metadatas=batch_meta, ids=batch_ids)
        
        print(f"   ✅ Indexed {total_companies} companies from {len(company_patterns)} patterns")
    else:
        print("   ⚠️ No company data found")
    
    return total_companies


def index_meetings():
    """Index meeting notes."""
    print("\n📅 Indexing meeting notes...")
    
    collection = get_or_create_collection(
        "meetings",
        "Meeting notes and decisions"
    )
    
    # Clear existing data
    try:
        existing = collection.get()
        if existing['ids']:
            collection.delete(ids=existing['ids'])
    except:
        pass
    
    documents = []
    metadatas = []
    ids = []
    
    for filepath in glob.glob(str(WORKSPACE_ROOT / "meetings/notes/*.md")):
        if "_TEMPLATE" in filepath:
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        rel_path = os.path.relpath(filepath, WORKSPACE_ROOT)
        filename = Path(filepath).stem
        
        # Extract date from filename (YYYY-MM-DD_topic)
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        date = date_match.group(1) if date_match else "unknown"
        topic = filename.split("_", 1)[1] if "_" in filename else filename
        
        documents.append(content[:5000])
        metadatas.append({
            "path": rel_path,
            "date": date,
            "topic": topic.replace("-", " ").replace("_", " "),
            "filename": filename,
            "type": "meeting"
        })
        ids.append(rel_path)
    
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"   ✅ Indexed {len(documents)} meeting notes")
    else:
        print("   ⚠️ No meeting notes found")
    
    return len(documents)


def print_summary():
    """Print summary of indexed collections."""
    print("\n" + "="*60)
    print("📊 INDEX SUMMARY")
    print("="*60)
    
    collections = client.list_collections()
    for col in collections:
        count = col.count()
        print(f"   {col.name}: {count} items")
    
    print(f"\n   Index location: {CHROMA_PATH}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Index workspace for semantic search")
    parser.add_argument("--quick", action="store_true", help="Quick index (scripts + docs only)")
    args = parser.parse_args()
    
    print("🚀 Chroma Workspace Indexer")
    print("="*60)
    print(f"   Workspace: {WORKSPACE_ROOT}")
    print(f"   Index path: {CHROMA_PATH}")
    print("="*60)
    
    # Index collections
    scripts_count = index_scripts()
    docs_count = index_docs()
    
    if not args.quick:
        companies_count = index_companies()
        meetings_count = index_meetings()
    
    print_summary()
    print("\n✅ Indexing complete! Run 'python query_workspace.py' to search.\n")


if __name__ == "__main__":
    main()

