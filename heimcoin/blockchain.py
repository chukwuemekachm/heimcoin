import hashlib

from flask import current_app, Blueprint, json, request
from json import dumps as json_dumps
from heimcoin.transaction import get_transaction_list, clear_transaction_list, Transaction, create_output
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
                [self.create_block_reward(self.__index_block_reward_address)],
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
            [create_output(miner_address, self.get_block_reward_amount())],
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
            transactions,
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
    
    def wallet_transactions(self, wallet_address):
        chain = self.__chain
        wallet_address_outputs = []

        block_transaction_list = list(map(lambda b: b.wallet_address_transactions(wallet_address), chain))
        for block_transaction in block_transaction_list:
            wallet_address_outputs.extend(block_transaction)

        return wallet_address_outputs

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
            'chain': None,
            'message': 'Provide a wallet address for the miner',
        }), 400
    
    blockchain.mine_block(json_data['miner_address'])
    chain = blockchain.get_chain()

    return json.jsonify({
        'success': True,
        'chain': list(map(lambda b: b.get_data(True), chain)),
        'length': len(chain),
    }), 201

@blockchain_blueprint.route('/wallet-transactions', methods = ['POST'])
def wallet_transactions():
    json_data = request.get_json(force=True)
    
    if (not json_data) or (not json_data['wallet_address']):
        return json.jsonify({
            'success': False,
            'transactions': None,
            'message': 'Provide a wallet address',
        }), 400
    
    transactions = blockchain.wallet_transactions(json_data['wallet_address'])

    return json.jsonify({
        'success': True,
        'transactions': transactions,
        'length': len(transactions),
    }), 201
