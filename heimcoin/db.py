from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import current_app
from json import dumps as json_dumps, loads as json_loads

def get_db():
    return MongoClient(
        ,
        server_api=ServerApi('1')
    )[current_app.config['HEIM_COIN_NET']]

def write_item(key, item):
    db = get_db()
    try:
        db[key] = json_dumps(item)
    except Exception as e:
        print(e, 'FAILING TO WRITE FROM FILE')
    finally:
        db.close()

def read_item(key):
    item = None
    db = get_db()
    try:
        item = db.get(key)
    except Exception as e:
        print(e, 'FAILING TO READ FROM FILE')
    finally:
        db.close()
    return json_loads(item) if item else False
