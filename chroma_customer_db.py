"""
Chroma Database for Customer Management

This module provides functionality to store and query customer data
using ChromaDB Cloud.
"""

import chromadb
import json
from typing import Optional
from datetime import datetime


class ChromaCustomerDB:
    """
    A class to manage customer data in ChromaDB Cloud.
    """
    
    def __init__(self):
        """Initialize connection to ChromaDB Cloud."""
        self.client = chromadb.CloudClient(
            api_key='ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm',
            tenant='aa8f571e-03dc-4cd8-b888-723bd00b83f0',
            database='customer'
        )
        
        # Get or create the customers collection
        self.collection = self.client.get_or_create_collection(
            name="customers",
            metadata={"description": "GTM Customer Database"}
        )
        
        print(f"Connected to ChromaDB Cloud - Collection: 'customers'")
        print(f"Current document count: {self.collection.count()}")
    
    def add_customer(
        self,
        company_name: str,
        category: str = "customer",
        source: str = "manual",
        source_url: Optional[str] = None,
        video_title: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Add a single customer to the database.
        
        Args:
            company_name: Name of the company
            category: Type of company (customer, competitor, partner)
            source: Where this data came from (youtube, website, manual)
            source_url: URL of the source
            video_title: Title of video if from YouTube
            notes: Additional notes
            metadata: Any extra metadata
            
        Returns:
            Document ID
        """
        doc_id = f"{company_name.lower().replace(' ', '_')}_{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        doc_metadata = {
            "company_name": company_name,
            "category": category,
            "source": source,
            "added_at": datetime.now().isoformat(),
        }
        
        if source_url:
            doc_metadata["source_url"] = source_url
        if video_title:
            doc_metadata["video_title"] = video_title
        if notes:
            doc_metadata["notes"] = notes
        if metadata:
            doc_metadata.update(metadata)
        
        # Create searchable document text
        document_text = f"{company_name} - {category}"
        if notes:
            document_text += f". {notes}"
        
        self.collection.add(
            ids=[doc_id],
            documents=[document_text],
            metadatas=[doc_metadata]
        )
        
        print(f"Added: {company_name} ({category})")
        return doc_id
    
    def add_customers_batch(self, customers: list[dict]) -> list[str]:
        """
        Add multiple customers at once.
        
        Args:
            customers: List of customer dictionaries with keys:
                - company_name (required)
                - category (optional, default: "customer")
                - source (optional)
                - source_url (optional)
                - video_title (optional)
                - notes (optional)
                
        Returns:
            List of document IDs
        """
        ids = []
        documents = []
        metadatas = []
        
        for customer in customers:
            company_name = customer.get("company_name")
            if not company_name:
                continue
                
            category = customer.get("category", "customer")
            doc_id = f"{company_name.lower().replace(' ', '_')}_{category}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            doc_metadata = {
                "company_name": company_name,
                "category": category,
                "source": customer.get("source", "batch_import"),
                "added_at": datetime.now().isoformat(),
            }
            
            if customer.get("source_url"):
                doc_metadata["source_url"] = customer["source_url"]
            if customer.get("video_title"):
                doc_metadata["video_title"] = customer["video_title"]
            if customer.get("notes"):
                doc_metadata["notes"] = customer["notes"]
            
            document_text = f"{company_name} - {category}"
            if customer.get("notes"):
                document_text += f". {customer['notes']}"
            
            ids.append(doc_id)
            documents.append(document_text)
            metadatas.append(doc_metadata)
        
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Added {len(ids)} customers to database")
        
        return ids
    
    def search_customers(self, query: str, n_results: int = 10, category: Optional[str] = None) -> list[dict]:
        """
        Search for customers by query.
        
        Args:
            query: Search query
            n_results: Maximum number of results
            category: Filter by category (customer, competitor, partner)
            
        Returns:
            List of matching customer records
        """
        where_filter = None
        if category:
            where_filter = {"category": category}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        customers = []
        if results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas'][0]):
                customer = metadata.copy()
                customer['relevance_score'] = 1 - results['distances'][0][i] if results['distances'] else None
                customers.append(customer)
        
        return customers
    
    def get_all_customers(self, category: Optional[str] = None) -> list[dict]:
        """
        Get all customers, optionally filtered by category.
        
        Args:
            category: Filter by category (customer, competitor, partner)
            
        Returns:
            List of all customer records
        """
        where_filter = None
        if category:
            where_filter = {"category": category}
        
        results = self.collection.get(where=where_filter)
        
        customers = []
        if results and results['metadatas']:
            for metadata in results['metadatas']:
                customers.append(metadata)
        
        return customers
    
    def get_customer_count(self) -> dict:
        """
        Get count of customers by category.
        
        Returns:
            Dictionary with counts
        """
        total = self.collection.count()
        
        customers = len(self.get_all_customers(category="customer"))
        competitors = len(self.get_all_customers(category="competitor"))
        partners = len(self.get_all_customers(category="partner"))
        
        return {
            "total": total,
            "customers": customers,
            "competitors": competitors,
            "partners": partners
        }
    
    def delete_customer(self, doc_id: str) -> bool:
        """Delete a customer by document ID."""
        try:
            self.collection.delete(ids=[doc_id])
            print(f"Deleted: {doc_id}")
            return True
        except Exception as e:
            print(f"Error deleting {doc_id}: {e}")
            return False
    
    def update_customer(self, company_name: str, updates: dict) -> bool:
        """
        Update a customer record by company name.
        
        Args:
            company_name: Name of the company to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        # Find the customer by company name
        results = self.collection.get(
            where={"company_name": company_name}
        )
        
        if not results or not results['ids']:
            print(f"Customer not found: {company_name}")
            return False
        
        doc_id = results['ids'][0]
        current_metadata = results['metadatas'][0]
        current_document = results['documents'][0] if results['documents'] else ""
        
        # Update metadata with new values
        updated_metadata = current_metadata.copy()
        updated_metadata.update(updates)
        updated_metadata['updated_at'] = datetime.now().isoformat()
        
        # Rebuild document text if relevant fields changed
        document_parts = [f"{updated_metadata.get('company_name', company_name)}"]
        if updated_metadata.get('vector_db_used'):
            document_parts[0] += f" uses {updated_metadata['vector_db_used']}"
        if updated_metadata.get('use_case'):
            document_parts.append(f"Use case: {updated_metadata['use_case']}")
        if updated_metadata.get('industry'):
            document_parts.append(f"Industry: {updated_metadata['industry']}")
        if updated_metadata.get('notes'):
            document_parts.append(updated_metadata['notes'])
        
        updated_document = ". ".join(document_parts)
        
        # Update in ChromaDB
        self.collection.update(
            ids=[doc_id],
            metadatas=[updated_metadata],
            documents=[updated_document]
        )
        
        print(f"Updated: {company_name}")
        return True
    
    def mark_as_verified(self, company_name: str) -> bool:
        """
        Mark a customer record as verified (updates last_verified_at timestamp).
        
        Args:
            company_name: Name of the company to verify
            
        Returns:
            True if successful, False otherwise
        """
        return self.update_customer(company_name, {
            "last_verified_at": datetime.now().isoformat()
        })
    
    def get_customer_by_name(self, company_name: str) -> Optional[dict]:
        """
        Get a single customer record by company name.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Customer record or None if not found
        """
        results = self.collection.get(
            where={"company_name": company_name}
        )
        
        if results and results['metadatas']:
            return results['metadatas'][0]
        return None
    
    def import_from_json(self, json_file: str, source_name: str = "json_import") -> int:
        """
        Import customers from a JSON file.
        
        Expected JSON structure:
        {
            "companies": {
                "customers": ["Company1", "Company2"],
                "competitors": ["Competitor1"],
                "technology_partners": ["Partner1"]
            }
        }
        
        Args:
            json_file: Path to JSON file
            source_name: Name of the source
            
        Returns:
            Number of customers imported
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        customers_to_add = []
        
        # Handle nested structure
        companies = data.get("companies", data)
        
        for company in companies.get("customers", []):
            customers_to_add.append({
                "company_name": company,
                "category": "customer",
                "source": source_name
            })
        
        for company in companies.get("competitors", []):
            customers_to_add.append({
                "company_name": company,
                "category": "competitor",
                "source": source_name
            })
        
        for company in companies.get("technology_partners", companies.get("partners", [])):
            customers_to_add.append({
                "company_name": company,
                "category": "partner",
                "source": source_name
            })
        
        if customers_to_add:
            self.add_customers_batch(customers_to_add)
        
        return len(customers_to_add)
    
    def import_vector_db_research(self, json_file: str) -> int:
        """
        Import customers from the vector database research JSON format.
        
        Expected JSON structure:
        {
            "output": {
                "vector_database_customers": [
                    {
                        "company_name": "...",
                        "vector_db_used": "...",
                        "source": "...",
                        "source_url": "...",
                        "use_case": "...",
                        "industry": "...",
                        "company_size": "...",
                        "confidence": "...",
                        "date_found": "...",
                        "notes": "..."
                    }
                ]
            }
        }
        
        Args:
            json_file: Path to JSON file
            
        Returns:
            Number of customers imported
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        customers_list = data.get("output", {}).get("vector_database_customers", [])
        
        if not customers_list:
            print("No customers found in the JSON file")
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for customer in customers_list:
            company_name = customer.get("company_name")
            if not company_name:
                continue
            
            vector_db = customer.get("vector_db_used", "unknown")
            doc_id = f"{company_name.lower().replace(' ', '_')}_{vector_db.lower()}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            # Build metadata
            doc_metadata = {
                "company_name": company_name,
                "category": "prospect",  # These are competitor customers = our prospects
                "vector_db_used": vector_db,
                "source": customer.get("source", "research"),
                "added_at": datetime.now().isoformat(),
            }
            
            # Add optional fields if present
            if customer.get("source_url"):
                doc_metadata["source_url"] = customer["source_url"]
            if customer.get("use_case"):
                doc_metadata["use_case"] = customer["use_case"]
            if customer.get("industry"):
                doc_metadata["industry"] = customer["industry"]
            if customer.get("company_size"):
                doc_metadata["company_size"] = customer["company_size"]
            if customer.get("confidence"):
                doc_metadata["confidence"] = customer["confidence"]
            if customer.get("date_found"):
                doc_metadata["date_found"] = customer["date_found"]
            if customer.get("notes"):
                doc_metadata["notes"] = customer["notes"]
            
            # Create rich searchable document text
            document_parts = [f"{company_name} uses {vector_db}"]
            if customer.get("use_case"):
                document_parts.append(f"Use case: {customer['use_case']}")
            if customer.get("industry"):
                document_parts.append(f"Industry: {customer['industry']}")
            if customer.get("notes"):
                document_parts.append(customer["notes"])
            
            document_text = ". ".join(document_parts)
            
            ids.append(doc_id)
            documents.append(document_text)
            metadatas.append(doc_metadata)
        
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"Imported {len(ids)} vector DB customers to database")
        
        return len(ids)
    
    def search_by_vector_db(self, vector_db: str, n_results: int = 50) -> list[dict]:
        """
        Get all customers using a specific vector database.
        
        Args:
            vector_db: Name of vector database (e.g., "Pinecone", "Weaviate")
            n_results: Maximum results to return
            
        Returns:
            List of customer records
        """
        results = self.collection.get(
            where={"vector_db_used": vector_db}
        )
        
        customers = []
        if results and results['metadatas']:
            for metadata in results['metadatas']:
                customers.append(metadata)
        
        return customers
    
    def search_by_industry(self, industry: str, n_results: int = 10) -> list[dict]:
        """
        Search customers by industry using semantic search.
        
        Args:
            industry: Industry to search for
            n_results: Maximum results to return
            
        Returns:
            List of matching customer records
        """
        results = self.collection.query(
            query_texts=[f"Industry: {industry}"],
            n_results=n_results
        )
        
        customers = []
        if results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas'][0]):
                customer = metadata.copy()
                customer['relevance_score'] = 1 - results['distances'][0][i] if results['distances'] else None
                customers.append(customer)
        
        return customers
    
    def import_all_from_research_json(self, json_file: str) -> dict:
        """
        Import ALL customer data from the vector database research JSON file.
        
        This imports from all sections:
        - vector_database_customers
        - dedicated_managed_db_customer_profiles
        - open_source_db_customer_profiles
        - integrated_search_engine_customer_profiles
        - general_purpose_db_customer_profiles
        - postgres_ecosystem_customer_profiles
        - specialized_and_embedded_db_customer_profiles
        
        Args:
            json_file: Path to JSON file
            
        Returns:
            Dictionary with import counts by section
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        output = data.get("output", {})
        import_counts = {}
        
        # 1. Import main vector_database_customers (detailed format)
        main_customers = output.get("vector_database_customers", [])
        if main_customers:
            count = self._import_detailed_customers(main_customers, "vector_database_customers")
            import_counts["vector_database_customers"] = count
        
        # 2. Import profile sections (simpler format)
        profile_sections = [
            "dedicated_managed_db_customer_profiles",
            "open_source_db_customer_profiles",
            "integrated_search_engine_customer_profiles",
            "general_purpose_db_customer_profiles",
            "postgres_ecosystem_customer_profiles",
            "specialized_and_embedded_db_customer_profiles"
        ]
        
        for section in profile_sections:
            profiles = output.get(section, [])
            if profiles:
                count = self._import_profile_customers(profiles, section)
                import_counts[section] = count
        
        # Print summary
        total = sum(import_counts.values())
        print(f"\n=== Import Summary ===")
        for section, count in import_counts.items():
            print(f"  {section}: {count}")
        print(f"  TOTAL: {total}")
        
        return import_counts
    
    def _import_detailed_customers(self, customers: list, source_section: str) -> int:
        """Import customers with detailed format (company_name, vector_db_used, etc.)"""
        ids = []
        documents = []
        metadatas = []
        
        for customer in customers:
            company_name = customer.get("company_name")
            if not company_name:
                continue
            
            vector_db = customer.get("vector_db_used", "unknown")
            doc_id = f"{company_name.lower().replace(' ', '_')}_{vector_db.lower()}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            doc_metadata = {
                "company_name": company_name,
                "category": "prospect",
                "vector_db_used": vector_db,
                "source": customer.get("source", source_section),
                "source_section": source_section,
                "added_at": datetime.now().isoformat(),
            }
            
            for field in ["source_url", "use_case", "industry", "company_size", "confidence", "date_found", "notes"]:
                if customer.get(field):
                    doc_metadata[field] = customer[field]
            
            document_parts = [f"{company_name} uses {vector_db}"]
            if customer.get("use_case"):
                document_parts.append(f"Use case: {customer['use_case']}")
            if customer.get("industry"):
                document_parts.append(f"Industry: {customer['industry']}")
            if customer.get("notes"):
                document_parts.append(customer["notes"])
            
            ids.append(doc_id)
            documents.append(". ".join(document_parts))
            metadatas.append(doc_metadata)
        
        if ids:
            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
        
        return len(ids)
    
    def _import_profile_customers(self, profiles: list, source_section: str) -> int:
        """Import customers with profile format (vendor_name/platform_name, company_name, use_case, selection_rationale)"""
        ids = []
        documents = []
        metadatas = []
        
        for profile in profiles:
            company_name = profile.get("company_name")
            if not company_name:
                continue
            
            # Handle both vendor_name and platform_name
            vector_db = profile.get("vendor_name") or profile.get("platform_name", "unknown")
            doc_id = f"{company_name.lower().replace(' ', '_')}_{vector_db.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            doc_metadata = {
                "company_name": company_name,
                "category": "prospect",
                "vector_db_used": vector_db,
                "source": source_section,
                "source_section": source_section,
                "added_at": datetime.now().isoformat(),
            }
            
            if profile.get("use_case"):
                doc_metadata["use_case"] = profile["use_case"]
            if profile.get("selection_rationale"):
                doc_metadata["selection_rationale"] = profile["selection_rationale"]
            
            document_parts = [f"{company_name} uses {vector_db}"]
            if profile.get("use_case"):
                document_parts.append(f"Use case: {profile['use_case']}")
            if profile.get("selection_rationale"):
                document_parts.append(f"Why: {profile['selection_rationale']}")
            
            ids.append(doc_id)
            documents.append(". ".join(document_parts))
            metadatas.append(doc_metadata)
        
        if ids:
            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
        
        return len(ids)


def main():
    """Example usage of ChromaCustomerDB."""
    
    # Initialize database
    db = ChromaCustomerDB()
    
    # Show current stats
    print("\n--- Current Database Stats ---")
    stats = db.get_customer_count()
    print(f"Total records: {stats['total']}")
    print(f"Customers: {stats['customers']}")
    print(f"Competitors: {stats['competitors']}")
    print(f"Partners: {stats['partners']}")
    
    # Example: Add a single customer
    # db.add_customer(
    #     company_name="Acme Corp",
    #     category="customer",
    #     source="youtube",
    #     source_url="https://youtube.com/watch?v=example",
    #     notes="Mentioned in product demo video"
    # )
    
    # Example: Add multiple customers
    # db.add_customers_batch([
    #     {"company_name": "TechCorp", "category": "customer"},
    #     {"company_name": "DataInc", "category": "partner"},
    # ])
    
    # Example: Import from JSON file
    # db.import_from_json("vespa_COMPANIES_FINAL.json", source_name="vespa_youtube")
    
    # Example: Search customers
    # results = db.search_customers("tech", n_results=5)
    # for r in results:
    #     print(f"  - {r['company_name']} ({r['category']})")


if __name__ == "__main__":
    main()
