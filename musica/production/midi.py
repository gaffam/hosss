import logging

try:
    import mido
    from mido import Message
    import mido.backends.rtmidi
    MIDI_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    MIDI_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MidiRouter:
    """Simple MIDI router that forwards messages to callbacks."""

    def __init__(self):
        self.callbacks = []
        if MIDI_AVAILABLE:
            try:
                self.input = mido.open_input(callback=self._handle)
                logging.info("MIDI input opened: %s", self.input.name)
            except Exception as e:  # pragma: no cover
                logging.error("MIDI açma hatası: %s", e)
                self.input = None
        else:
            self.input = None

    def _handle(self, msg):
        for cb in self.callbacks:
            cb(msg)

    def register(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def close(self):
        if self.input:
            self.input.close()


def update_velocity(notes, index, velocity):
    """Update velocity of a note in a MIDI note list."""
    if 0 <= index < len(notes):
        notes[index]["velocity"] = max(0, min(127, velocity))
