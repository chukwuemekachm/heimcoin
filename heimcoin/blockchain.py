import hashlib

from flask import current_app, Blueprint, json, request
from json import dumps as json_dumps
from functools import reduce

import heimcoin.validation_schemas as validation_schemas
from heimcoin.transaction import get_transaction_list, clear_transaction_list, Transaction, create_output, add_transaction, create_input
from heimcoin.address import derive_pass_phrase_key_pair, sign_message, get_key_pair_from_sk
from heimcoin.block import Block
from heimcoin.decorators import validate_request
from heimcoin.db import read_item, write_item

def load_chain_from_file(file_data):
    chain = []

    for data in file_data:
        transactions = []
        for transaction in data['transactions']:
            transactions.append(Transaction(
                transaction['sender_public_key'],
                transaction['output_list'],
                transaction['input_list'],
                transaction['signature'],
                transaction['timestamp'],
                transaction['trnx'],
            ))
        chain.append(Block(
            data['index'],
            data['proof'],
            data['previous_block_hash'],
            transactions,
            data['miner_address'],
            data['node_address'],
            data['timestamp'],
        ))
    return chain


class Blockchain:
    __chain = load_chain_from_file(read_item('HEIMCOIN_CHAIN') or [])
    __node_address = None
    __index_block_reward_address = 'H10000000000000000000000000000000'

    def mine_genesis_block(self):
        if not len(self.__chain):
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
        write_item('HEIMCOIN_CHAIN', list(map(lambda b: b.get_data(True), self.__chain)))
        clear_transaction_list()

        return block
    
    def wallet_transactions(self, wallet_address):
        chain = self.__chain
        wallet_address_outputs = []

        block_transaction_list = list(map(lambda b: b.wallet_address_transactions(wallet_address), chain))
        for block_transaction in block_transaction_list:
            wallet_address_outputs.extend(block_transaction)

        return wallet_address_outputs
    
    def verify_transaction_input(self, transaction_input, wallet_address):
        transaction = False, None, None
        for block in self.__chain:
            is_output, output_data, transaction_data = block.is_transaction_output(
                wallet_address, transaction_input['otrnx'],
            )
            print(is_output, output_data, transaction_data, 'is_output, output_data, transaction_data ---------')
            if is_output:
                transaction = is_output, output_data, transaction_data
                break

        return transaction
    
    def verify_transaction_inputs(self, input_list, wallet_address):
        are_outputs_valid = True

        for transaction_input in input_list:
            is_output = self.verify_transaction_input(transaction_input, wallet_address)
            
            if not is_output[0]:
                are_outputs_valid = False
                break

        return are_outputs_valid
    
    def is_output_spent(self, transaction_output, wallet_address):
        transaction = False, None, None
        for block in self.__chain:
            is_output, output_data, transaction_data = block.is_transaction_input(
                wallet_address, transaction_output['otrnx'],
            )
            if is_output:
                transaction = is_output, output_data, transaction_data
                break

        return transaction
    
    def are_outputs_spent(self, output_list, wallet_address):
        have_outputs_been_spent = False

        for transaction_input in output_list:
            was_input = self.is_output_spent(transaction_input, wallet_address)
            if was_input[0]:
                have_outputs_been_spent = True
                break

        return have_outputs_been_spent
    
    def submit_transaction(self, input_list, output_list, private_key):
        input_sum = reduce(lambda curr, acc: curr['receiver_amount'] + acc, input_list)
        output_sum = reduce(lambda curr, acc: curr['receiver_amount'] + acc, input_list)
        if output_sum > input_sum:
            return False, None

        address = get_key_pair_from_sk(private_key)
        wallet_address = address['address']
        public_key = address['public_key']
        private_key_obj = address['private_key_obj']
        are_inputs_valid = self.verify_transaction_inputs(input_list, wallet_address)
        if not are_inputs_valid:
            return False, None
        
        are_inputs_spent = self.are_outputs_spent(input_list, wallet_address)
        if are_inputs_spent:
            return False, None
        
        transaction = Transaction(
            public_key,
            list(map(lambda o: create_output(o['receiver_address'], o['receiver_amount']), output_list)),
            list(map(lambda i: create_input(i['receiver_address'], i['receiver_amount'], i['otrnx']), input_list)),
        )
        transaction.set_signature(
            sign_message(transaction.get_data(), private_key_obj)
        )
        add_transaction(transaction)
        return True, transaction

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
@validate_request(validation_schemas.mine_block_validation_schema)
def mine_block():
    json_data = request.get_json(force=True)
    blockchain.mine_block(json_data['miner_address'])
    chain = blockchain.get_chain()

    return json.jsonify({
        'success': True,
        'chain': list(map(lambda b: b.get_data(True), chain)),
        'length': len(chain),
    }), 201

@blockchain_blueprint.route('/wallet-transactions', methods = ['POST'])
@validate_request(validation_schemas.wallet_transactions_validation_schema)
def wallet_transactions():
    json_data = request.get_json(force=True)
    transactions = blockchain.wallet_transactions(json_data['wallet_address'])

    return json.jsonify({
        'success': True,
        'transactions': transactions,
        'length': len(transactions),
    }), 201


@blockchain_blueprint.route('/transaction', methods = ['POST'])
@validate_request(validation_schemas.submit_transaction_validation_schema)
def submit_transaction():
    json_data = request.get_json(force=True)
    input_list = json_data['input_list']
    output_list = json_data['output_list']
    private_key = json_data['private_key']

    submitted_ok, transaction = blockchain.submit_transaction(
        input_list, output_list, private_key
    )

    if not submitted_ok:
        return json.jsonify({
            'success': False,
            'transaction': None,
            'error': 'Invalid or spent transaction inputs'
        }), 422


    return json.jsonify({
        'success': True,
        'transaction': transaction.get_data(),
    }), 201

@blockchain_blueprint.route('/transaction-pool', methods = ['GET'])
def get_transaction_pool():
    transactions = get_transaction_list()

    return json.jsonify({
        'success': True,
        'transaction': list(map(lambda t: t.get_data(True), transactions)),
        'length': len(transactions),
    }), 201
