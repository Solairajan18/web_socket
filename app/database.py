import chromadb
from datetime import datetime
from typing import List, Dict, Any
from app.config import settings
from app.models import PersonalDetail

class DatabaseService:
    def __init__(self):
        self.client = chromadb.CloudClient(
            api_key=settings.CHROMA_API_KEY,
            tenant=settings.CHROMA_TENANT,
            database=settings.CHROMA_DATABASE
        )
        self.collection = self.client.get_or_create_collection(name="portfolio")

    async def add_personal_detail(self, detail: PersonalDetail) -> bool:
        try:
            self.collection.add(
                documents=[detail.content],
                metadatas=[{
                    "category": detail.category,
                    "timestamp": detail.timestamp.isoformat(),
                    **detail.metadata
                }],
                ids=[f"{detail.category}_{datetime.now().timestamp()}"]
            )
            return True
        except Exception as e:
            print(f"Error adding personal detail: {e}")
            return False

    async def search_context(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return [
                {
                    "content": doc,
                    "metadata": meta
                }
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ]
        except Exception as e:
            print(f"Error searching context: {e}")
            return []

    async def get_all_details(self) -> List[Dict[str, Any]]:
        try:
            # Note: This is a simplified version. In production, you might want to implement pagination
            results = self.collection.get()
            return [
                {
                    "content": doc,
                    "metadata": meta
                }
                for doc, meta in zip(results["documents"], results["metadatas"])
            ]
        except Exception as e:
            print(f"Error getting all details: {e}")
            return []
