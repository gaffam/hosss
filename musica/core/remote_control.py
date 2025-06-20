from threading import Thread
import logging

try:
    from flask import Flask
    from flask_socketio import SocketIO, emit
    SOCKET_AVAILABLE = True
except Exception:  # pragma: no cover
    SOCKET_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RemoteServer:
    """Flask-SocketIO based remote control."""

    def __init__(self, audio_chain):
        self.audio_chain = audio_chain
        if not SOCKET_AVAILABLE:
            self.app = None
            return
        self.app = Flask(__name__)
        self.sock = SocketIO(self.app, cors_allowed_origins="*")

        @self.sock.on('play')
        def _play(data):  # pragma: no cover - network IO
            deck = data.get('deck', 0)
            self.audio_chain.dj_decks[deck].play()

        @self.sock.on('pause')
        def _pause(data):
            deck = data.get('deck', 0)
            self.audio_chain.dj_decks[deck].pause()

    def start(self, host='0.0.0.0', port=5000):
        if not self.app:
            logging.warning('SocketIO not available')
            return
        def run():  # pragma: no cover - network
            self.sock.run(self.app, host=host, port=port)
        Thread(target=run, daemon=True).start()
