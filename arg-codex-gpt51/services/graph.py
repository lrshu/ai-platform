from __future__ import annotations

from typing import Iterable, Sequence

from neo4j import GraphDatabase

from services.config import get_settings
from services.models import GraphEdge, RetrievalResult, VectorRecord


def _ensure_list(values: Iterable[float]) -> list[float]:
    return list(values)


def _execute_write(session, func, *args, **kwargs):
    if hasattr(session, "execute_write"):
        return session.execute_write(func, *args, **kwargs)
    return session.write_transaction(func, *args, **kwargs)


def _execute_read(session, func, *args, **kwargs):
    if hasattr(session, "execute_read"):
        return session.execute_read(func, *args, **kwargs)
    return session.read_transaction(func, *args, **kwargs)


class GraphStore:
    def __init__(self):
        settings = get_settings()
        self._driver = GraphDatabase.driver(
            settings.database_url,
            auth=(settings.database_user or "", settings.database_password or ""),
        )
        with self._driver.session() as session:
            self._ensure_indexes(session)

    def close(self):
        self._driver.close()

    def store_vectors(self, name: str, vectors: Sequence[VectorRecord]):
        with self._driver.session() as session:
            _execute_write(session, self._create_collection, name)
            for idx, record in enumerate(vectors):
                _execute_write(session, self._create_chunk, name, idx, record)

    def store_graph(self, name: str, edges: Sequence[GraphEdge]):
        if not edges:
            return
        with self._driver.session() as session:
            for edge in edges:
                _execute_write(session, self._create_edge, name, edge)

    @staticmethod
    def _create_collection(tx, name: str):
        tx.run(
            "MERGE (c:Collection {name: $name}) RETURN c",
            name=name,
        )

    @staticmethod
    def _create_chunk(tx, name: str, idx: int, record: VectorRecord):
        tx.run(
            "MERGE (c:Collection {name: $name})"
            "CREATE (chunk:Chunk {cid: $cid, content: $content, embedding: $embedding})"
            "MERGE (chunk)-[:IN]->(c)",
            name=name,
            cid=f"{name}_{idx}",
            content=record.content,
            embedding=_ensure_list(record.embedding),
        )

    @staticmethod
    def _create_edge(tx, name: str, edge: GraphEdge):
        tx.run(
            "MATCH (c:Collection {name: $name})"
            "MERGE (src:Chunk {cid: $src_cid})-[:IN]->(c)"
            "MERGE (dst:Chunk {cid: $dst_cid})-[:IN]->(c)"
            "MERGE (src)-[r:RELATION {type: $relation}]->(dst)"
            "SET r.weight = $weight",
            name=name,
            src_cid=edge.source,
            dst_cid=edge.target,
            relation=edge.relation,
            weight=edge.weight,
        )

    def vector_search(self, name: str, query_embedding: Sequence[float], top_k: int) -> list[RetrievalResult]:
        embedding = _ensure_list(query_embedding)
        if not embedding:
            return []
        with self._driver.session() as session:
            result = _execute_read(session, self._vector_similarity_search, name, embedding, top_k)
        return [
            RetrievalResult(content=row["chunk"]["content"], score=row["score"], metadata={"cid": row["chunk"]["cid"]})
            for row in result
        ]

    @staticmethod
    def _vector_similarity_search(tx, name: str, embedding: list[float], top_k: int):
        query = (
            "CALL vector_search.search('chunk_embedding_index', $top_k, $embedding) "
            "YIELD node AS chunk, similarity as score "
            "MATCH (chunk)-[:IN]->(c:Collection {name: $name}) "
            "WHERE chunk.embedding IS NOT NULL AND score > 0.0 "
            "RETURN chunk, score ORDER BY score DESC LIMIT $top_k"
        )
        return tx.run(
            query,
            name=name,
            embedding=embedding,
            top_k=top_k
        ).data()

    @staticmethod
    def _ensure_indexes(tx):
        tx.run("CREATE TEXT INDEX collection_name_index ON :Collection(name)")
        tx.run("CREATE TEXT INDEX chunk_cid_index ON :Chunk(cid)")
        tx.run("""CREATE VECTOR INDEX chunk_embedding_index ON :Chunk(embedding) WITH CONFIG {"dimension": 1536, "metric": "cos", "capacity": 1000 }""")

    def keyword_search(self, name: str, question: str, top_k: int) -> list[RetrievalResult]:
        with self._driver.session() as session:
            data = _execute_read(session, self._keyword_search, name, question, top_k)
        return [
            RetrievalResult(content=row["chunk"]["content"], score=row["score"], metadata={"cid": row["chunk"]["cid"]})
            for row in data
        ]

    def graph_search(self, name: str, question: str, top_k: int) -> list[RetrievalResult]:
        with self._driver.session() as session:
            rows = _execute_read(session, self._relationship_search, name, question, top_k)
        results: list[RetrievalResult] = []
        for row in rows:
            metadata = {"cid": row.get("cid")}
            content = f"{row.get('cid', '')} {row.get('type', '')} {row.get('dst_cid', '')}"
            results.append(
                RetrievalResult(content=content, score=row["score"], metadata=metadata)
            )
        return results

    @staticmethod
    def _keyword_search(tx, name: str, question: str, top_k: int):
        query = (
            "MATCH (chunk:Chunk)-[:IN]->(c:Collection {name: $name}) "
            "WHERE toLower(chunk.content) CONTAINS toLower($question) "
            "RETURN chunk, 1.0 AS score LIMIT $top_k"
        )
        return tx.run(query, name=name, question=question, top_k=top_k).data()

    @staticmethod
    def _relationship_search(tx, name: str, question: str, top_k: int):
        query = (
            "MATCH (chunk:Chunk)-[:RELATION]->(:Chunk)-[:IN]->(c:Collection {name: $name}) "
            "WHERE toLower(chunk.cid) CONTAINS toLower($question) "
            "OPTIONAL MATCH (src)-[r:RELATION]->(dst:Chunk) "
            "WHERE src.cid = chunk.cid or dst.cid = chunk.cid "
            "RETURN src.cid AS cid,0.8 AS score,r.type AS type,r.weight AS weight,dst.cid AS dst_cid LIMIT $top_k"
        )
        return tx.run(query, name=name, question=question, top_k=top_k).data()
