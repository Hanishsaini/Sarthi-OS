import chromadb
from datetime import datetime

class SemanticMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="memory/semantic_db")
        self.collection = self.client.get_or_create_collection("user_interactions")
    
    def add(self, text: str, metadata: dict = None):
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"timestamp": datetime.now().isoformat()}],
            ids=[f"mem_{datetime.now().timestamp()}"]
        )