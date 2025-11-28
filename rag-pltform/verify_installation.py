"""
Script to verify that all required packages and modules can be imported correctly.
"""
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_external_packages():
    """Verify that external packages can be imported."""
    print("Verifying external package imports...")

    packages = [
        ("langchain", "langchain"),
        ("langchain_core", "langchain_core"),
        ("neo4j", "neo4j"),
        ("pymupdf", "fitz"),
        ("python-dotenv", "dotenv"),
        ("openai", "openai"),
    ]

    success_count = 0
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {package_name} - {e}")

    print(f"External packages: {success_count}/{len(packages)} imported successfully\n")
    return success_count == len(packages)

def verify_internal_modules():
    """Verify that internal modules can be imported."""
    print("Verifying internal module imports...")

    modules = [
        # Models
        ("src.models.base", "src.models.base"),
        ("src.models.document", "src.models.document"),
        ("src.models.chunk", "src.models.chunk"),
        ("src.models.vector", "src.models.vector"),
        ("src.models.knowledge_graph", "src.models.knowledge_graph"),
        ("src.models.query", "src.models.query"),
        ("src.models.search_result", "src.models.search_result"),
        ("src.models.conversation", "src.models.conversation"),
        ("src.models.response", "src.models.response"),

        # Lib
        ("src.lib.exceptions", "src.lib.exceptions"),
        ("src.lib.database", "src.lib.database"),
        ("src.lib.config", "src.lib.config"),
        ("src.lib.logging", "src.lib.logging"),
        ("src.lib.llm_client", "src.lib.llm_client"),
        ("src.lib.pdf_parser", "src.lib.pdf_parser"),
        ("src.lib.chunker", "src.lib.chunker"),
        ("src.lib.vector_store", "src.lib.vector_store"),
        ("src.lib.graph_store", "src.lib.graph_store"),

        # Services
        ("src.services.indexing", "src.services.indexing"),
        ("src.services.pre_retrieval", "src.services.pre_retrieval"),
        ("src.services.retrieval", "src.services.retrieval"),
        ("src.services.post_retrieval", "src.services.post_retrieval"),
        ("src.services.generation", "src.services.generation"),
        ("src.services.orchestration", "src.services.orchestration"),
    ]

    success_count = 0
    for module_name, import_path in modules:
        try:
            __import__(import_path)
            print(f"  ✅ {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {module_name} - {e}")

    print(f"Internal modules: {success_count}/{len(modules)} imported successfully\n")
    return success_count == len(modules)

def main():
    """Run verification."""
    print("RAG Platform Installation Verification")
    print("=" * 40)
    print()

    external_success = verify_external_packages()
    internal_success = verify_internal_modules()

    if external_success and internal_success:
        print("🎉 All packages and modules imported successfully!")
        print("The RAG Platform is ready to use.")
        return 0
    else:
        print("⚠️  Some imports failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())