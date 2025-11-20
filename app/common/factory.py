"""
Factory pattern for provider instantiation based on configuration.
"""

from typing import Any, Dict, Type
import importlib
from app.common.config_loader import config_loader
from app.common.interfaces.database import IDatabase
from app.common.interfaces.generator import ITextGenerator
from app.common.interfaces.embedder import IEmbedder
from app.common.interfaces.reranker import IReranker
from app.common.interfaces.parser import IDocumentParser


class ProviderFactory:
    """Factory for creating provider instances based on configuration."""

    def __init__(self):
        """Initialize the provider factory."""
        self._provider_map = {
            'database': IDatabase,
            'generator': ITextGenerator,
            'embedder': IEmbedder,
            'reranker': IReranker,
            'parser': IDocumentParser
        }

    def create_provider(self, capability: str, **kwargs) -> Any:
        """
        Create a provider instance for a specific capability.

        Args:
            capability: The capability to create a provider for (database, generator, etc.)
            **kwargs: Additional arguments to pass to the provider constructor

        Returns:
            Provider instance

        Raises:
            ValueError: If capability is not supported or provider class cannot be found
            ImportError: If provider module cannot be imported
        """
        if capability not in self._provider_map:
            raise ValueError(f"Unsupported capability: {capability}")

        # Get the provider name from configuration
        capability_config = config_loader.get_capability_config(capability)
        if not capability_config:
            raise ValueError(f"No configuration found for capability: {capability}")

        provider_name = capability_config.get('provider')
        if not provider_name:
            raise ValueError(f"No provider specified for capability: {capability}")

        # Get the class path from configuration
        class_path = config_loader.get_provider_class(provider_name)
        if not class_path:
            raise ValueError(f"No class path found for provider: {provider_name}")

        # Split the class path into module and class name
        try:
            module_path, class_name = class_path.rsplit('.', 1)
        except ValueError:
            raise ValueError(f"Invalid class path format: {class_path}")

        # Import the module and get the class
        try:
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)
        except ImportError as e:
            raise ImportError(f"Could not import module {module_path}: {e}")
        except AttributeError:
            raise ValueError(f"Class {class_name} not found in module {module_path}")

        # Verify that the class implements the correct interface
        interface_class = self._provider_map[capability]
        if not issubclass(provider_class, interface_class):
            raise ValueError(f"Provider class {class_name} does not implement {interface_class.__name__}")

        # Create and return the provider instance
        return provider_class(**kwargs)

    def create_database_provider(self, **kwargs) -> IDatabase:
        """
        Create a database provider instance.

        Args:
            **kwargs: Additional arguments to pass to the provider constructor

        Returns:
            Database provider instance
        """
        return self.create_provider('database', **kwargs)

    def create_generator_provider(self, **kwargs) -> ITextGenerator:
        """
        Create a text generator provider instance.

        Args:
            **kwargs: Additional arguments to pass to the provider constructor

        Returns:
            Text generator provider instance
        """
        return self.create_provider('generator', **kwargs)

    def create_embedder_provider(self, **kwargs) -> IEmbedder:
        """
        Create an embedder provider instance.

        Args:
            **kwargs: Additional arguments to pass to the provider constructor

        Returns:
            Embedder provider instance
        """
        return self.create_provider('embedder', **kwargs)

    def create_reranker_provider(self, **kwargs) -> IReranker:
        """
        Create a reranker provider instance.

        Args:
            **kwargs: Additional arguments to pass to the provider constructor

        Returns:
            Reranker provider instance
        """
        return self.create_provider('reranker', **kwargs)

    def create_parser_provider(self, **kwargs) -> IDocumentParser:
        """
        Create a document parser provider instance.

        Args:
            **kwargs: Additional arguments to pass to the provider constructor

        Returns:
            Document parser provider instance
        """
        return self.create_provider('parser', **kwargs)


# Global provider factory instance
provider_factory = ProviderFactory()