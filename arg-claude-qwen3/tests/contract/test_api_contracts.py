"""
Contract tests for the RAG backend API endpoints.
"""

import pytest
import yaml
import os


class TestAPIContracts:
    """Test that API contracts are properly defined and consistent."""

    def test_indexing_contract_exists(self):
        """Test that the indexing API contract exists and is valid."""
        contract_path = "specs/001-rag-backend/contracts/indexing.yaml"
        assert os.path.exists(contract_path), f"Contract file {contract_path} does not exist"

        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)

        assert contract is not None
        assert 'openapi' in contract
        assert 'paths' in contract
        assert '/index' in contract['paths']

    def test_search_contract_exists(self):
        """Test that the search API contract exists and is valid."""
        contract_path = "specs/001-rag-backend/contracts/search.yaml"
        assert os.path.exists(contract_path), f"Contract file {contract_path} does not exist"

        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)

        assert contract is not None
        assert 'openapi' in contract
        assert 'paths' in contract
        assert '/search' in contract['paths']

    def test_chat_contract_exists(self):
        """Test that the chat API contract exists and is valid."""
        contract_path = "specs/001-rag-backend/contracts/chat.yaml"
        assert os.path.exists(contract_path), f"Contract file {contract_path} does not exist"

        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)

        assert contract is not None
        assert 'openapi' in contract
        assert 'paths' in contract
        assert '/chat' in contract['paths']

    def test_contract_consistency(self):
        """Test that contracts are consistent with each other."""
        # All contracts should have the same version
        contracts = [
            "specs/001-rag-backend/contracts/indexing.yaml",
            "specs/001-rag-backend/contracts/search.yaml",
            "specs/001-rag-backend/contracts/chat.yaml"
        ]

        versions = []
        for contract_path in contracts:
            assert os.path.exists(contract_path), f"Contract file {contract_path} does not exist"

            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)

            versions.append(contract['info']['version'])

        # All versions should be the same
        assert len(set(versions)) == 1, "All contracts should have the same version"


if __name__ == "__main__":
    pytest.main([__file__])