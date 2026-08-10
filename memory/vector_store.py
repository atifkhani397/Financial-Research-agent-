"""
ARA-1 Vector Store (Long-Term Memory)

Local Chroma-backed vector store with the schema from the architecture spec:
  id, content, embedding, ticker, source_type, date, confidence,
  researcher_session, verified

Uses sentence-transformers/all-MiniLM-L6-v2 for embeddings by default (free, CPU-only).

Migration path to Pinecone/Weaviate/Qdrant:
  1. Swap the ChromaClient initialization for the target client.
  2. The metadata schema and embedding function remain identical.
  3. Update CHROMA_PERSIST_DIR to the managed service's connection string.
  See docs/architecture_specification.md Section 4.2 for details.
"""

import uuid
import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config import get_settings

logger = logging.getLogger("ara1.memory.vector_store")


class VectorStore:
    """Chroma-backed long-term memory for ARA-1."""

    def __init__(self, collection_name: str = "ara1_findings"):
        settings = get_settings()
        self.persist_dir = settings.chroma_persist_dir
        self.embedding_model_name = settings.embedding_model

        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Load embedding model (CPU-only, local)
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedder = SentenceTransformer(self.embedding_model_name)
        logger.info("Embedding model loaded successfully.")

    def store(
        self,
        content: str,
        ticker: str = "",
        source_type: str = "",
        date: str = "",
        confidence: float = 0.0,
        researcher_session: str = "",
        verified: bool = False,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Embed and store a document chunk in Chroma.

        Returns:
            The document ID.
        """
        doc_id = doc_id or str(uuid.uuid4())
        embedding = self.embedder.encode(content).tolist()

        metadata = {
            "ticker": ticker,
            "source_type": source_type,
            "date": date,
            "confidence": confidence,
            "researcher_session": researcher_session,
            "verified": verified,
        }

        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )

        logger.info(f"Stored document id={doc_id} ticker={ticker} source={source_type}")
        return doc_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        where_filter: Optional[dict] = None,
    ) -> list[dict]:
        """
        Semantic search against stored findings.

        Returns:
            List of dicts with keys: id, content, metadata, distance
        """
        query_embedding = self.embedder.encode(query).tolist()

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, self.collection.count()) if self.collection.count() > 0 else top_k,
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)

        output = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                output.append({
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })

        logger.info(f"Vector search returned {len(output)} results for query='{query[:50]}...'")
        return output

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()

    def delete_collection(self):
        """Delete the entire collection (for testing/reset)."""
        self.client.delete_collection(self.collection.name)
        logger.warning("Collection deleted.")
