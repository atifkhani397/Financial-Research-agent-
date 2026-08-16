"""
ARA-1 Vector Store (Long-Term Memory)

Local Chroma-backed vector store with the schema from the architecture spec:
  id, content, embedding, ticker, source_type, date, confidence,
  researcher_session, verified

Uses sentence-transformers/all-MiniLM-L6-v2 for embeddings by default (free, CPU-only).

Includes structural document chunking per Section A3.3:
  - SEC Filings: chunk by section/risk-factor
  - Earnings Transcripts: chunk by speaker-turn / Q&A pair
  - News Articles: chunk by paragraph with headline context carried into every chunk
  - Financial Statements: store as structured metadata, not embedded prose
"""

import re
import uuid
import logging
from typing import Optional, Union, Dict, Any, List

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    ChromaSettings = None
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from config import get_settings

logger = logging.getLogger("ara1.memory.vector_store")


# ── Structural Text Chunkers (Section A3.3) ──────────────────────────

def chunk_sec_filing(text: str, max_chunk_size: int = 900) -> List[str]:
    """
    Chunk SEC filings by Section / Item / Risk Factors headings.
    Splits on patterns like 'Item 1.', 'Item 1A.', 'Item 7.', 'PART I', etc.
    Tuned to max 900 chars per Day 13 retrieval optimizations.
    """
    if not text or not text.strip():
        return []

    sec_pattern = re.compile(
        r'(?=\b(?:ITEM\s+\d+[A-Z]?|PART\s+[I|V|X]+|SECTION\s+\d+)\b)',
        re.IGNORECASE
    )

    sections = sec_pattern.split(text)
    chunks = []

    for sec in sections:
        sec_str = sec.strip()
        if not sec_str:
            continue
        if len(sec_str) <= max_chunk_size:
            chunks.append(sec_str)
        else:
            paragraphs = sec_str.split("\n\n")
            current_chunk = []
            current_len = 0
            for para in paragraphs:
                para_str = para.strip()
                if not para_str:
                    continue
                if current_len + len(para_str) + 2 > max_chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [para_str]
                    current_len = len(para_str)
                else:
                    current_chunk.append(para_str)
                    current_len += len(para_str) + 2
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text.strip()]


def chunk_earnings_transcript(text: str, max_chunk_size: int = 900) -> List[str]:
    """
    Chunk earnings transcripts by speaker-turn or Q&A pair per Section A3.3.
    Tuned to max 900 chars for precision retrieval.
    """
    if not text or not text.strip():
        return []

    speaker_pattern = re.compile(
        r'\n+(?=(?:Operator|Question-and-Answer|Q:|A:|[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s*\([^\)]+\))?:))',
        re.MULTILINE
    )

    turns = [t.strip() for t in speaker_pattern.split(text) if t.strip()]
    if not turns:
        return [text.strip()]

    if len(turns) <= 10:
        return turns

    chunks = []
    current_chunk = []
    current_len = 0

    for turn in turns:
        if len(turn) > max_chunk_size:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_len = 0
            chunks.append(turn)
        elif current_len + len(turn) + 2 > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [turn]
            current_len = len(turn)
        else:
            current_chunk.append(turn)
            current_len += len(turn) + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text.strip()]


def chunk_news_article(text: str, headline: str = "", max_chunk_size: int = 800) -> List[str]:
    """
    Chunk news articles by paragraph, carrying headline context into every chunk.
    Tuned to max 800 chars.
    """
    if not text or not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    headline_prefix = f"Headline: {headline}\n\n" if headline else ""

    current_body = []
    current_len = len(headline_prefix)

    for para in paragraphs:
        if current_len + len(para) + 2 > max_chunk_size and current_body:
            chunk_content = headline_prefix + "\n\n".join(current_body)
            chunks.append(chunk_content)
            current_body = [para]
            current_len = len(headline_prefix) + len(para)
        else:
            current_body.append(para)
            current_len += len(para) + 2

    if current_body:
        chunk_content = headline_prefix + "\n\n".join(current_body)
        chunks.append(chunk_content)

    return chunks if chunks else [headline_prefix + text.strip()]


