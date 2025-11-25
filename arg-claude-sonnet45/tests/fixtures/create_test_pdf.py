"""Script to create a simple test PDF for integration tests."""

from pathlib import Path


def create_simple_test_pdf():
    """Create a minimal test PDF using reportlab if available, or pymupdf."""
    output_path = Path(__file__).parent / "test_document.pdf"

    try:
        # Try using reportlab (most common PDF creation library)
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(output_path), pagesize=letter)

        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Test Document for RAG System")

        # Add content
        c.setFont("Helvetica", 12)
        y_position = 700

        content = [
            "",
            "Introduction",
            "This is a test document for the RAG (Retrieval-Augmented Generation) backend system.",
            "It contains sample content to test document indexing, retrieval, and question answering.",
            "",
            "Main Content",
            "The RAG system processes documents through several stages:",
            "1. Indexing: Documents are parsed, chunked, and embedded",
            "2. Retrieval: Relevant chunks are found using hybrid search",
            "3. Generation: Answers are generated with citations",
            "",
            "Technical Details",
            "The system uses Memgraph as unified storage for both vector embeddings",
            "and graph relationships. This provides efficient similarity search",
            "while maintaining document structure and relationships.",
            "",
            "Vector embeddings are computed using Qwen text-embedding-v4 model,",
            "which produces 1024-dimensional vectors for semantic search.",
            "",
            "Conclusion",
            "This test document helps verify that the RAG pipeline correctly",
            "handles PDF parsing, chunking, embedding, storage, and retrieval.",
        ]

        for line in content:
            if line:
                c.drawString(100, y_position, line)
            y_position -= 20

            if y_position < 100:  # Start new page if needed
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 750

        c.save()
        print(f"✓ Created test PDF: {output_path}")
        return str(output_path)

    except ImportError:
        print("reportlab not installed. Trying alternative method...")

        try:
            # Alternative: Use PyMuPDF (fitz) to create PDF
            import fitz  # PyMuPDF

            doc = fitz.open()
            page = doc.new_page(width=595, height=842)  # A4 size

            # Add text
            text = """Test Document for RAG System

Introduction
This is a test document for the RAG (Retrieval-Augmented Generation) backend system.
It contains sample content to test document indexing, retrieval, and question answering.

Main Content
The RAG system processes documents through several stages:
1. Indexing: Documents are parsed, chunked, and embedded
2. Retrieval: Relevant chunks are found using hybrid search
3. Generation: Answers are generated with citations

Technical Details
The system uses Memgraph as unified storage for both vector embeddings
and graph relationships. This provides efficient similarity search
while maintaining document structure and relationships.

Vector embeddings are computed using Qwen text-embedding-v4 model,
which produces 1024-dimensional vectors for semantic search.

Conclusion
This test document helps verify that the RAG pipeline correctly
handles PDF parsing, chunking, embedding, storage, and retrieval."""

            page.insert_text((72, 72), text, fontsize=11)
            doc.save(str(output_path))
            doc.close()

            print(f"✓ Created test PDF: {output_path}")
            return str(output_path)

        except ImportError:
            print("ERROR: Neither reportlab nor PyMuPDF available for PDF creation")
            print("Install one with: pip install reportlab  OR  pip install PyMuPDF")
            return None


if __name__ == "__main__":
    create_simple_test_pdf()
