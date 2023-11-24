from flask import current_app, Blueprint, json, request
from urllib.parse import urlparse
from heimcoin.address import Address, derive_pass_phrase_key_pair

__node_address = Address()
__network_nodes = set()
network_blueprint = Blueprint('network', __name__, url_prefix='/api/v1/network')

def add_network_node(address):
    parsed_url = urlparse(address)
    node = parsed_url.netloc
    __network_nodes.add(node)
    return node

def get_network_nodes():
    return __network_nodes

def remove_network_node(node):
    __network_nodes.remove(node)

def get_node_address():
    return __node_address

@network_blueprint.route('/node-address', methods = ['GET'])
def get_node_address():
    node_pass_phrase = current_app.config['HEIM_COIN_PRIVATE_KEY_PASS_PHRASE']
    node_key_pair = derive_pass_phrase_key_pair(node_pass_phrase)

    return json.jsonify({
        'success': True,
        'node_address': node_key_pair['public_key']
    }), 200

@network_blueprint.route('/', methods = ['POST'])
def add_nodes():
    json_data = request.get_json()
    node_list = []
    for address in json_data['nodes']:
        node_address = add_network_node(address)
        node_list.append(node_address)

    return json.jsonify({
        'success': True,
        'nodes': node_list,
    }), 201

@network_blueprint.route('/', methods = ['GET'])
def get_nodes():
    nodes = get_network_nodes()
    return json.jsonify({
        'success': True,
        'nodes': list(nodes),
    }), 200
