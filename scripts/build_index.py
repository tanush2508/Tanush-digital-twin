from __future__ import annotations

from backend.config import settings
from backend.embed import embed_texts
from backend.ingest import chunk_records, load_all_records
from backend.vector_store import LocalVectorStore


def main() -> None:
    settings.validate()

    records = load_all_records()
    print(f"Loaded {len(records)} memory records")

    chunks = chunk_records(records)
    print(f"Created {len(chunks)} chunks")

    texts = [chunk.content for chunk in chunks]
    vectors = embed_texts(texts)
    print(f"Embedded {len(vectors)} chunks")

    store = LocalVectorStore()
    store.save(chunks, vectors)

    print("Index saved successfully")
    print(store.count_by_layer())


if __name__ == "__main__":
    main()