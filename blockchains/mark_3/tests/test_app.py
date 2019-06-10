import pytest
import random

from flask import g
from jsonschema import validate
from unittest import mock

from ...mark_1.tests.test_blockchain import (sample_transaction_f,
                                             w_sample_blocks_f)
from .. import app as sut_app
from .test_blockchain import sample_sut


SCHEMA_DRAFT = "http://json-schema.org/draft-07/schema#"


@pytest.fixture(scope="function")
def client(sample_sut):
    client = sut_app.app.test_client()
    g.blockchain = sample_sut()
    return client


@pytest.fixture(scope="function")
def schema_def_genesis_hash():
    return {
        "type": "string",
        "minLength": 1,
        "maxLength": 1,
        "pattern": "0",
    }


@pytest.fixture(scope="function")
def schema_def_hash():
    return {
        "type": "string",
        "minLength": 64,
        "maxLength": 64,
    }


@pytest.fixture(scope="function")
def schema_def_transaction():
    return {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "format": "date-time",
            },
        },
        "additionalProperties": False,
        "required": [
            "data",
        ]
    }


@pytest.fixture(scope="function")
def schema_def_block():
    return {
        "type": "object",
        "properties": {
            "index": {
                "type": "number",
                "minimum": 1,
            },
            "timestamp": {
                "type": "number",
            },
            "transactions": {
                "$ref": "#/definitions/transactions"
            },
            "previous_hash": {
                "oneOf": [
                    {
                        "$ref": "#/definitions/genesis_hash"
                    },
                    {
                        "$ref": "#/definitions/hash"
                    },
                ]
            }
        },
        "additionalProperties": False,
        "required": [
            "index", "timestamp", "transactions", "previous_hash"
        ]
    }


@pytest.fixture(scope="function")
def schema_def_chain(schema_def_transaction,
                     schema_def_genesis_hash,
                     schema_def_hash,
                     schema_def_block):
    return {
        "$schema": SCHEMA_DRAFT,
        "definitions": {
            "transaction": schema_def_transaction,
            "transactions": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/transaction"
                },
                "minItems": 1,
                "uniqueItems": True,
            },
            "genesis_hash": schema_def_genesis_hash,
            "hash": schema_def_hash,
            "block": schema_def_block,
            "blocks": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/block"
                },
                "minItems": 1,
                "uniqueItems": True,
            },
        },
        "type": "object",
        "properties": {
            "chain": {
                "$ref": "#/definitions/blocks"
            },
            "is_valid": {
                "type": "boolean"
            }
        },
        "additionalProperties": False,
        "required": [
            "chain", "is_valid",
        ]
    }


@pytest.fixture(scope="function")
def schema_def_mine(schema_def_block):
    return {
        "$schema": SCHEMA_DRAFT,
        "definitions": {
            "block": schema_def_block,
        },
        "type": "object",
        "properties": {
            "new_block": {
                "oneOf": [
                    {
                        "$ref": "#/definitions/block"
                    },
                    {
                        "type": "null",
                    }
                ]
            },
            "is_valid": {
                "type": "boolean"
            }
        },
        "additionalProperties": False,
        "required": [
            "new_block", "is_valid",
        ]
    }


@pytest.fixture(scope="function")
def schema_def_evil_action(schema_def_transaction,
                           schema_def_genesis_hash,
                           schema_def_hash,
                           schema_def_block):
    return {
        "$schema": SCHEMA_DRAFT,
        "definitions": {
            "transaction": schema_def_transaction,
            "transactions": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/transaction"
                },
                "minItems": 1,
                "uniqueItems": True,
            },
            "genesis_hash": schema_def_genesis_hash,
            "hash": schema_def_hash,
            "block": schema_def_block,
        },
        "type": "object",
        "properties": {
            "status": {
                "oneOf": [
                    {
                        "type": "string",
                        "pattern": "Snap done!",
                    },
                    {
                        "type": "string",
                        "pattern": "Nothing to do...",
                    }
                ]
            },
            "element": {
                "oneOf": [
                    {
                        "$ref": "#/definitions/block",
                    },
                    {
                        "type": "null",
                    }
                ]
            },
        },
        "additionalProperties": False,
        "required": [
            "status", "element",
        ]
    }


