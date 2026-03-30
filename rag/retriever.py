import os

class Retriever:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        try:
            with open("rag/jaipur_data.txt", "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""

    def retrieve(self, query: str):
        """
        Simple retrieval: returns relevant chunk
        Later we upgrade to vector DB
        """

        query = query.lower()

        # basic keyword filtering
        if "temple" in query:
            return self.extract_section("temple")

        if "fort" in query:
            return self.extract_section("fort")

        if "food" in query:
            return self.extract_section("food")

        if "shopping" in query:
            return self.extract_section("shopping")

        return self.data[:2000]  # fallback chunk

    def extract_section(self, keyword):
        chunks = self.data.split("\n\n")
        relevant = [c for c in chunks if keyword in c.lower()]
        return "\n\n".join(relevant[:5])