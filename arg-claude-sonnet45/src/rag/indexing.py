"""Document indexing pipeline: PDF parsing, chunking, embedding, and storage."""

import time
from pathlib import Path
from uuid import UUID

import pymupdf4llm
from dashscope import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.logging import get_logger
from src.config.settings import settings
from src.models.document import ChunkMetadata, Document, DocumentChunk
from src.storage.graph_store import GraphStore

logger = get_logger(__name__)


def parse_pdf(file_path: str) -> str:
    """Parse PDF file and convert to markdown format.

    Args:
        file_path: Absolute path to PDF file

    Returns:
        Markdown-formatted text content

    Raises:
        FileNotFoundError: If file_path does not exist
        ValueError: If file is not a valid PDF
        RuntimeError: If parsing fails
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.suffix.lower() == ".pdf":
        raise ValueError(f"File must be a PDF (.pdf extension required): {file_path}")

    try:
        logger.info(
            f"Parsing PDF: {file_path}",
            extra={"stage": "parse_pdf", "file": file_path},
        )
        start_time = time.time()
        markdown = pymupdf4llm.to_markdown(file_path)
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Parsed PDF successfully",
            extra={"stage": "parse_pdf", "duration_ms": duration_ms, "length": len(markdown)},
        )
        return markdown
    except Exception as e:
        logger.error(
            f"Failed to parse PDF: {e}",
            extra={"stage": "parse_pdf", "file": file_path},
            exc_info=True,
        )
        raise RuntimeError(f"Failed to parse PDF: {e}") from e


def chunk_text(markdown: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split markdown text into semantically coherent chunks.

    Args:
        markdown: Markdown-formatted text
        chunk_size: Target size per chunk in characters
        overlap: Character overlap between consecutive chunks

    Returns:
        List of text chunks

    Raises:
        ValueError: If chunk_size < 100 or overlap >= chunk_size
    """
    if chunk_size < 100:
        raise ValueError("chunk_size must be at least 100")

    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")

    try:
        logger.info(
            f"Chunking text",
            extra={"stage": "chunk_text", "text_length": len(markdown), "chunk_size": chunk_size},
        )
        start_time = time.time()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        chunks = splitter.split_text(markdown)
        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Created {len(chunks)} chunks",
            extra={"stage": "chunk_text", "count": len(chunks), "duration_ms": duration_ms},
        )
        return chunks
    except Exception as e:
        logger.error(
            f"Failed to chunk text: {e}",
            extra={"stage": "chunk_text"},
            exc_info=True,
        )
        raise


def embed_chunks(chunks: list[str]) -> list[tuple[str, list[float]]]:
    """Generate embeddings for text chunks using Qwen text-embedding-v4.

    Args:
        chunks: List of text chunks

    Returns:
        List of (chunk_text, embedding_vector) pairs

    Raises:
        RuntimeError: If embedding API is unavailable
        ValueError: If chunks list is empty
    """
    if not chunks:
        raise ValueError("chunks list cannot be empty")

    try:
        logger.info(
            f"Embedding {len(chunks)} chunks",
            extra={"stage": "embed_chunks", "count": len(chunks)},
        )
        start_time = time.time()

        # Batch embed (DashScope supports up to 25 texts per call)
        batch_size = 25
        all_embeddings = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            try:
                response = TextEmbedding.call(
                    model="text-embedding-v4",
                    input=batch,
                    api_key=settings.qwen_api_key,
                )

                if response.status_code == 200:
                    batch_embeddings = [item["embedding"] for item in response.output["embeddings"]]
                    all_embeddings.extend(batch_embeddings)
                else:
                    raise RuntimeError(f"Embedding API error: {response.message}")

            except Exception as e:
                logger.warning(
                    f"Failed to embed batch {i // batch_size + 1}: {e}",
                    extra={"stage": "embed_chunks", "batch": i // batch_size + 1},
                )
                # Skip failed batch
                continue

        if len(all_embeddings) != len(chunks):
            logger.warning(
                f"Embedded only {len(all_embeddings)}/{len(chunks)} chunks",
                extra={"stage": "embed_chunks"},
            )

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Embedded {len(all_embeddings)} chunks successfully",
            extra={"stage": "embed_chunks", "count": len(all_embeddings), "duration_ms": duration_ms},
        )

        return list(zip(chunks[: len(all_embeddings)], all_embeddings))

    except Exception as e:
        logger.error(
            f"Failed to embed chunks: {e}",
            extra={"stage": "embed_chunks"},
            exc_info=True,
        )
        raise RuntimeError(f"Failed to embed chunks: {e}") from e


def store_document(
    name: str,
    embeddings: list[tuple[str, list[float]]],
    metadata: dict[str, str | int],
) -> UUID:
    """Store document chunks with embeddings in Memgraph (unified storage).

    Args:
        name: Document namespace/collection name
        embeddings: Chunk texts and embeddings
        metadata: Document metadata (filename, file_path, file_size required)

    Returns:
        Unique document ID

    Raises:
        ValueError: If name invalid or metadata missing required keys
        RuntimeError: If storage operations fail
    """
    required_keys = {"filename", "file_path", "file_size"}
    if not required_keys.issubset(metadata.keys()):
        raise ValueError(f"metadata must contain: {required_keys}")

    try:
        logger.info(
            f"Storing document with {len(embeddings)} chunks in Memgraph",
            extra={"stage": "store_document", "namespace": name, "chunks": len(embeddings)},
        )
        start_time = time.time()

        # Create document model
        document = Document(
            name=name,
            filename=str(metadata["filename"]),
            file_path=str(metadata["file_path"]),
            file_size=int(metadata["file_size"]),
            chunk_count=len(embeddings),
            processing_status="completed",
        )

        # Store in Memgraph (both graph and vectors in one place)
        graph_store = GraphStore()

        # Create document node
        graph_store.create_document_node(
            doc_id=document.id,
            namespace=name,
            filename=document.filename,
            file_path=document.file_path,
            chunk_count=document.chunk_count,
            metadata={
                "file_size": document.file_size,
                "processing_status": document.processing_status,
            },
        )

        # Prepare chunk data for batch insert
        chunks_data = []
        for position, (text, embedding) in enumerate(embeddings):
            chunk_metadata = {
                "document_name": name,
                "filename": str(metadata["filename"]),
                "position": position,
            }
            chunk = DocumentChunk(
                document_id=document.id,
                text=text,
                embedding=embedding,
                position=position,
                char_offset=position * settings.chunk_size,  # Approximate
                metadata=ChunkMetadata(
                    document_name=name,
                    filename=str(metadata["filename"]),
                ),
            )

            chunks_data.append((
                str(chunk.id),  # chunk_id
                text,  # text
                embedding,  # embedding vector
                position,  # position
                chunk.char_offset,  # char_offset
                chunk_metadata,  # metadata
            ))

        # Batch create chunks with embeddings
        graph_store.batch_create_chunks_with_embeddings(
            namespace=name,
            document_id=document.id,
            chunks_data=chunks_data,
        )

        graph_store.close()

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Stored document successfully in Memgraph",
            extra={
                "stage": "store_document",
                "document_id": str(document.id),
                "duration_ms": duration_ms,
            },
        )

        return document.id

    except Exception as e:
        logger.error(
            f"Failed to store document: {e}",
            extra={"stage": "store_document", "namespace": name},
            exc_info=True,
        )
        raise RuntimeError(f"Failed to store document: {e}") from e
