import hashlib

from heimcoin.address import get_public_key_obj, verify_signature
from json import dumps as json_dumps
from datetime import datetime
from uuid import uuid4

def load_transactions_from_file(file_data):
    transactions = []
    for transaction in file_data:
        transactions.append(Transaction(
            transaction['sender_public_key'],
            transaction['output_list'],
            transaction['input_list'],
            transaction['signature'],
            transaction['timestamp'],
            transaction['trnx'],
        ))
    return transactions

__transaction_list = []

def get_transaction_list():
    return __transaction_list

def clear_transaction_list():
    return __transaction_list.clear()

def add_transaction(transaction):
    __transaction_list.append(transaction)
    return __transaction_list

def create_output(receiver_address, receiver_amount):
    return {
        'receiver_address': receiver_address,
        'receiver_amount': receiver_amount,
        'otrnx': uuid4().hex,
    }

def create_input(receiver_address, receiver_amount, otrnx):
    return {
        'receiver_address': receiver_address,
        'receiver_amount': receiver_amount,
        'otrnx': otrnx,
        'intrnx': uuid4().hex,
    }

class Transaction:
    __data = {
        'trnx': None,
        'sender_public_key': None,
        'output_list': [],
        'input_list': [],
        'timestamp': None,
        'signature': None,
    }
    __data_hash = None
    __public_key_obj = None

    def get_data(self, include_meta=False):
        if not include_meta:
            return {
                'trnx': self.__data['trnx'],
                'sender_public_key': self.__data['sender_public_key'],
                'output_list': self.__data['output_list'],
                'input_list': self.__data['input_list'],
                'timestamp': self.__data['timestamp'],
            }
        
        return {
            'trnx': self.__data['trnx'],
            'sender_public_key': self.__data['sender_public_key'],
            'output_list': self.__data['output_list'],
            'input_list': self.__data['input_list'],
            'timestamp': self.__data['timestamp'],
            'signature': self.__data['signature'],
         }

    def hash_transaction(self):
        self.__data_hash = hashlib.sha256(json_dumps(self.get_data()).encode()).hexdigest()
        return self.__data_hash

    def __init__(self, sender_public_key, output_list, input_list, signature=None, time_stamp=None, trnx=None):
        self.__data = {
            'sender_public_key': sender_public_key,
            'output_list': output_list,
            'input_list': input_list,
            'trnx': trnx or uuid4().hex,
            'timestamp': time_stamp or str(datetime.now()),
            'signature': signature
        }
        self.__public_key_obj = get_public_key_obj(sender_public_key)
        

    def is_signature_valid(self):
        if (not self.__data['signature']) or (not self.__public_key_obj):
            return False
       
        return verify_signature(
            self.__data['signature'],
            self.get_data(),
            self.__data['sender_public_key'],
        )
    
    def set_signature(self, signature):
        self.__data['signature'] = signature

    def wallet_address_outputs(self, wallet_address):
        output_list = []

        wallet_output_list = list(filter(
            lambda o: o['receiver_address'] == wallet_address,
            self.__data['output_list']
        ))
        output_list.extend(wallet_output_list)

        return output_list
    
    def is_transaction_output(self, wallet_address, otrnx):
        for output in self.__data['output_list']:
            if output['receiver_address'] == wallet_address and output['otrnx'] == otrnx:
                return True, output, self.get_data(True)
            
        return False, None, None
    
    def is_transaction_input(self, wallet_address, otrnx):
        for input in self.__data['input_list']:
            if input['receiver_address'] == wallet_address and input['otrnx'] == otrnx:
                return True, input, self.get_data(True)
            
        return False, None, None
            
