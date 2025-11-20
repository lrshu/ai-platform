"""
Example script demonstrating how to use the RAG backend for document indexing.
"""

import asyncio
import os
from pathlib import Path
from app.indexing.orchestrator import IndexingOrchestrator


async def main():
    """Main function to demonstrate document indexing."""
    # Create indexing orchestrator
    orchestrator = IndexingOrchestrator()

    # Example document path (you would replace this with actual document paths)
    # For demonstration, we'll create a simple text file
    document_content = """
    This is a sample document for demonstration purposes.
    It contains multiple sentences to showcase the chunking capabilities.
    The RAG backend will parse this document, create chunks, generate embeddings,
    and store everything in the Memgraph database.

    This is another paragraph with more content.
    It will be processed as part of the indexing pipeline.

    The Small-to-Big chunking strategy will create parent chunks of approximately
    1000 tokens and child chunks of approximately 200 tokens with overlap.
    """

    # Create a temporary file for demonstration
    temp_file = Path("example_document.txt")
    temp_file.write_text(document_content)

    try:
        # Index the document
        print("Starting document indexing...")
        result = await orchestrator.index_document(temp_file, "example_collection")

        # Print results
        print("Indexing completed!")
        print(f"Status: {result['status']}")
        if result['status'] == 'completed':
            print(f"Parent chunks: {result['parent_chunks']}")
            print(f"Child chunks: {result['child_chunks']}")
            print(f"Entities: {result['entities']}")
            print(f"Relationships: {result['relationships']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"Error during indexing: {e}")

    finally:
        # Clean up temporary file
        if temp_file.exists():
            temp_file.unlink()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())