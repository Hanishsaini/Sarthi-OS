import ollama
import chromadb
import json
import os

class Retriever:
    def __init__(self, data_path: str = "data/places.json"):
        self.chroma = chromadb.PersistentClient(path="memory/semantic_db")
        self.collection = self.chroma.get_or_create_collection("jaipur_knowledge")
        self.embedding_model = "nomic-embed-text"
        self.data_path = data_path
        if self.collection.count() == 0:
            self._load_data()

    def _load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            places = json.load(f)

        for idx, place in enumerate(places):
            text = f"{place['name']}\nType: {place['type']}\nBest time: {place['best_time']}\nTimings: {place['timings']}\nNotes: {place['notes']}"
            emb = ollama.embed(model=self.embedding_model, input=text)['embeddings'][0]
            self.collection.add(
                documents=[text],
                embeddings=[emb],
                metadatas=[place],      # store full dict
                ids=[f"place_{idx}"]
            )
        print(f"✅ Loaded {len(places)} places from {self.data_path}")

    def retrieve(self, query: str, n_results: int = 1) -> dict:
        emb = ollama.embed(model=self.embedding_model, input=query)['embeddings'][0]
        results = self.collection.query(
            query_embeddings=[emb],
            n_results=n_results,
            include=["metadatas", "distances"]
        )
        if results["metadatas"] and results["metadatas"][0]:
            # Return the best matching place's metadata
            return results["metadatas"][0][0]
        return None