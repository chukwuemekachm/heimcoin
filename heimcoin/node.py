from socketio import SimpleClient, Server
from enum import Enum

class MessageEvent(Enum):
    # nodes
    PING_PEER = 'PING_PEER'
    FETCH_NODES = 'FETCH_NODES'
    SHARE_NODE = 'SHARE_NODE'
    SHARE_NODES = 'SHARE_NODES'
    REPORT_NODE = 'REPORT_NODE'
    # chain
    FETCH_CHAIN = 'FETCH_CHAIN'
    REPLACE_CHAIN = 'REPLACE_CHAIN'
    # transaction
    FETCH_TRANSACTION = 'FETCH_TRANSACTION'
    SHARE_TRANSACTION = 'SHARE_TRANSACTION'
    FETCH_TRANSACTIONS = 'FETCH_TRANSACTIONS'
    SHARE_TRANSACTIONS = 'SHARE_TRANSACTIONS'
    

socket_io = Server(async_mode='threading')

@socket_io.on(MessageEvent.PING_PEER.value)
def handle_peer_ping():
    socket_io.emit(
        MessageEvent.PING_RESPONSE.value,
        { 'status': True }
    )

def message_peer(peer_address, message, message_event, response_event_handler=None):
    client = SimpleClient()

    try:
        client.connect(f'http://{peer_address}', transports=['websocket'])
    except Exception as e:
        return None

    try:
        client.emit(message_event, { 'message': message })
        if (response_event_handler):
            response = client.receive()
            response_event_handler(response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print(f"Connection to peer {peer_address} closed")
