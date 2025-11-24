"""
Database connection and utilities for Memgraph.
"""

from neo4j import GraphDatabase
from typing import Optional, Any, Dict
import logging
from src.lib.config import get_config

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages connection to Memgraph database."""

    def __init__(self):
        """Initialize database connection parameters from environment."""
        config = get_config()
        self.uri = config.database_url
        self.user = config.database_user
        self.password = config.database_password
        self._driver: Optional[GraphDatabase] = None

    def connect(self) -> GraphDatabase:
        """
        Establish connection to the database.

        Returns:
            GraphDatabase driver instance
        """
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password) if self.user or self.password else None,
                    max_connection_lifetime=30 * 60,  # 30 minutes
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=2 * 60,  # 2 minutes
                )
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
        return self._driver

    def close(self) -> None:
        """Close database connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Database connection closed")

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query result
        """
        driver = self.connect()
        with driver.session() as session:
            try:
                result = session.run(query, parameters or {})
                return result
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            driver = self.connect()
            with driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database connection instance
db_connection = DatabaseConnection()


def get_db_connection() -> DatabaseConnection:
    """
    Get the global database connection instance.

    Returns:
        DatabaseConnection instance
    """
    return db_connection