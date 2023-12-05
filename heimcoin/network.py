from flask import current_app, Blueprint, json, request
from urllib.parse import urlparse
from heimcoin.address import Address, derive_pass_phrase_key_pair
from heimcoin.node import message_peer, MessageEvent
from heimcoin.decorators import validate_request
import heimcoin.validation_schemas as validation_schemas

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
    node_pass_phrase = current_app.config['HEIM_COIN_PRIVATE_KEY_PASS_PHRASE']
    node_key_pair = derive_pass_phrase_key_pair(node_pass_phrase)
    __node_address = __node_address = Address(
        node_key_pair['public_key'],
        node_key_pair['private_key'],
        node_key_pair['private_key_obj'],
        node_key_pair['public_key_obj'],
        node_key_pair['address'],
    )
    return __node_address

@network_blueprint.route('/node-address', methods = ['GET'])
def get_network_node_address():
    __node_address = get_node_address()

    return json.jsonify({
        'success': True,
        'node_address': __node_address.wallet_address
    }), 200

@network_blueprint.route('/', methods = ['POST'])
@validate_request(validation_schemas.add_node_validation_schema)
def add_nodes():
    json_data = request.get_json()

    for address in json_data['nodes']:
        add_network_node(address)

    return json.jsonify({
        'success': True,
        'nodes': list(__network_nodes),
    }), 201



@network_blueprint.route('/', methods = ['GET'])
def get_nodes():
    nodes = get_network_nodes()
    return json.jsonify({
        'success': True,
        'nodes': list(nodes),
    }), 200


@network_blueprint.route('/ping', methods = ['POST'])
def ping_nodes():
    nodes = list(get_network_nodes())

    for node in nodes:
        message_peer(
            node,
            { 'data': f'Hello {node}' },
            MessageEvent.PING_PEER.value,
        )

    return json.jsonify({
        'success': True,
        'nodes': nodes,
    }), 200
