import os
import logging
import numpy as np
import soundfile as sf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MediaPlayer:
    def __init__(self, fs=44100):
        self.fs = fs
        self.playlist = []
        self.current_track = None
        self.position = 0
        self.playing = False
        self.volume = 1.0
        self.audio = None

    def load_playlist(self, directory):
        try:
            self.playlist = []
            for file in os.listdir(directory):
                if file.endswith(('.flac', '.m4a', '.alac', '.wav', '.mp3')):
                    self.playlist.append(os.path.join(directory, file))
            logging.info("Playlist yüklendi: %d parça", len(self.playlist))
        except FileNotFoundError:
            logging.error("Playlist dizini bulunamadı: %s", directory)

    def play(self, track_index=None):
        try:
            if track_index is not None and 0 <= track_index < len(self.playlist):
                self.current_track = self.playlist[track_index]
                with sf.SoundFile(self.current_track) as f:
                    self.audio = f.read()
                    self.fs = f.samplerate
                self.position = 0
                self.playing = True
                logging.info("Player: %s oynatılıyor", self.current_track)
        except Exception as e:
            logging.error("Player oynatma hatası: %s", e)

    def pause(self):
        self.playing = False

    def next_track(self):
        current_idx = self.playlist.index(self.current_track) if self.current_track in self.playlist else -1
        if current_idx + 1 < len(self.playlist):
            self.play(current_idx + 1)

    def prev_track(self):
        current_idx = self.playlist.index(self.current_track) if self.current_track in self.playlist else -1
        if current_idx > 0:
            self.play(current_idx - 1)

    def process(self, block_size):
        if not self.playing or self.audio is None:
            return np.zeros((block_size, 2))
        start = int(self.position)
        end = min(start + block_size, len(self.audio))
        block = self.audio[start:end] * self.volume
        self.position += block_size
        if self.position >= len(self.audio):
            self.next_track()
        return block
