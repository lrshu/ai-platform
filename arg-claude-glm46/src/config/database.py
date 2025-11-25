"""Database configuration and connection management for Memgraph."""

import os
from neo4j import GraphDatabase


class DatabaseConfig:
    """Configuration for Memgraph database connection."""

    def __init__(self):
        """Initialize database configuration from environment variables."""
        self.uri = os.getenv("DATABASE_URL", "bolt://localhost:7687")
        self.username = os.getenv("DATABASE_USER", "")
        self.password = os.getenv("DATABASE_PASSWORD", "")

    def get_driver(self):
        """Create and return a Neo4j driver instance."""
        return GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password) if self.username or self.password else None
        )


# Global database configuration instance
db_config = DatabaseConfig()