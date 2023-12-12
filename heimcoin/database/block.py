from mongoengine import *
from json import dumps as json_dumps
import datetime

class Block(Document):
    block_data = StringField(required=True)
    block_data_index = IntField(required=True)
    next_block_id = StringField()
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)


def save_new_block_to_db(block_data, previous_block_id=None):
    block = Block(block_data=json_dumps(block_data), block_data_index=block_data['index'])
    block.save()

    if previous_block_id:
        previous_block, _ = Block.objects(id=previous_block_id)
        previous_block.next_block_id = block.id
        previous_block.date_modified = datetime.datetime.utcnow
        previous_block.save()

def get_chain_from_db():
    return sorted(Block.objects, key=lambda b: b.block_data_index)


