#!/usr/bin/env python3
"""
Chroma MCP Server
=================
Model Context Protocol server that exposes Chroma workspace search to AI agents.

This allows Cursor (and other MCP-compatible tools) to use your local Chroma
index for semantic search instead of their built-in search.

Setup in Cursor:
1. Add to ~/.cursor/mcp.json:
   {
     "mcpServers": {
       "chroma-workspace": {
         "command": "python3",
         "args": ["/Users/ankitpansari/Desktop/Chroma GTM/scripts/chroma/mcp_chroma_server.py"],
         "env": {}
       }
     }
   }

2. Restart Cursor

Usage:
    The AI will now have access to tools like:
    - chroma_search_scripts
    - chroma_search_docs
    - chroma_search_companies
    - chroma_search_all
"""

import json
import sys
from pathlib import Path

# Add workspace root to path
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Error: chromadb not installed", file=sys.stderr)
    sys.exit(1)

# Chroma setup
CHROMA_PATH = WORKSPACE_ROOT / ".chroma_workspace_index"

if not CHROMA_PATH.exists():
    print(f"Error: Chroma index not found at {CHROMA_PATH}", file=sys.stderr)
    print("Run: python index_workspace.py", file=sys.stderr)
    sys.exit(1)

client = chromadb.PersistentClient(path=str(CHROMA_PATH))
ef = embedding_functions.DefaultEmbeddingFunction()


def get_collection(name: str):
    """Get a collection by name."""
    try:
        return client.get_collection(name, embedding_function=ef)
    except:
        return None


def search_collection(collection_name: str, query: str, n_results: int = 5) -> dict:
    """Search a specific collection."""
    collection = get_collection(collection_name)
    if not collection:
        return {"error": f"Collection '{collection_name}' not found. Run index_workspace.py"}
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted = []
    if results['ids'][0]:
        for i, (id, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            similarity = max(0, 1 - distance)
            formatted.append({
                "id": id,
                "similarity": f"{similarity:.1%}",
                "metadata": metadata,
                "preview": results['documents'][0][i][:500] if results['documents'] else ""
            })
    
    return {
        "query": query,
        "collection": collection_name,
        "count": len(formatted),
        "results": formatted
    }


# MCP Protocol Implementation
def handle_initialize(params):
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "chroma-workspace",
            "version": "1.0.0"
        }
    }


def handle_tools_list(params):
    return {
        "tools": [
            {
                "name": "chroma_search_scripts",
                "description": "Search Python scripts in the workspace using semantic search. Use this to find existing automation scripts before creating new ones.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language description of what you're looking for (e.g., 'sync companies to HubSpot', 'LinkedIn automation')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "chroma_search_docs",
                "description": "Search documentation files in the workspace. Use this to find strategy docs, guides, and playbooks.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language description of what you're looking for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "chroma_search_companies",
                "description": "Search company data in the workspace. Use this to find leads, customers, or competitor information.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Company name, industry, or description to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "chroma_search_meetings",
                "description": "Search meeting notes. Use this to find past discussions, decisions, or action items.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Topic or content to search for in meeting notes"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "chroma_search_all",
                "description": "Search all collections (scripts, docs, companies, meetings) at once. Use this for broad searches.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language description of what you're looking for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results per collection (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "chroma_index_stats",
                "description": "Get statistics about the Chroma index (collection counts, last updated, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }


def handle_tools_call(params):
    tool_name = params.get("name")
    args = params.get("arguments", {})
    
    if tool_name == "chroma_search_scripts":
        result = search_collection("scripts", args["query"], args.get("limit", 5))
    elif tool_name == "chroma_search_docs":
        result = search_collection("docs", args["query"], args.get("limit", 5))
    elif tool_name == "chroma_search_companies":
        result = search_collection("companies", args["query"], args.get("limit", 10))
    elif tool_name == "chroma_search_meetings":
        result = search_collection("meetings", args["query"], args.get("limit", 5))
    elif tool_name == "chroma_search_all":
        limit = args.get("limit", 3)
        result = {
            "query": args["query"],
            "scripts": search_collection("scripts", args["query"], limit),
            "docs": search_collection("docs", args["query"], limit),
            "companies": search_collection("companies", args["query"], limit),
            "meetings": search_collection("meetings", args["query"], limit)
        }
    elif tool_name == "chroma_index_stats":
        collections = client.list_collections()
        stats = {}
        for col in collections:
            stats[col.name] = {
                "count": col.count(),
                "metadata": col.metadata
            }
        result = {
            "index_path": str(CHROMA_PATH),
            "collections": stats
        }
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


def main():
    """Main MCP server loop using stdio transport."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "tools/list":
                result = handle_tools_list(params)
            elif method == "tools/call":
                result = handle_tools_call(params)
            elif method == "notifications/initialized":
                continue  # No response needed for notifications
            else:
                result = {"error": f"Unknown method: {method}"}
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id if 'request_id' in dir() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

