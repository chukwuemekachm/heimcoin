from flask import Blueprint, json, request
from ecdsa import NIST256p, SigningKey, VerifyingKey
from ecdsa.util import randrange_from_seed__trytryagain

import hashlib
from json import dumps as json_dumps

__elliptic_curve = NIST256p

def get_public_key_obj(public_key):
    return VerifyingKey.from_string(bytearray.fromhex(public_key), curve=__elliptic_curve)

def derive_pass_phrase_key_pair(pass_phrase):
    pass_phrase_hex = ''.join([format(ord(char), 'x') for char in pass_phrase])
    secexp = randrange_from_seed__trytryagain(int(pass_phrase_hex, 16), __elliptic_curve.order)
    private_key = SigningKey.from_secret_exponent(secexp, curve=__elliptic_curve)
    public_key = private_key.verifying_key

    address_hash = hashlib.blake2b(digest_size=16)
    address_hash.update(str(public_key.to_string('compressed').hex()).encode())

    return {
        'private_key': private_key.to_string().hex(),
        'public_key': public_key.to_string('compressed').hex(),
        'address': f"H{address_hash.hexdigest()}",
        'private_key_obj': private_key,
        'public_key_obj': public_key,
    }

def verify_signature(signature, message, public_key):
    message_hash = hashlib.sha256(json_dumps(message).encode()).hexdigest().encode()
    public_key_obj = get_public_key_obj(public_key)
    return public_key_obj.verify(
        signature.encode('IBM852'),
        message_hash,
    )

def sign_message(message, private_key):
    message_hash = hashlib.sha256(json_dumps(message).encode()).hexdigest().encode()
    return private_key.sign_deterministic(message_hash).decode('IBM852')

class Address:
    private_key = None
    private_key_obj = None
    public_key = None
    public_key_obj = None
    wallet_address = None

    def __init__(self, public_key, private_key, private_key_obj, public_key_obj, address):
        self.public_key = public_key
        self.private_key = private_key
        self.public_key_obj = public_key_obj
        self.private_key_obj = private_key_obj
        self.wallet_address = address

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
            'address': address_keys['address'],
        },
    }), 201
