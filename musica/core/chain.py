import logging
import numpy as np
import sounddevice as sd
from concurrent import futures

from .device import AudioDeviceManager
from ..dj.deck import DJDeck
from ..dj.mixer import DJMixer
from ..effects_pkg import EffectRack
from .ai_remixer import AIRemixer
from .player import MediaPlayer
from ..production.track import ProductionTrack
from .stem_separator import RealTimeStemSeparator
from .recorder import Recorder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AudioChain:
    def __init__(self):
        self.device_manager = AudioDeviceManager()
        self.fs = self.device_manager.current_device["recommended_sample_rate"] if self.device_manager.current_device else 44100
        self.dj_decks = [DJDeck(i, self.fs) for i in range(4)]
        self.dj_mixer = DJMixer()
        self.effect_rack = EffectRack()
        self.ai_remixer = AIRemixer(self.fs)
        self.stem_separator = RealTimeStemSeparator()
        self.player = MediaPlayer(self.fs)
        self.production_tracks = [ProductionTrack(self.fs) for _ in range(8)]
        self.recorder = Recorder(self.fs)
        self.mic_active = False
        self.master_volume = 1.0
        self.stream = None
        self.configure()

    def configure(self):
        try:
            if self.stream:
                self.stream.close()
            self.device_manager.detect_device()
            success, message = self.device_manager.configure_audio()
            if not success:
                raise RuntimeError(message)
            self.fs = sd.default.samplerate
            for deck in self.dj_decks:
                deck.fs = self.fs
            self.player.fs = self.fs
            self.ai_remixer.fs = self.fs
            for track in self.production_tracks:
                track.fs = self.fs
            self.recorder.fs = self.fs
            self.stream = sd.OutputStream(samplerate=self.fs, blocksize=self.device_manager.current_device["default_buffer_size"], channels=2)
            self.stream.start()
        except Exception as e:
            logging.error("Ses yapılandırma hatası: %s", e)

    def process(self, block_size=128):
        output = np.zeros((block_size, 2))
        try:
            with futures.ThreadPoolExecutor() as executor:
                deck_futures = [executor.submit(deck.process, block_size) for deck in self.dj_decks]
                deck_outputs = [f.result() for f in deck_futures]
            dj_out = self.dj_mixer.process(deck_outputs, self.fs)
            bpm = self.dj_decks[0].bpm if self.dj_decks[0].bpm else None
            dj_out = self.effect_rack.process(dj_out, self.fs, bpm)
            output += dj_out
            player_out = self.player.process(block_size)
            output += player_out
            for track in self.production_tracks:
                prod_out = track.process(block_size, self.player.position if self.player.playing else 0)
                output += prod_out
            if self.mic_active:
                mic_input = np.random.randn(block_size, 2) * 0.1
                output += mic_input * self.dj_mixer.mic["gain"]
            output *= self.master_volume
            self.recorder.write(output)
            return output
        except Exception as e:
            logging.error("Ses işleme hatası: %s", e)
            return output

    def start_recording(self, filename: str):
        """Begin recording the master output to a file."""
        self.recorder.start(filename)

    def stop_recording(self):
        """Stop the current recording session."""
        self.recorder.stop()
