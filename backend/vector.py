"""ChromaDB com embeddings Ollama. Reusa o modelo local do projeto anterior."""
import os
from pathlib import Path
import requests
from academic.knowledge_index import chunks, keywords

ROOT = Path(__file__).resolve().parents[1]
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
COLLECTION = "resumos_ollama_v1"


def embed(texts):
    response = requests.post(os.getenv("OLLAMA_URL", "http://127.0.0.1:11434") + "/api/embed",
        json={"model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), "input": texts}, timeout=(5, 120))
    response.raise_for_status()
    return response.json()["embeddings"]


def collection():
    import chromadb
    client = chromadb.PersistentClient(path=str(ROOT / "runtime" / "chroma"))
    return client.get_or_create_collection(COLLECTION, embedding_function=None,
        metadata={"embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), "hnsw:space": "cosine"})


def rebuild():
    col = collection()
    if col.count():
        col.delete(where={"tipo": "resumo proprio aprovado"})
    items = chunks()
    for start in range(0, len(items), 16):
        batch = items[start:start+16]
        col.add(ids=[i[0] for i in batch], documents=[i[1] for i in batch], metadatas=[i[2] for i in batch],
                embeddings=embed([i[1] for i in batch]))
    return col.count()


def retrieve(question, limit=4):
    col = collection()
    if col.metadata.get("embedding_model") != os.getenv("EMBEDDING_MODEL", "nomic-embed-text"):
        raise ValueError("O modelo de embeddings mudou. Recrie o índice.")
    if not col.count():
        raise ValueError("Índice vazio. Execute python -m backend.vector para indexar os resumos.")
    hits = col.query(query_embeddings=embed([question]), n_results=col.count())
    candidates = [{"texto": text, "fonte": meta["fonte"], "secao": meta["secao"], "tema": meta["tema"], "distancia": distance}
        for text, meta, distance in zip(hits["documents"][0], hits["metadatas"][0], hits["distances"][0])]
    words = keywords(question)
    return sorted(candidates, key=lambda hit: len(words & keywords(hit["secao"] + " " + hit["tema"])) * 3
                  + len(words & keywords(hit["texto"])) - hit["distancia"], reverse=True)[:limit]


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    print(f"{rebuild()} trechos próprios indexados em ChromaDB.")
