import chromadb
import uuid

# 1. Initialize a persistent database on your local machine
# This will create a folder called 'chroma_db' in your backend directory
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 2. Create or load a "Collection" (Think of this like a SQL table for vectors)
memory_collection = chroma_client.get_or_create_collection(name="user_facts")

def save_memory(fact: str):
    """
    Takes a string fact, automatically embeds it into a vector, and saves it.
    """
    # We generate a unique ID for every memory
    memory_id = str(uuid.uuid4())
    
    memory_collection.add(
        documents=[fact],
        ids=[memory_id]
    )
    print(f"🧠 [DB LOG] Memory Saved: {fact}")

def search_memory(query: str, n_results: int = 3) -> list:
    """
    Searches the vector DB for past facts that are relevant to the user's current query.
    """
    # If the database is empty, don't try to search it
    if memory_collection.count() == 0:
        return []

    # Chroma automatically converts our query into a vector and calculates the closest matches
    results = memory_collection.query(
        query_texts=[query],
        n_results=min(n_results, memory_collection.count())
    )
    
    # Chroma returns a nested dictionary. We just want the raw text strings.
    if results and results['documents']:
        return results['documents'][0]
    
    return []