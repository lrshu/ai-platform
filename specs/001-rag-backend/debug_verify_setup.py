#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to verify that the RAG backend setup is correct.
"""

import sys
import os
import traceback

# Add the project root to the path
sys.path.insert(0, '/Users/zhengliu/Desktop/workspace/work/study/ai-platform')

def verify_imports():
    """Verify that all modules can be imported."""
    try:
        # Test core imports
        print("Importing ConfigLoader...")
        from app.common.config_loader import ConfigLoader
        print("✅ ConfigLoader imported successfully")

        print("Importing ProviderFactory...")
        from app.common.factory import ProviderFactory
        print("✅ ProviderFactory imported successfully")

        print("Importing models...")
        from app.common.models import SearchRequest, Chunk, DocumentMetadata
        print("✅ Core imports successful")

        # Test interface imports
        print("Importing interfaces...")
        from app.common.interfaces.database import IDatabase
        from app.common.interfaces.generator import ITextGenerator
        from app.common.interfaces.embedder import IEmbedder
        from app.common.interfaces.reranker import IReranker
        from app.common.interfaces.parser import IDocumentParser
        print("✅ Interface imports successful")

        # Test implementation imports
        print("Importing implementations...")
        from app.database.memgraph_db import MemgraphDB
        from app.providers.qwen_provider import QwenProvider
        from app.providers.mineru_provider import MineruProvider
        from app.indexing.chunker import Chunker
        from app.indexing.orchestrator import IndexingOrchestrator
        print("✅ Implementation imports successful")

        # Test API imports
        print("Importing API...")
        from app.api.indexing import router
        print("✅ API imports successful")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def verify_config():
    """Verify that configuration can be loaded."""
    try:
        from app.common.config_loader import config_loader
        # Try to get a configuration value
        db_config = config_loader.get('database')
        if db_config:
            print("✅ Configuration loading successful")
            return True
        else:
            print("❌ Configuration loading failed")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        traceback.print_exc()
        return False

def verify_models():
    """Verify that Pydantic models work correctly."""
    try:
        from app.common.models import SearchRequest, DocumentMetadata, Chunk
        from datetime import datetime

        # Test SearchRequest model
        search_request = SearchRequest(
            query="test query",
            use_hyde=True,
            use_rerank=False,
            top_k=10
        )
        print("✅ SearchRequest model validation successful")

        # Test DocumentMetadata model
        metadata = DocumentMetadata(
            document_id="test_doc",
            start_index=0,
            end_index=100,
            source_type="txt"
        )
        print("✅ DocumentMetadata model validation successful")

        # Test Chunk model
        chunk = Chunk(
            id="test_chunk",
            content="test content",
            metadata=metadata
        )
        print("✅ Chunk model validation successful")

        return True
    except Exception as e:
        print(f"❌ Model validation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main verification function."""
    print("🔍 Verifying RAG Backend Setup...")
    print()

    # Check if we're in the right directory
    current_dir = os.getcwd()
    expected_dir = "/Users/zhengliu/Desktop/workspace/work/study/ai-platform/specs/001-rag-backend"
    if current_dir != expected_dir:
        print(f"⚠️  Warning: Current directory is {current_dir}")
        print(f"   Expected: {expected_dir}")
        print()

    # Run verification checks
    checks = [
        ("Import Verification", verify_imports),
        ("Configuration Verification", verify_config),
        ("Model Verification", verify_models)
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"🧪 {check_name}")
        if not check_func():
            all_passed = False
        print()

    if all_passed:
        print("🎉 All verification checks passed!")
        print("✅ The RAG backend setup is working correctly.")
        return 0
    else:
        print("❌ Some verification checks failed.")
        print("⚠️  Please check the errors above and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())