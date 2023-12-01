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

    def __init__(self, index, proof, previous_hash, transactions, miner_address):
        self.__data = {
            'index': index,
            'timestamp': str(datetime.now()),
            'proof': proof,
            'previous_block_hash': previous_hash,
            'transactions': transactions,
            'miner_address': miner_address,
            'node_address': get_node_address().wallet_address,
        }
        self.hash_block()

    def set_proof(self, proof):
        self.__data['proof'] = proof
        self.hash_block()

    def get_data(self, include_meta=False):
        if not include_meta:
            return self.__data

        data = {
            'index': self.__data['index'],
            'timestamp': self.__data['timestamp'],
            'proof': self.__data['proof'],
            'previous_block_hash': self.__data['previous_block_hash'],
            'transactions': self.__data['transactions'],
            'miner_address': self.__data['miner_address'],
            'node_address': self.__data['node_address'],
        }
        data['block_hash'] = self.__data_hash
        return data
    
    def get_data_hash(self):
        return self.__data_hash
    
    def get_block_height(self):
        return self.__data['index']
    
    def hash_block(self):
        encoded_block = json_dumps(self.__data, sort_keys = True).encode()
        self.__data_hash = hashlib.sha256(encoded_block).hexdigest()
    