@pytest.fixture(scope="function")
def schema_def_evaluate_consensus(schema_def_transaction,
                                  schema_def_genesis_hash,
                                  schema_def_hash,
                                  schema_def_block):
    return {
        "$schema": SCHEMA_DRAFT,
        "definitions": {
            "transaction": schema_def_transaction,
            "transactions": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/transaction"
                },
                "minItems": 1,
                "uniqueItems": True,
            },
            "genesis_hash": schema_def_genesis_hash,
            "hash": schema_def_hash,
            "block": schema_def_block,
            "blocks": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/block"
                },
                "minItems": 1,
                "uniqueItems": True,
            },
        },
        "type": "object",
        "properties": {
            "status": {
                "oneOf": [
                    {
                        "type": "string",
                        "pattern": "Chain replaced",
                    },
                    {
                        "type": "string",
                        "pattern": "Chain not replaced - master",
                    }
                ]
            },
            "chain": {
                "$ref": "#/definitions/blocks",
            }
        },
        "additionalProperties": False,
        "required": [
            "status", "chain",
        ]
    }


# Tests

class TestEvilActionEndpoint(object):
    """
    Test the evil action endpoint
    """

    def test_on_empty_chain(self, client, schema_def_evil_action):
        # Arrange
        schema = schema_def_evil_action
        # Act
        response = client.post('/action/evil', json={})
        # Assert
        assert response.status_code == 200
        validate(instance=response.json, schema=schema)

    def test_on_not_empty_chain(self,
                                client,
                                schema_def_evil_action,
                                w_sample_blocks_f):
        # Arrange
        schema = schema_def_evil_action
        with client:
            random_integer = random.randint(1, 10)
            g.blockchain = w_sample_blocks_f(random_integer)
            # Act
            response = client.post('/action/evil', json={})
            # Assert
            assert response.status_code == 200
            validate(instance=response.json, schema=schema)


class TestMineEndpoint(object):
    """
    Test the mine endpoint
    """

    def test_on_empty_chain(self, client, schema_def_mine):
        # Arrange
        schema = schema_def_mine
        # Act
        response = client.post('/mine', json={})
        # Assert
        assert response.status_code == 201
        validate(instance=response.json, schema=schema)

    def test_on_not_valid_chain(self,
                                client,
                                w_sample_blocks_f,
                                schema_def_mine):
        # Arrange
        schema = schema_def_mine
        with client:
            random_integer = 3
            g.blockchain = w_sample_blocks_f(random_integer)
            g.blockchain._chain[1]['index'] = 23
            # Act
            response = client.post('/mine', json={})
            # Assert
            assert response.status_code == 200
            validate(instance=response.json, schema=schema)


class TestTransactionEndpoint(object):
    """
    Test the transaction endpoint
    """

    def test_sample_transaction(self, client, sample_transaction_f):
        # Arrange
        payload = sample_transaction_f()
        # Act
        response = client.post('/transactions/new', json=payload)
        # Assert
        assert response.status_code == 201

    def test_empty_transaction(self, client):
        # Arrange
        payload = {}
        # Act
        response = client.post('/transactions/new', json=payload)
        # Assert
        assert response.status_code == 400


class TestChainEndpoint(object):
    """
    Test the chain endpoint
    """

    def test_validate_schema(self, client, schema_def_chain):
        # Arrange
        schema = schema_def_chain
        # Act
        response = client.get('/chain', json={})
        # Assert
        assert response.status_code == 200
        validate(instance=response.json, schema=schema)


class TestRegisterKnownNodeFunction(object):
    """
    Test the register_known_node function
    """

    def test_empty_url_address(self):
        # Arrange
        test_url = ""
        # Act
        # Assert
        with pytest.raises(ValueError):
            sut_app.register_known_node(test_url)

    def test_netloc_url_address(self, client):
        # Arrange
        test_url = "http://localhost:8082"
        extracted_test_url = "localhost:8082"
        # Act
        # Assert
        with client:
            sut_app.register_known_node(test_url)
            assert extracted_test_url in g.known_nodes

    def test_path_url_address(self, client):
        # Arrange
        test_url = "localhost:8082"
        extracted_test_url = "localhost:8082"
        # Act
        # Assert
        with client:
            sut_app.register_known_node(test_url)
            assert extracted_test_url in g.known_nodes


