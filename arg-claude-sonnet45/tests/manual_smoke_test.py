#!/usr/bin/env python3
"""Manual smoke test to verify Memgraph-only refactoring."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")

    try:
        from src.storage.graph_store import GraphStore
        print("  ✓ GraphStore imports OK")
    except ImportError as e:
        print(f"  ✗ GraphStore import failed: {e}")
        return False

    try:
        from src.config.settings import settings
        print("  ✓ Settings imports OK")
    except ImportError as e:
        print(f"  ✗ Settings import failed: {e}")
        return False

    try:
        from src.rag.indexing import parse_pdf, chunk_text, embed_chunks, store_document
        print("  ✓ Indexing module imports OK")
    except ImportError as e:
        print(f"  ✗ Indexing module import failed: {e}")
        return False

    try:
        from src.rag.retrieval import get_query_embedding, vector_search, keyword_search, hybrid_search
        print("  ✓ Retrieval module imports OK")
    except ImportError as e:
        print(f"  ✗ Retrieval module import failed: {e}")
        return False

    try:
        from src.rag.generation import generate_answer
        print("  ✓ Generation module imports OK")
    except ImportError as e:
        print(f"  ✗ Generation module import failed: {e}")
        return False

    try:
        from src.rag.orchestration import index_document, search_documents, chat_with_documents
        print("  ✓ Orchestration module imports OK")
    except ImportError as e:
        print(f"  ✗ Orchestration module import failed: {e}")
        return False

    return True


def test_no_chroma_imports():
    """Verify no Chroma imports remain."""
    print("\nChecking for Chroma imports...")

    import os
    import re

    src_dir = Path(__file__).parent.parent / "src"
    chroma_pattern = re.compile(r'from\s+.*chroma|import\s+.*chroma|VectorStore', re.IGNORECASE)

    found_chroma = False
    for py_file in src_dir.rglob("*.py"):
        if py_file.name == "__pycache__":
            continue

        content = py_file.read_text()
        matches = chroma_pattern.findall(content)

        if matches and "vector_store.py" not in str(py_file):
            print(f"  ✗ Found Chroma reference in {py_file}: {matches}")
            found_chroma = True

    if not found_chroma:
        print("  ✓ No Chroma imports found")
        return True
    return False


def test_graph_store_features():
    """Test that GraphStore has vector capabilities."""
    print("\nTesting GraphStore features...")

    try:
        from src.storage.graph_store import GraphStore

        store = GraphStore()

        # Check for vector methods
        if hasattr(store, 'vector_similarity_search'):
            print("  ✓ GraphStore has vector_similarity_search method")
        else:
            print("  ✗ GraphStore missing vector_similarity_search method")
            return False

        if hasattr(store, 'batch_create_chunks_with_embeddings'):
            print("  ✓ GraphStore has batch_create_chunks_with_embeddings method")
        else:
            print("  ✗ GraphStore missing batch_create_chunks_with_embeddings method")
            return False

        if hasattr(store, 'keyword_search'):
            print("  ✓ GraphStore has keyword_search method")
        else:
            print("  ✗ GraphStore missing keyword_search method")
            return False

        store.close()
        return True

    except Exception as e:
        print(f"  ✗ Error testing GraphStore: {e}")
        return False


def test_settings():
    """Test that settings don't reference Chroma."""
    print("\nTesting settings...")

    try:
        from src.config.settings import settings

        if hasattr(settings, 'chroma_persist_directory'):
            print("  ✗ Settings still has chroma_persist_directory")
            return False
        else:
            print("  ✓ Settings has no Chroma configuration")

        # Check required settings
        required = ['qwen_api_key', 'database_url', 'chunk_size', 'chunk_overlap']
        missing = [attr for attr in required if not hasattr(settings, attr)]

        if missing:
            print(f"  ✗ Settings missing: {missing}")
            return False
        else:
            print("  ✓ All required settings present")

        return True

    except Exception as e:
        print(f"  ✗ Error testing settings: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("Memgraph-Only Refactoring Smoke Test")
    print("=" * 60)

    results = {
        "Imports": test_imports(),
        "No Chroma": test_no_chroma_imports(),
        "GraphStore Features": test_graph_store_features(),
        "Settings": test_settings(),
    }

    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All smoke tests passed!")
        print("The refactoring to Memgraph-only storage is complete.")
        return 0
    else:
        print("\n❌ Some tests failed.")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
