import hashlib

from datetime import datetime
from json import dumps as json_dumps
from heimcoin.network import get_node_address

class Block:
    __data = {
        'index': None,
        'timestamp': None,
        'proof': None,
        'previous_block_hash': None,
        'transactions': [],
        'miner_address': None,
        'node_address': None,
    }
    __data_hash = None

    def __init__(self, index, proof, previous_hash, transactions, miner_address, node_address=None, timestamp=None):
        self.__data = {
            'index': index,
            'timestamp': timestamp or str(datetime.now()),
            'proof': proof,
            'previous_block_hash': previous_hash,
            'transactions': transactions,
            'miner_address': miner_address,
            'node_address': node_address or get_node_address().wallet_address,
        }
        self.hash_block()

    def set_proof(self, proof):
        self.__data['proof'] = proof
        self.hash_block()

    def get_data(self, include_meta=False):
        data = {
            'index': self.__data['index'],
            'timestamp': self.__data['timestamp'],
            'proof': self.__data['proof'],
            'previous_block_hash': self.__data['previous_block_hash'],
            'transactions': list(map(lambda t: t.get_data(True), self.__data['transactions'])),
            'miner_address': self.__data['miner_address'],
            'node_address': self.__data['node_address'],
        }

        if not include_meta:
            return data
    
        data['block_hash'] = self.__data_hash
        return data
    
    def get_data_hash(self):
        return self.__data_hash
    
    def get_block_height(self):
        return self.__data['index']
    
    def hash_block(self):
        encoded_block = json_dumps(self.get_data(), sort_keys = True).encode()
        self.__data_hash = hashlib.sha256(encoded_block).hexdigest()

    def wallet_address_transactions(self, wallet_address):
        transaction_outputs = []

        transaction_list = list(map(
            lambda transaction: transaction.wallet_address_outputs(wallet_address),
            self.__data['transactions']
        ))
        for transaction in transaction_list:
            transaction_outputs.extend(transaction)

        return transaction_outputs
    
    def is_transaction_output(self, wallet_address, otrnx):
        for transaction in self.__data['transactions']:
            is_output, output_data, transaction_data = transaction.is_transaction_output(wallet_address, otrnx)
            if is_output:
                return True, output_data, transaction_data
            
        return False, None, None
    
    def is_transaction_input(self, wallet_address, otrnx):
        for transaction in self.__data['transactions']:
            is_input, input_data, transaction_data = transaction.is_transaction_input(wallet_address, otrnx)
            if is_input:
                return True, input_data, transaction_data
            
        return False, None, None
    
    

    
