from maestroia.memory.vector import VectorStore

store = VectorStore()

def store_memory(text: str):
    store.add_document(text)

def retrieve_memory(query: str):
    return store.search(query)
