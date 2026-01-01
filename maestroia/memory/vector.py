import faiss
import numpy as np
from maestroia.services.openai_service import get_embedding
from maestroia.config import settings


class VectorStore:
    def __init__(self):
        dim = getattr(settings, 'DEFAULT_EMBEDDING_DIM', 1536)
        self.index = faiss.IndexFlatL2(dim)  # Dimensão do embedding
        self.documents = []

    def add_document(self, text: str):
        vector = np.array(get_embedding(text), dtype=np.float32)
        self.index.add(np.array([vector]))
        self.documents.append(text)

    def search(self, query: str, k=5):
        vector = np.array(get_embedding(query), dtype=np.float32)
        distances, indices = self.index.search(np.array([vector]), k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
