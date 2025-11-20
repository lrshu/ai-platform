#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Add current directory to Python path
sys.path.insert(0, '.')

def verify_imports():
    """Verify that all modules can be imported."""
    try:
        # Test core imports
        from app.common.config_loader import ConfigLoader
        from app.common.factory import ProviderFactory
        from app.common.models import SearchRequest, Chunk, DocumentMetadata
        print("OK: Core imports successful")

        # Test interface imports
        from app.common.interfaces.database import IDatabase
        from app.common.interfaces.generator import ITextGenerator
        from app.common.interfaces.embedder import IEmbedder
        from app.common.interfaces.reranker import IReranker
        from app.common.interfaces.parser import IDocumentParser
        print("OK: Interface imports successful")

        # Test implementation imports
        from app.database.memgraph_db import MemgraphDB
        from app.providers.qwen_provider import QwenProvider
        from app.providers.mineru_provider import MineruProvider
        from app.indexing.chunker import Chunker
        from app.indexing.orchestrator import IndexingOrchestrator
        print("OK: Implementation imports successful")

        # Test API imports
        from app.api.indexing import router
        print("OK: API imports successful")

        return True
    except Exception as e:
        print("ERROR: Import error: {}".format(e))
        return False

def main():
    """Main verification function."""
    print("Verifying RAG Backend Setup...")
    print()

    if verify_imports():
        print()
        print("SUCCESS: All verification checks passed!")
        print("The RAG backend setup is working correctly.")
        return 0
    else:
        print()
        print("FAILURE: Some verification checks failed.")
        print("Please check the errors above and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())