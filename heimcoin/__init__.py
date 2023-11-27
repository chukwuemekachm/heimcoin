import os

from flask import Flask
from socketio import Server, WSGIApp
from heimcoin import address, network, node

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

    app.register_blueprint(address.address_blueprint)
    app.register_blueprint(network.network_blueprint)
    app.wsgi_app = WSGIApp(node.socket_io, app.wsgi_app)

    return app
