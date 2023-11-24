from flask import Blueprint, json, request
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
import hashlib
from json import dumps as json_dumps

__private_key = None
__elliptic_curve = ec.SECP384R1()
__ecdsa = ec.ECDSA(utils.Prehashed(hashes.SHA256()))

def get_public_key_obj(public_key):
    first, second = public_key.split('-')
    public_number_x = int(first[1:])
    public_number_y = int(second[1:])
    return ec.EllipticCurvePublicNumbers(
        x=public_number_x,
        y=public_number_y,
        curve=__elliptic_curve
    ).public_key()

def derive_pass_phrase_key_pair(pass_phrase):
    pass_phrase_hex = ''.join([format(ord(char), 'x') for char in pass_phrase])
    private_key = ec.derive_private_key(int(pass_phrase_hex, 16), __elliptic_curve)
    public_key = private_key.public_key()
    
    private_values = private_key.private_numbers()
    public_values = public_key.public_numbers()
    return {
        'private_key': f"{hex(private_values.private_value)}",
        'public_key': f"H{hex(public_values.x)}-C{hex(public_values.y)}",
        'private_key_obj': private_key,
        'public_key_obj': public_key,
    }

def sign_message(message, private_key=__private_key):
    if (private_key):
        message_hash = hashlib.sha256(json_dumps(message).encode()).digest()
        return private_key.sign(message_hash, __ecdsa)
    
def verify_signature(signature, message, public_key):
    public_key_obj = get_public_key_obj(public_key=public_key)
    message_hash = hashlib.sha256(json_dumps(message).encode()).digest()
    return public_key_obj.verify(
        signature,
        message_hash,
        __ecdsa
    )

class Address:
    private_key = None
    private_key_obj = None
    public_key = None
    public_key_obj = None
    elliptic_curve = ec.SECP384R1()
    ecdsa = ec.ECDSA(utils.Prehashed(hashes.SHA256()))

    def __init__(self, public_key='', private_key=''):
        self.public_key = public_key
        self.private_key = private_key

address_blueprint = Blueprint('address', __name__, url_prefix='/api/v1/address')

@address_blueprint.route('/', methods = ['POST'])
def generate_key_pair():
    json_data = request.get_json(force=True)
    
    if (not json_data) or (not json_data['pass_phrase']):
        return json.jsonify({
            'success': False,
            'key_pair': None,
            'message': 'Provide a pass phrase to generate your heimcoin address',
        }), 400
    
    address_keys = derive_pass_phrase_key_pair(json_data['pass_phrase'])

    return json.jsonify({
        'success': True,
        'key_pair': {
            'private_key': address_keys['private_key'],
            'public_key': address_keys['public_key'],
        },
    }), 200
