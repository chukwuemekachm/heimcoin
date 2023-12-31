import os

from flask import Flask, jsonify
from flask_helmet import FlaskHelmet
from socketio import WSGIApp
from mongoengine import connect

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if test_config is None:
        app.config.from_pyfile('../heimcoin/config.py')
    else:
        app.config.from_mapping(test_config)

    helmet = FlaskHelmet()
    helmet.init_app(app)
    connect(
        db=app.config['HEIM_COIN_DB_NAME'],
        username=app.config['HEIM_COIN_DB_USERNAME'],
        password=app.config['HEIM_COIN_DB_PASSWORD'],
        host=app.config['HEIM_COIN_DB_HOST'],
    )

    with app.app_context():
        from heimcoin import address, network, node, blockchain

        app.register_blueprint(address.address_blueprint)
        app.register_blueprint(network.network_blueprint)
        app.register_blueprint(blockchain.blockchain_blueprint)
        app.wsgi_app = WSGIApp(node.socket_io, app.wsgi_app)
        blockchain.blockchain.mine_genesis_block()

    @app.errorhandler(400)
    def invalid_api_usage(error):
        return jsonify({
            'success': False,
            'message': 'Invalid Request',
            'error': error.description or 'Provide a valid JSON payload',
        }), 400
    
    @app.errorhandler(404)
    def resource_not_found(_):
        return jsonify({
            'success': False,
            'error': 'Resource Not Found',
        }), 404

    return app
