from gqlalchemy import Memgraph
from . import config

def get_memgraph():
    memgraph = Memgraph(host=config.DATABASE_URL.split("://")[1].split(":")[0], port=int(config.DATABASE_URL.split(":")[2]))
    return memgraph

from .models import TextChunk, Entity, Relationship
from .indexing import Graph

def save_graph(memgraph: Memgraph, graph: Graph, document_id: str, knowledge_base_name: str):
    """
    Saves a knowledge graph to Memgraph.
    """
    for node_name in graph.nodes:
        entity = Entity(name=node_name).save(memgraph)
        # Link entity to document
        memgraph.execute(f"MATCH (d:Document {{id: '{document_id}'}}), (e:Entity {{name: '{node_name}'}}) CREATE (d)-[:CONTAINS]->(e)")

    for source, target, relationship in graph.edges:
        source_node = Entity(name=source).save(memgraph)
        target_node = Entity(name=target).save(memgraph)
        Relationship(start_node=source_node, end_node=target_node, type=relationship).save(memgraph)

def save_chunks(memgraph: Memgraph, chunks: list[str], embeddings: list[list[float]], document_id: str):
    """
    Saves text chunks and their embeddings to Memgraph.
    """
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{document_id}_{i}"
        TextChunk(id=chunk_id, document_id=document_id, text=chunk, vector=embedding).save(memgraph)
