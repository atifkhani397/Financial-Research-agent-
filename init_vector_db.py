"""
ARA-1 Vector Store Initialization Script

Run this once to create and verify the Chroma collection with the
correct schema. Also performs a quick round-trip test.
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# We need GROQ_API_KEY set even just for config init.
# For this init script only, set a dummy if not present.
if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "gsk_init_script_dummy_key"

from memory.vector_store import VectorStore


def main():
    print("=" * 60)
    print("  ARA-1 Vector Store Initialization")
    print("=" * 60)

    vs = VectorStore(collection_name="ara1_findings")
    print(f"✓ Chroma collection 'ara1_findings' ready at: {vs.persist_dir}")
    print(f"✓ Embedding model loaded: {vs.embedding_model_name}")
    print(f"  Current document count: {vs.count()}")

    # Round-trip test
    print("\nRunning round-trip test...")
    test_id = vs.store(
        content="Apple Inc reported Q3 2024 revenue of $85.8 billion, up 5% YoY.",
        ticker="AAPL",
        source_type="SEC_10Q",
        date="2024-08-01",
        confidence=0.95,
        researcher_session="init_test",
        verified=True,
        doc_id="init_test_001",
    )
    print(f"  ✓ Stored test document: id={test_id}")

    results = vs.search("Apple revenue Q3 2024", top_k=1)
    if results and results[0]["id"] == "init_test_001":
        print(f"  ✓ Retrieved test document successfully (distance={results[0]['distance']:.4f})")
    else:
        print("  ✗ Round-trip test FAILED")
        sys.exit(1)

    print(f"\n  Final document count: {vs.count()}")
    print("\n✓ Vector store initialization complete.")


if __name__ == "__main__":
    main()
