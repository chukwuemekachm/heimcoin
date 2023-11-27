from dotenv import load_dotenv

load_dotenv()

from heimcoin import create_app
from heimcoin.node import handle_socket_request

if __name__ == '__main__':
    app, socket_io = create_app()

    print('app config: ---- ', app.config)

    @socket_io.on('PEER_PING')
    def handle_peer_ping(data):
        print('received message: ---- ' + data)
        result = handle_socket_request(data)
        socket_io.emit(
            'PEER_RESPONSE',
            { 'status': True, 'message': 'Thank you', 'data': result }
        )

    
    socket_io

    
    # socket_io.run(
    #     app=app,
    #     host=app.config['FLASK_RUN_HOST'],
    #     port=app.config['FLASK_RUN_PORT'],
    #     debug=app.config['FLASK_DEBUG'],
    #     use_reloader=app.config['FLASK_RELOAD']
    # )
