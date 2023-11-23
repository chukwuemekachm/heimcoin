from flask import Blueprint, json, request
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
import hashlib
from json import dumps as json_dumps

class Address:
    private_key = ''
    public_key = ''
    elliptic_curve = ec.SECP384R1()
    ecdsa = ec.ECDSA(utils.Prehashed(hashes.SHA256()))

    def __init__(self, public_key='', private_key=''):
        self.public_key = public_key
        self.private_key = private_key

    def set_public_key(self, public_key):
        first, second = public_key.split('-')
        public_number_x = int(first[1:])
        public_number_y = int(second[1:])
        self.public_key = ec.EllipticCurvePublicNumbers(
            x=public_number_x,
            y=public_number_y,
            curve=self.elliptic_curve
        ).public_key()

    def generate_key_pair(self, pass_phrase):
        pass_phrase_hex = ''.join([format(ord(char), 'x') for char in pass_phrase])
        private_key = ec.derive_private_key(int(pass_phrase_hex, 16), self.elliptic_curve)
        public_key = private_key.public_key()

        self.private_key = private_key
        self.public_key = public_key
        
        private_values = private_key.private_numbers()
        public_values = public_key.public_numbers()
        return {
            'private_key': f"{hex(private_values.private_value)}",
            'public_key': f"H{hex(public_values.x)}-C{hex(public_values.y)}"
        }

    def sign_message(self, message):
        if (self.private_key):
            message_hash = hashlib.sha256(json_dumps(message).encode()).digest()
            return self.private_key.sign(message_hash, self.ecdsa)
        
    def verify_signature(self, public_key, signature, message):
        self.set_public_key(public_key=public_key)
        message_hash = hashlib.sha256(json_dumps(message).encode()).digest()
        return self.public_key.verify(
            signature,
            message_hash,
            self.ecdsa
        )

address_module = Blueprint('address', __name__, url_prefix='/api/v1/address')

@address_module.route('/', methods = ['POST'])
def generate_key_pair():
    json_data = request.get_json(force=True)
    
    if (not json_data) or (not json_data['pass_phrase']):
        return json.jsonify({
            'success': False,
            'key_pair': None,
            'message': 'Provide a pass phrase to generate your heimcoin address',
        }), 400
    
    address = Address()
    address_keys = address.generate_key_pair(json_data['pass_phrase'])

    return json.jsonify({
        'success': True,
        'key_pair': {
            'private_key': address_keys['private_key'],
            'public_key': address_keys['public_key'],
        },
    }), 200
