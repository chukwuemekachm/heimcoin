import random
import hashlib

from flask import current_app, Blueprint, json, request, app
from datetime import datetime
from json import dumps as json_dumps
from heimcoin.transaction import get_transaction_list, clear_transaction_list, Transaction, Output
from heimcoin.address import derive_pass_phrase_key_pair, sign_message
from heimcoin.block import Block

class Blockchain:
    __chain = []
    __node_address = None
    __index_block_reward_address = 'H10000000000000000000000000000000'

    def mine_genesis_block(self):
        self.__chain.append(
            Block(
                1,
                0,
                None,
                [self.create_block_reward(self.__index_block_reward_address).get_data(True)],
                self.__index_block_reward_address
            )
        )

    def create_block_reward(self, miner_address):
        if self.__node_address is None:
            self.__node_address = derive_pass_phrase_key_pair(
                current_app.config['HEIM_COIN_PRIVATE_KEY_PASS_PHRASE']
            )

        block_reward = Transaction(
            self.__node_address['public_key'],
            [Output(miner_address, self.get_block_reward_amount()).get_data()],
            [],
        )
        block_reward.set_signature(
            sign_message(block_reward.get_data(), self.__node_address['private_key_obj'])
        )
        return block_reward

    def get_block_reward_amount(self):
        return 10
    
    def get_previous_block(self):
        return self.__chain[-1]
    
    def get_chain(self):
        return self.__chain
    
    def hash_block(self, block):
        encoded_block = json_dumps(block.get_, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def create_block(self, proof, previous_hash, transactions, miner_address):        
        return Block(
            len(self.__chain) + 1,
            proof,
            previous_hash,
            list(map(lambda t: t.get_data(True), transactions)),
            miner_address,
        )
    
    def find_block_proof(self, block):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            block.set_proof(new_proof)
            hash_operation = block.get_data_hash()
            if hash_operation.startswith('0000'):
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def mine_block(self, miner_address):
        block_transactions = [self.create_block_reward(miner_address)]
        block_transactions.extend(get_transaction_list())
        previous_block = self.get_previous_block()
        previous_hash = previous_block.get_data_hash()
        block = self.create_block(1, previous_hash, block_transactions, miner_address)
        proof = self.find_block_proof(block)
        block.set_proof(proof)

        self.__chain.append(block)
        clear_transaction_list()

        return block

blockchain = Blockchain()
blockchain_blueprint = Blueprint('blockchain', __name__, url_prefix='/api/v1/blockchain')

@blockchain_blueprint.route('/', methods = ['GET'])
def get_chain():
    chain = blockchain.get_chain()

    return json.jsonify({
        'success': True,
        'chain': list(map(lambda b: b.get_data(True), chain)),
        'length': len(chain),
    }), 200

@blockchain_blueprint.route('/', methods = ['POST'])
def mine_block():
    json_data = request.get_json(force=True)
    
    if (not json_data) or (not json_data['miner_address']):
        return json.jsonify({
            'success': False,
            'key_pair': None,
            'message': 'Provide a wallet address for the miner',
        }), 400
    
    blockchain.mine_block(json_data['miner_address'])
    chain = blockchain.get_chain()

    return json.jsonify({
        'success': True,
        'chain': list(map(lambda b: b.get_data(True), chain)),
        'length': len(chain),
    }), 201
