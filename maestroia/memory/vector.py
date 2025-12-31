import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatL2(1536)  # Dimensão do embedding
        self.documents = []

    def add_document(self, text: str):
        vector = embeddings.embed_query(text)
        self.index.add(np.array([vector]))
        self.documents.append(text)

    def search(self, query: str, k=5):
        vector = embeddings.embed_query(query)
        distances, indices = self.index.search(np.array([vector]), k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
