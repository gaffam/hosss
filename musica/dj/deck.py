import logging
import numpy as np
import soundfile as sf
import librosa
from scipy.signal import butter, lfilter

from ..effects_pkg import Neve1073Sim, EffectRack

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DJDeck:
    def __init__(self, deck_id, fs=44100):
        self.deck_id = deck_id
        self.fs = fs
        self.audio = None
        self.original_audio = None
        self.stems = None
        self.position = 0
        self.playing = False
        self.pitch = 1.0
        self.cue_points = []
        self.hot_cues = [None] * 8
        self.loop = None
        self.volume = 1.0
        self.bpm = None
        self.key = None
        self.waveform_cache = None
        self.metronome = False
        self.metronome_sound = np.sin(2 * np.pi * 440 * np.arange(int(fs * 0.1)) / fs) * 0.2
        self.effect_rack = EffectRack()

    def load_track(self, file_path):
        try:
            if file_path.endswith(('.flac', '.m4a', '.alac', '.wav')):
                with sf.SoundFile(file_path) as f:
                    self.audio = f.read()
                    self.original_audio = self.audio.copy()
                    self.fs = f.samplerate
                self.stems = None
                self.bpm, _ = librosa.beat.beat_track(y=self.audio.mean(axis=0), sr=self.fs)
                self.waveform_cache = self.audio.mean(axis=0)[::10]
                try:
                    f0 = librosa.yin(
                        self.audio.mean(axis=0),
                        fmin=librosa.note_to_hz("C2"),
                        fmax=librosa.note_to_hz("C7"),
                        sr=self.fs,
                    )
                    self.key = librosa.hz_to_note(float(np.median(f0)))
                except Exception:
                    self.key = None
                logging.info("Deck %s: %s yüklendi, BPM: %s", self.deck_id, file_path, self.bpm)
                return True
            raise ValueError("Unsupported format")
        except Exception as e:
            logging.error("Yükleme hatası: %s", e)
            return False

    def preview(self, duration=5.0):
        if self.audio is not None:
            return self.audio[:int(duration * self.fs)]
        return None

    def play(self):
        self.playing = True
        logging.info("Deck %s oynatılıyor", self.deck_id)

    def pause(self):
        self.playing = False
        logging.info("Deck %s durduruldu", self.deck_id)

    def toggle_metronome(self):
        self.metronome = not self.metronome

    def set_cue(self, position):
        self.cue_points.append(position)

    def set_hot_cue(self, index, position):
        self.hot_cues[index] = position

    def trigger_hot_cue(self, index):
        if self.hot_cues[index] is not None:
            self.position = self.hot_cues[index]
            self.play()

    def set_loop(self, start, beat_count=8):
        """Set a loop starting at ``start`` for a number of beats."""
        if self.bpm:
            beat_duration = self.fs * 60 / self.bpm
            end = start + beat_duration * beat_count
        else:
            end = start + 10000
        self.loop = (start, end)
        logging.info("Deck %s loop: %d-%d", self.deck_id, start, end)

    def process(self, block_size):
        if not self.playing or self.audio is None:
            return np.zeros((block_size, 2))
        start = int(self.position)
        end = min(start + int(block_size * self.pitch), len(self.audio))
        block = self.audio[start:end] * self.volume
        if self.loop:
            loop_start, loop_end = self.loop
            if self.position >= loop_end:
                self.position = loop_start
        self.position += block_size * self.pitch
        block = librosa.resample(block, orig_sr=self.fs, target_sr=int(self.fs / self.pitch))
        block = self.effect_rack.process(block, self.fs)
        return block

    def get_stem(self, kind, separator):
        if self.original_audio is None:
            return None
        if self.stems is None:
            self.stems = separator.separate(self.original_audio, self.fs)
        return self.stems.get(kind)

class DJMixer:
    def __init__(self, num_channels=4):
        self.channels = [
            {"gain": 1.0, "eq_low": 0.0, "eq_mid": 0.0, "eq_high": 0.0, "filter": 0.0, "volume": 1.0}
            for _ in range(num_channels)
        ]
        self.crossfader = 0.5
        self.master_volume = 1.0
        self.mic = {"gain": 1.0, "talkover": False}

    def process(self, deck_outputs, fs=44100):
        output = np.zeros_like(deck_outputs[0])
        try:
            for i, (deck_out, ch) in enumerate(zip(deck_outputs, self.channels)):
                eq = Neve1073Sim(low_gain=ch["eq_low"], mid_gain=ch["eq_mid"], high_gain=ch["eq_high"])
                processed = eq.process(deck_out, fs)
                if ch["filter"] != 0:
                    cutoff = 200 + (abs(ch["filter"]) * 19800)
                    b, a = butter(2, cutoff / (fs / 2), btype='low' if ch["filter"] < 0 else 'high')
                    processed = lfilter(b, a, processed)
                processed *= ch["gain"] * ch["volume"]
                if i < 2 and self.crossfader < 0.5:
                    processed *= (1 - self.crossfader * 2)
                elif i >= 2 and self.crossfader > 0.5:
                    processed *= (self.crossfader * 2 - 1)
                output += processed
            output *= self.master_volume
            if self.mic["talkover"]:
                output *= 0.7
            return output
        except Exception as e:
            logging.error("Mikser işleme hatası: %s", e)
            return output
