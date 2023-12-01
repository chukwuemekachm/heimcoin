from heimcoin.address import Address, get_public_key_obj, verify_signature
from json import dumps as json_dumps
from datetime import datetime
from uuid import uuid4

import hashlib

__transaction_list = []

class Output:
    __data = {
        'trnx': None,
        'receiver_address': None,
        'receiver_amount': 0,
    }

    def __init__(self, receiver_address, receiver_amount):
        self.__data['receiver_address'] = receiver_address
        self.__data['receiver_amount'] = receiver_amount
        self.__data['trnx'] = uuid4().hex

    def get_data(self):
        return self.__data

class Transaction:
    __data = {
        'trnx': None,
        'sender_public_key': None,
        'output_list': [],
        'input_list': [],
        'time_stamp': None,
        'signature': None,
    }
    __data_hash = None
    __public_key_obj = None

    def get_data(self, include_meta=False):
        if (include_meta):
            return {
                'trnx': self.__data['trnx'],
                'sender_public_key': self.__data['sender_public_key'],
                'output_list': self.__data['output_list'],
                'input_list': self.__data['input_list'],
                'time_stamp': self.__data['time_stamp'],
            }
        
        return {
            'trnx': self.__data['trnx'],
            'sender_public_key': self.__data['sender_public_key'],
            'output_list': self.__data['output_list'],
            'input_list': self.__data['input_list'],
            'time_stamp': self.__data['time_stamp'],
            'signature': self.__data['signature'],
            'hash': self.__data_hash,
         }

    def hash_transaction(self):
        self.__data_hash = hashlib.sha256(json_dumps(self.get_data()).encode()).hexdigest()
        return self.__data_hash

    def __init__(self, sender_public_key, output_list, input_list, signature=''):
        self.__data = {
            'sender_public_key': sender_public_key,
            'output_list': output_list,
            'input_list': input_list,
            'trnx': uuid4().hex,
            'time_stamp': str(datetime.now()),
            'signature': signature
        }
        self.__public_key_obj = get_public_key_obj(sender_public_key)
        

    def is_signature_valid(self):
        if (not self.__data['signature']) or (not self.__public_key_obj):
            return False
       
        return verify_signature(
            self.__data['sender_public_key'],
            self.get_data(),
            self.__data['signature']
        )
    
    def set_signature(self, signature):
        self.__data['signature'] = signature


def get_transaction_list():
    return __transaction_list

def clear_transaction_list():
    return __transaction_list.clear()

def add_transaction(transaction):
    __transaction_list.append(transaction)
    return __transaction_list
