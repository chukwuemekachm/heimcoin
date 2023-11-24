from heimcoin.address import Address
from json import dumps as json_dumps

import hashlib

transaction_address = Address()

class Output:
  receiver_public_key = None
  receiver_amount = 0
  trnx = None

class Transaction:
    trnx = None
    sender_public_key = None
    output_list = []
    input_list = []
    signature = None
    transaction_hash = None

    def hash_transaction_data(self, transaction_data):
       return hashlib.sha256(json_dumps(transaction_data).encode()).digest()

    def __init__(self, sender_public_key, output_list, input_list, trnx):
        self.trnx = trnx
        self.sender_public_key = sender_public_key
        self.output_list = output_list
        self.input_list = input_list
        self.transaction_hash = self.hash_transaction_data({
             'sender_public_key': self.sender_public_key,
             'output_list': self.output_list,
             'input_list': self.input_list,
             'trnx': self.trnx,
        })

    def is_signature_valid(self):
       if (not self.signature) or (not self.sender_public_key):
          return False
       
       return transaction_address.verify_signature(
          self.sender_public_key,
          self.signature,
          self.transaction_hash
        )
