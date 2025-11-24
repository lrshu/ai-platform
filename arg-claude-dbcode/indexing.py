"""Indexing module for RAG backend system."""

import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dashscope import TextEmbedding

class QwenEmbeddings:
    def __init__(self):
        self.model = "text-embedding-v1"

    def embed_documents(self, texts):
        response = TextEmbedding.call(
            model=self.model,
            input=texts
        )
        return [result['embedding'] for result in response.output['embeddings']]

from langchain_community.graphs import Neo4jGraph
import uuid

# Load environment variables
load_dotenv()

class Indexing:
    """Handles document indexing operations."""

    def __init__(self):
        """Initialize indexing module with required configurations."""
        self.embeddings = QwenEmbeddings()
        self.graph = Neo4jGraph(
            url=os.getenv("DATABASE_URL"),
            username=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

    def parse_pdf(self, file_path: str) -> str:
        """
        Parse a PDF file and return its content as Markdown.

        Args:
            file_path: Path to the PDF file.

        Returns:
            str: PDF content in Markdown format.

        Raises:
            FileNotFoundError: If the file does not exist.
            Exception: If there's an error parsing the PDF.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            markdown_content = "\n".join([page.page_content for page in pages])
            return markdown_content
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")

    def split_content(self, markdown_content: str) -> List[Dict]:
        """
        Split Markdown content into manageable chunks.

        Args:
            markdown_content: Markdown content to split.

        Returns:
            List[Dict]: List of chunks with content and metadata.
        """
        chunks = self.text_splitter.split_text(markdown_content)
        chunk_list = []
        for i, chunk in enumerate(chunks):
            chunk_list.append({
                "content": chunk,
                "chunk_index": i,
                "metadata": {
                    "chunk_length": len(chunk),
                    "chunk_number": i + 1,
                    "total_chunks": len(chunks)
                }
            })
        return chunk_list

    def generate_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            chunks: List of chunks to generate embeddings for.

        Returns:
            List[Dict]: Chunks with embeddings added.
        """
        content_list = [chunk["content"] for chunk in chunks]
        embeddings = self.embeddings.embed_documents(content_list)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
        return chunks

    def extract_knowledge_graph(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract knowledge graph entities and relationships from chunks.

        Args:
            chunks: List of text chunks.

        Returns:
            List[Dict]: Chunks with knowledge graph information added.
        """
        # For demonstration, we'll extract simple entities (proper nouns)
        # In a real implementation, this would use a NER model or KG extraction service
        import re

        for chunk in chunks:
            content = chunk["content"]
            # Extract proper nouns using regex (simplified)
            entities = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', content)
            # Deduplicate entities
            unique_entities = list(set(entities))
            chunk["entities"] = unique_entities

            # Create simple relationships (demo only)
            relationships = []
            for entity1 in unique_entities:
                for entity2 in unique_entities:
                    if entity1 != entity2 and entity1 in content and entity2 in content:
                        relationships.append({
                            "source": entity1,
                            "target": entity2,
                            "type": "RELATED_TO"
                        })
            # Deduplicate relationships
            unique_relationships = []
            seen = set()
            for rel in relationships:
                key = (rel["source"], rel["target"], rel["type"])
                if key not in seen:
                    seen.add(key)
                    unique_relationships.append(rel)

            chunk["relationships"] = unique_relationships

        return chunks

    def store_content(self, name: str, chunks: List[Dict], file_path: str = "") -> str:
        """
        Store chunks, embeddings, and knowledge graph in Memgraph.

        Args:
            name: Name identifier for the document.
            chunks: List of chunks with embeddings and KG info.
            file_path: Path to the original PDF file (optional).

        Returns:
            str: Generated document ID.

        Raises:
            Exception: If storage fails.
        """
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())

            # Create document node
            document_query = """
            CREATE (d:Document {
                document_id: $document_id,
                document_name: $name,
                file_path: $file_path,
                created_at: datetime(),
                status: 'completed',
                chunk_count: $chunk_count
            })
            """
            self.graph.query(
                document_query,
                {"document_id": document_id, "name": name, "file_path": file_path, "chunk_count": len(chunks)}
            )

            # Create chunks and relationships
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())

                # Create text chunk node with embedding
                chunk_query = """
                CREATE (c:TextChunk {
                    chunk_id: $chunk_id,
                    content: $content,
                    chunk_index: $chunk_index,
                    embedding: $embedding,
                    metadata: $metadata
                })
                """
                self.graph.query(
                    chunk_query,
                    {"chunk_id": chunk_id, "content": chunk["content"], "chunk_index": chunk["chunk_index"],
                     "embedding": chunk["embedding"], "metadata": chunk["metadata"]}
                )

                # Create HAS_CHUNK relationship
                has_chunk_query = """
                MATCH (d:Document {document_id: $document_id}), (c:TextChunk {chunk_id: $chunk_id})
                CREATE (d)-[:HAS_CHUNK]->(c)
                """
                self.graph.query({"document_id": document_id, "chunk_id": chunk_id})

                # Create entities and relationships
                for entity_name in chunk["entities"]:
                    # Merge entity node
                    entity_query = """
                    MERGE (e:Entity {entity_name: $entity_name})
                    ON CREATE SET e.entity_id = $entity_id, e.entity_type = 'UNKNOWN'
                    """
                    entity_id = str(uuid.uuid4())
                    self.graph.query({"entity_name": entity_name, "entity_id": entity_id})

                    # Create MENTIONS relationship
                    mentions_query = """
                    MATCH (c:TextChunk {chunk_id: $chunk_id}), (e:Entity {entity_name: $entity_name})
                    CREATE (c)-[:MENTIONS]->(e)
                    """
                    self.graph.query({"chunk_id": chunk_id, "entity_name": entity_name})

                # Create entity relationships
                for rel in chunk["relationships"]:
                    relationship_query = """
                    MATCH (source:Entity {entity_name: $source}), (target:Entity {entity_name: $target})
                    MERGE (source)-[r:RELATED_TO]->(target)
                    """
                    self.graph.query({"source": rel["source"], "target": rel["target"]})

            return document_id
        except Exception as e:
            # Update document status to failed if there's an error
            update_status_query = """
            MATCH (d:Document {document_id: $document_id})
            SET d.status = 'failed'
            """
            if 'document_id' in locals():
                self.graph.query({"document_id": document_id})

            raise Exception(f"Failed to store content: {str(e)}")

if __name__ == "__main__":
    # Example usage
    indexing = Indexing()
    # pdf_path = "example.pdf"
    # md_content = indexing.parse_pdf(pdf_path)
    # chunks = indexing.split_content(md_content)
    # chunks_with_embeddings = indexing.generate_embeddings(chunks)
    # chunks_with_kg = indexing.extract_knowledge_graph(chunks_with_embeddings)
    # doc_id = indexing.store_content("example_doc", chunks_with_kg, pdf_path)
    # print(f"Indexed document with ID: {doc_id}")