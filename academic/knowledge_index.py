"""Índice ChromaDB dos resumos próprios, com embeddings multilíngues locais.

Uso: python academic/knowledge_index.py --rebuild
     python academic/knowledge_index.py --ask "O que é contraste pessoal?"
"""

import argparse
import hashlib
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
KNOWLEDGE = ROOT / "knowledge"
DB_PATH = ROOT / "chroma_store"
COLLECTION = "resumos_aprovados_v1"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def split_sections(text: str) -> list[tuple[str, str]]:
    content = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.S)
    sections: list[tuple[str, str]] = []
    heading = "Introdução"
    body: list[str] = []
    for line in content.splitlines():
        if line.startswith(("## ", "### ")):
            if "\n".join(body).strip():
                sections.append((heading, "\n".join(body).strip()))
            heading = line.lstrip("# ").strip()
            body = []
        else:
            body.append(line)
    if "\n".join(body).strip():
        sections.append((heading, "\n".join(body).strip()))
    return sections


def chunks(max_words: int = 350) -> list[tuple[str, str, dict]]:
    result: list[tuple[str, str, dict]] = []
    for path in sorted(KNOWLEDGE.glob("[0-9][0-9]_*.md")):
        text = path.read_text(encoding="utf-8")
        theme = path.stem[3:].replace("_", " ")
        level_match = re.search(r"^nivel:\s*(.+)$", text, flags=re.M)
        level = level_match.group(1).strip() if level_match else "não informado"
        for section, body in split_sections(text):
            words = body.split()
            for offset in range(0, len(words), max_words):
                part = f"{section}\n" + " ".join(words[offset:offset + max_words])
                key = f"{path.name}:{section}:{offset}"
                stable_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
                result.append((stable_id, part, {
                    "fonte": path.name, "tema": theme, "nivel": level,
                    "secao": section, "tipo": "resumo proprio aprovado",
                }))
    return result


def keywords(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    plain = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stopwords = {"como", "para", "uma", "que", "qual", "quais", "pelo", "pela", "sobre", "com", "dos", "das", "ser", "seu", "sua"}
    # Trim plural endings ("silhuetas" ~ "silhueta", "femininas" ~ "feminina")
    # so singular and plural forms match each other in the reranker.
    return {re.sub(r"s$", "", word) for word in re.findall(r"[a-z]{4,}", plain)
            if word not in stopwords}


class LocalEmbeddings:
    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(MODEL)

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.model.encode(input, normalize_embeddings=True).tolist()

    def name(self) -> str:
        return MODEL

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)


def collection():
    import chromadb

    client = chromadb.PersistentClient(path=str(DB_PATH))
    return client.get_or_create_collection(
        COLLECTION, embedding_function=LocalEmbeddings(),
        metadata={"hnsw:space": "cosine"},
    )


def rebuild() -> int:
    import chromadb

    items = chunks()
    if not items:
        raise ValueError("Não há resumos próprios para indexar.")
    client = chromadb.PersistentClient(path=str(DB_PATH))
    if COLLECTION in [entry.name for entry in client.list_collections()]:
        client.delete_collection(COLLECTION)
    col = collection()
    for start in range(0, len(items), 32):
        batch = items[start:start + 32]
        col.add(ids=[item[0] for item in batch],
                documents=[item[1] for item in batch],
                metadatas=[item[2] for item in batch])
    return col.count()


def retrieve(question: str, limit: int = 4) -> list[dict]:
    col = collection()
    if col.count() == 0:
        return []
    # The corpus is small (tens of chunks), so rank ALL of them: the local
    # embedding model under-scores short table-like chunks, and capping the
    # candidate pool made good sections disappear from the ranking entirely.
    hits = col.query(query_texts=[question], n_results=col.count())
    candidates = [
        {"texto": document, "fonte": metadata["fonte"],
         "secao": metadata["secao"], "tema": metadata["tema"],
         "distancia": distance}
        for document, metadata, distance in zip(
            hits["documents"][0], hits["metadatas"][0], hits["distances"][0]
        )
    ]
    query_words = keywords(question)
    # Keep semantic recall, but prioritize precise terminology in title and body.
    return sorted(candidates, key=lambda hit: (
        len(query_words & keywords(hit["secao"] + " " + hit["tema"])) * 3
        + len(query_words & keywords(hit["texto"]))
        - hit["distancia"]
    ), reverse=True)[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--rebuild", action="store_true")
    group.add_argument("--ask")
    args = parser.parse_args()
    if args.rebuild:
        print(f"{rebuild()} trechos indexados a partir de resumos próprios.")
    else:
        for hit in retrieve(args.ask):
            print(f"\n{hit['fonte']} · {hit['secao']}\n{hit['texto']}\n")


if __name__ == "__main__":
    main()