def chunk_text(text: str, source_type: str = "", headline: str = "") -> List[str]:
    """
    Unified structural chunker dispatcher based on source_type.
    """
    st_upper = source_type.upper()
    if "SEC" in st_upper or "FILING" in st_upper or "10-K" in st_upper or "10-Q" in st_upper:
        return chunk_sec_filing(text)
    elif "TRANSCRIPT" in st_upper or "EARNINGS" in st_upper or "CALL" in st_upper:
        return chunk_earnings_transcript(text)
    elif "NEWS" in st_upper or "WEB" in st_upper or "ARTICLE" in st_upper:
        return chunk_news_article(text, headline=headline)
    else:
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paras) <= 1 and len(text) > 1500:
            return [text[i:i+1500] for i in range(0, len(text), 1500)]
        return paras if paras else [text.strip()]


# ── VectorStore Class ────────────────────────────────────────────────

class VectorStore:
    """Chroma-backed long-term memory for ARA-1."""

    def __init__(self, collection_name: str = "ara1_findings"):
        settings = get_settings()
        self.persist_dir = settings.chroma_persist_dir
        self.embedding_model_name = settings.embedding_model
        self.fallback_docs: List[Dict[str, Any]] = []

        if CHROMADB_AVAILABLE:
            # Initialize Chroma client with persistence
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        else:
            self.client = None
            self.collection = None
            logger.warning("chromadb not installed. Operating in lightweight in-memory fallback mode.")

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedder = SentenceTransformer(self.embedding_model_name)
        else:
            self.embedder = None
            logger.warning("sentence_transformers not installed. Operating in text-based fallback mode.")

    def store(
        self,
        content: str,
        ticker: str = "",
        source_type: str = "",
        date: str = "",
        confidence: float = 1.0,
        researcher_session: str = "",
        verified: bool = True,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Embed and store a single document chunk in Chroma.

        Returns:
            The document ID.
        """
        doc_id = doc_id or str(uuid.uuid4())
        metadata = {
            "ticker": str(ticker or ""),
            "source_type": str(source_type or ""),
            "date": str(date or ""),
            "confidence": float(confidence),
            "researcher_session": str(researcher_session or ""),
            "verified": bool(verified),
        }

        if self.collection and self.embedder:
            embedding = self.embedder.encode(content).tolist()
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
            )
        else:
            self.fallback_docs.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata,
            })

        logger.info(f"Stored document id={doc_id} ticker={ticker} source={source_type}")
        return doc_id

    def store_financial_statement(
        self,
        financial_data: Union[Dict[str, Any], str],
        ticker: str,
        date: str = "",
        source_type: str = "SEC_FINANCIAL_STATEMENT",
        confidence: float = 1.0,
        researcher_session: str = "",
        verified: bool = True,
    ) -> str:
        """
        Store financial statements as structured metadata per Section A3.3,
        not raw prose.
        """
        if isinstance(financial_data, dict):
            import json
            summary_content = f"Financial statement summary for {ticker} ({date}): " + ", ".join(
                f"{k}={v}" for k, v in financial_data.items() if not isinstance(v, (dict, list))
            )
            raw_data_str = json.dumps(financial_data)
        else:
            summary_content = f"Financial statement summary for {ticker} ({date}): {financial_data[:200]}"
            raw_data_str = str(financial_data)

        doc_id = str(uuid.uuid4())
        metadata = {
            "ticker": str(ticker),
            "source_type": str(source_type),
            "date": str(date),
            "confidence": float(confidence),
            "researcher_session": str(researcher_session),
            "verified": bool(verified),
            "is_financial_statement": True,
            "financial_data": raw_data_str[:4000],
        }

        if self.collection and self.embedder:
            embedding = self.embedder.encode(summary_content).tolist()
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[summary_content],
                metadatas=[metadata],
            )
        else:
            self.fallback_docs.append({
                "id": doc_id,
                "content": summary_content,
                "metadata": metadata,
            })

        logger.info(f"Stored financial statement id={doc_id} ticker={ticker}")
        return doc_id

    def chunk_and_store(
        self,
        content: str,
        ticker: str = "",
        source_type: str = "",
        date: str = "",
        confidence: float = 1.0,
        researcher_session: str = "",
        verified: bool = True,
        headline: str = "",
    ) -> List[str]:
        """
        Structural chunking + bulk embedding and storage.
        """
        chunks = chunk_text(content, source_type=source_type, headline=headline)
        if not chunks:
            return []

        doc_ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{uuid.uuid4().hex[:12]}_{i}"
            stored_id = self.store(
                content=chunk,
                ticker=ticker,
                source_type=source_type,
                date=date,
                confidence=confidence,
                researcher_session=researcher_session,
                verified=verified,
                doc_id=chunk_id,
            )
            doc_ids.append(stored_id)

        logger.info(f"Chunked and stored {len(doc_ids)} chunks for ticker={ticker} source={source_type}")
        return doc_ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        ticker: Optional[str] = None,
        source_type: Optional[str] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        where_filter: Optional[dict] = None,
    ) -> List[dict]:
        """
        Semantic search against stored findings with metadata filtering.
        """
        if self.collection and self.embedder:
            query_embedding = self.embedder.encode(query).tolist()
            filters = []
            if where_filter:
                filters.append(where_filter)
            if ticker:
                filters.append({"ticker": {"$eq": ticker}})
            if source_type:
                filters.append({"source_type": {"$eq": source_type}})

            final_where = None
            if len(filters) == 1:
                final_where = filters[0]
            elif len(filters) > 1:
                final_where = {"$and": filters}

            fetch_k = top_k * 3 if (date_start or date_end) else top_k

            kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": min(fetch_k, self.collection.count()) if self.collection.count() > 0 else fetch_k,
            }
            if final_where:
                kwargs["where"] = final_where

            results = self.collection.query(**kwargs)

            output = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    doc_date = meta.get("date", "")

                    if date_start and doc_date and doc_date < date_start:
                        continue
                    if date_end and doc_date and doc_date > date_end:
                        continue

                    output.append({
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": meta,
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    })
                    if len(output) >= top_k:
                        break

            logger.info(f"Vector search returned {len(output)} results for query='{query[:50]}...'")
            return output
        else:
            # Fallback text search with keyword scoring and metadata filtering
            scored_candidates = []
            query_terms = [t for t in re.findall(r'\w+', query.lower()) if len(t) > 1]
            for doc in self.fallback_docs:
                meta = doc.get("metadata", {})
                if ticker and meta.get("ticker") != ticker:
                    continue
                if source_type and meta.get("source_type") != source_type:
                    continue

                doc_date = meta.get("date", "")
                if date_start and doc_date and doc_date < date_start:
                    continue
                if date_end and doc_date and doc_date > date_end:
                    continue

                content_lower = doc["content"].lower()
                if not query_terms:
                    score = 1.0 if query.lower() in content_lower else 0.0
                else:
                    matches = sum(1 for term in query_terms if term in content_lower)
                    score = matches / len(query_terms)

                if score > 0.0:
                    scored_candidates.append((score, doc))

            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            output = [doc for score, doc in scored_candidates[:top_k]]
            logger.info(f"Fallback search returned {len(output)} results for query='{query[:50]}...'")
            return output

    def count(self) -> int:
        """Return the number of documents in the collection."""
        if self.collection:
            return self.collection.count()
        return len(self.fallback_docs)

    def delete_collection(self):
        """Delete the entire collection (for testing/reset)."""
        if self.client and self.collection:
            self.client.delete_collection(self.collection.name)
        self.fallback_docs = []
        logger.warning("Collection reset.")


_shared_vector_store_instance: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the global shared VectorStore instance."""
    global _shared_vector_store_instance
    if _shared_vector_store_instance is None:
        _shared_vector_store_instance = VectorStore()
    return _shared_vector_store_instance


def reset_shared_vector_store():
    """Reset global shared VectorStore instance (for testing)."""
    global _shared_vector_store_instance
    _shared_vector_store_instance = None
