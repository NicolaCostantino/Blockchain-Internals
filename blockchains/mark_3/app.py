import os
import requests

from flask import Flask, g, jsonify, request
from flask.views import View
from urllib.parse import urlparse
from uuid import uuid4

from .blockchain import Blockchain


# Instantiate the Node
app = Flask(__name__)
ctx = app.app_context()
ctx.push()

# Instantiate the Blockchain
g.blockchain = Blockchain()

# Generate a globally unique address for this node
g.node_identifier = str(uuid4()).replace('-', '')

# List of neighbours to this node
g.known_nodes = set()


# Blockchain-related actions

@app.route('/action/evil', methods=['POST'])
def evil_action_pop():
    blockchain = g.blockchain
    if len(blockchain._chain) > 1:
        # Don't remove a genesis block
        removed_element = blockchain._chain.pop()
        result = {
            'status': 'Snap done!',
            'element': removed_element,
        }
        status_code = 200
    else:
        result = {
            'status': 'Nothing to do...',
            'element': None,
        }
        status_code = 200
    response = jsonify(result)
    response.status_code = status_code
    return response


@app.route('/mine', methods=['POST'])
def mine():
    blockchain = g.blockchain
    result = {
        'new_block': blockchain.mine(),
        'is_valid': blockchain.is_valid(),
    }
    response = jsonify(result)
    status_code = 200 if not result['is_valid'] else 201

    response = jsonify(result)
    response.status_code = status_code
    return response


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    blockchain = g.blockchain
    input_values = request.get_json()

    required_args = ['data', ]
    if not input_values or not all(k in input_values for k in required_args):
        result = {
            'error': 'Missing values',
        }
        status_code = 400
    else:
        transaction = blockchain.add_transaction(input_values['data'])
        result = {
            'transaction': transaction,
        }
        status_code = 201

    response = jsonify(result)
    response.status_code = status_code
    return response


@app.route('/chain', methods=['GET'])
def chain():
    blockchain = g.blockchain
    result = {
        'chain': blockchain.get_chain(),
        'is_valid': blockchain.is_valid(),
    }

    response = jsonify(result)
    response.status_code = 200
    return response


# Node-related actions

def register_known_node(url_address):
    """
    Add a new node to the list of known nodes

    :param url_address: Address of node. Eg. 'http://127.0.0.1:5000'
    """
    # Parse the url
    parsed_url = urlparse(url_address)

    if parsed_url.netloc:
        # URL with scheme, e.g. 'http://127.0.0.1:5000'.
        extracted_url = parsed_url.netloc
        g.known_nodes.add(extracted_url)
    elif parsed_url.path:
        # URL without scheme, e.g. '127.0.0.1:5000'.
        extracted_url = parsed_url.path
        g.known_nodes.add(extracted_url)
    else:
        raise ValueError('Invalid URL')


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    input_values = request.get_json()

    nodes = input_values.get('nodes', None)
    if not nodes:
        result = {
            'error': 'Missing list of nodes',
        }
        status_code = 400
    else:
        invalid_nodes = []
        for node in nodes:
            try:
                register_known_node(node)
            except ValueError:
                print(f'Error adding {node}')
                invalid_nodes.append(node)
        result = {
            'total_nodes': list(g.known_nodes),
        }
        if len(invalid_nodes):
            result['invalid_nodes'] = invalid_nodes
        status_code = 201

    response = jsonify(result)
    response.status_code = status_code
    return response


def do_gossip(known_nodes):
    """
    The gossip algorithm - pull.
    All the known nodes are checked for collecting the available chains.

    :return: True if our chain was replaced, False if not
    """
    collected_chains = []
    # Pull: Collect the blockchains from the neighbours
    for node in known_nodes:
        try:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                chain = response.json()['chain']
                collected_chains.append(chain)
        except Exception as e:
            print(f'Exception on node {node}: {e}')
    return collected_chains


@app.route('/nodes/consensus', methods=['POST'])
def evaluate_consensus():
    """
    The consensus algorithm.
    The internal chain is replaced with the received one if longerk.

    :return: True if our chain was replaced, False if not
    """
    blockchain = g.blockchain
    collected_chains = do_gossip(g.known_nodes)
    replaced = blockchain.evaluate_consensus(collected_chains)

    if replaced:
        result = {
            'status': 'Chain replaced',
            'chain': blockchain.get_chain(),
        }
    else:
        result = {
            'status': 'Chain not replaced - master',
            'chain': blockchain.get_chain(),
        }
    status_code = 200

    response = jsonify(result)
    response.status_code = status_code
    return response