class TestRegisterNodesEndpoint(object):
    """
    Test the register known nodes endpoint
    """

    def test_empty_node_list(self, client):
        # Arrange
        schema = {
            "$schema": SCHEMA_DRAFT,
            "type": "object",
            "properties": {
                'error': {
                    "type": "string",
                    "pattern": "Missing list of nodes",
                }
            },
            "additionalProperties": False,
            "required": [
                "error",
            ]
        }
        payload = {}
        # Act
        response = client.post('/nodes/register', json=payload)
        # Assert
        assert response.status_code == 400
        validate(instance=response.json, schema=schema)

    def test_mixed_invalid_node_list(self, client):
        # Arrange
        schema = {
            "$schema": SCHEMA_DRAFT,
            "type": "object",
            "properties": {
                "total_nodes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 0,
                    "uniqueItems": True,
                },
                'invalid_nodes': {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 0,
                    "uniqueItems": True,
                },
            },
            "additionalProperties": False,
            "required": [
                "total_nodes",
                "invalid_nodes"
            ]
        }
        payload = {
            "nodes": [
                "",
                "localhost:8082",
            ]
        }
        # Act
        response = client.post('/nodes/register', json=payload)
        # Assert
        assert response.status_code == 201
        validate(instance=response.json, schema=schema)

    def test_valid_node_list(self, client):
        # Arrange
        schema = {
            "$schema": SCHEMA_DRAFT,
            "type": "object",
            "properties": {
                "total_nodes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 0,
                    "uniqueItems": True,
                }
            },
            "additionalProperties": False,
            "required": [
                "total_nodes",
            ]
        }
        payload = {
            "nodes": [
                "http://localhost:8082",
                "localhost:8082",
            ]
        }
        # Act
        response = client.post('/nodes/register', json=payload)
        # Assert
        assert response.status_code == 201
        validate(instance=response.json, schema=schema)


class TestDoGossipFunction(object):
    """
    Test the do_gossip function
    """

    def test_empty_node_list(self):
        # Arrange
        known_nodes = []
        # Act
        retrieved_value = sut_app.do_gossip(known_nodes)
        # Assert
        assert retrieved_value == []

    def test_valid_node_list(self):
        # Arrange
        known_nodes = [
            "localhost:8081",
        ]
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "chain": "sample value"
            }
            # Act
            retrieved_value = sut_app.do_gossip(known_nodes)
            # Assert
            assert retrieved_value == ["sample value"]

    def test_invalid_response_list(self):
        # Arrange
        known_nodes = [
            "localhost:8081",
        ]
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 500
            # Act
            retrieved_value = sut_app.do_gossip(known_nodes)
            # Assert
            assert retrieved_value == []

    def test_exception_response_list(self):
        # Arrange
        known_nodes = [
            "localhost:8081",
        ]
        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = Exception()
            # Act
            retrieved_value = sut_app.do_gossip(known_nodes)
            # Assert
            assert retrieved_value == []


class TestConsensusEndpoint(object):
    """
    Test the consensus endpoint
    """

    def test_replaced_chain(self, client, schema_def_evaluate_consensus):
        # Arrange
        schema = schema_def_evaluate_consensus
        with client:
            sample_blockchain = g.blockchain.get_chain()
            mocked_blockchain = mock.Mock()
            mocked_blockchain.evaluate_consensus.return_value = True
            mocked_blockchain.get_chain.return_value = sample_blockchain
            g.blockchain = mocked_blockchain
            g.known_nodes = []
            with mock.patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = sample_blockchain
                # Act
                response = client.post('/nodes/consensus', json={})
                # Assert
                assert response.status_code == 200
                validate(instance=response.json, schema=schema)

    def test_not_replaced_chain(self, client, schema_def_evaluate_consensus):
        # Arrange
        schema = schema_def_evaluate_consensus
        with client:
            sample_blockchain = g.blockchain.get_chain()
            mocked_blockchain = mock.Mock()
            mocked_blockchain.evaluate_consensus.return_value = False
            mocked_blockchain.get_chain.return_value = sample_blockchain
            g.blockchain = mocked_blockchain
            g.known_nodes = []
            with mock.patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = sample_blockchain
                # Act
                response = client.post('/nodes/consensus', json={})
                # Assert
                assert response.status_code == 200
                validate(instance=response.json, schema=schema)
