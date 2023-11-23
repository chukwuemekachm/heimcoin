from flask import current_app, Blueprint, json
from heimcoin.address import Address

node_address = Address()
node_module = Blueprint('node', __name__, url_prefix='/api/v1/node')

@node_module.route('/', methods = ['GET'])
def generate_key_pair():
    node_pass_phrase = current_app.config['HEIM_COIN_PRIVATE_KEY_PASS_PHRASE']
    node_key_pair = node_address.generate_key_pair(node_pass_phrase)

    return json.jsonify({
        'success': True,
        'node_address': node_key_pair['public_key']
    }), 200
