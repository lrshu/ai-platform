from . import indexing
from . import database
from .models import Document
from datetime import datetime
import uuid

def index(name: str, file: str):
    """
    Orchestrates the indexing pipeline.
    """
    print(f"Indexing file {file} into knowledge base {name}...")

    # 1. Parse PDF
    text = indexing.parse_pdf(file)
    if not text:
        print("Failed to parse PDF.")
        return

    # 2. Chunk text
    chunks = indexing.chunk_text(text)

    # 3. Get embeddings
    embeddings = indexing.get_embeddings(chunks)

    # 4. Get knowledge graph
    graph = indexing.get_knowledge_graph(chunks)

    # 5. Save to Memgraph
    db = database.get_memgraph()
    if not db:
        print("Failed to connect to Memgraph.")
        return

    document_id = str(uuid.uuid4())
    doc = Document(id=document_id, knowledge_base_name=name, file_name=file, indexed_at=datetime.now()).save(db)

    database.save_chunks(db, chunks, embeddings, document_id)
    database.save_graph(db, graph, document_id, name)

    print("Successfully indexed file.")
