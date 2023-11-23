import os

from flask import Flask
from heimcoin import address, node

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'heimcoin.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('../heimcoin/config.py')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(address.address_module)
    app.register_blueprint(node.node_module)

    return app
