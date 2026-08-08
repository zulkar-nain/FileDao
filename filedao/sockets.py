from datetime import datetime

from . import socketio


@socketio.on('connect')
def handle_connect():
    pass


def broadcast_file_update():
    socketio.emit('file_list_updated', {'updated_at': datetime.utcnow().isoformat()})
