import logging
import numpy as np
from scipy.signal import butter, lfilter

from .loader import PluginLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Neve1073Sim:
    """Simple EQ simulation of the Neve 1073 preamp."""

    def __init__(self, low_gain=0.0, mid_gain=0.0, high_gain=0.0):
        self.low_gain = low_gain / 15.0
        self.mid_gain = mid_gain / 15.0
        self.high_gain = high_gain / 15.0

    def process(self, audio, fs):
        if len(audio.shape) == 1:
            audio = np.expand_dims(audio, axis=1)
        b_low, a_low = butter(2, 200 / (fs / 2), btype='low')
        b_mid, a_mid = butter(2, [500 / (fs / 2), 3000 / (fs / 2)], btype='band')
        b_high, a_high = butter(2, 8000 / (fs / 2), btype='high')
        low = lfilter(b_low, a_low, audio) * (1 + self.low_gain)
        mid = lfilter(b_mid, a_mid, audio) * (1 + self.mid_gain)
        high = lfilter(b_high, a_high, audio) * (1 + self.high_gain)
        return np.clip(low + mid + high, -1.0, 1.0)


class EffectRack:
    """Manage realtime effects via plugin system."""

    def __init__(self):
        self.loader = PluginLoader()
        self.active_effects = []

    def add_effect(self, name, params=None):
        params = params or {}
        try:
            effect = self.loader.create(name, **params)
            self.active_effects = [fx for fx in self.active_effects if fx['name'] != name]
            self.active_effects.append({'name': name, 'instance': effect})
            logging.info("Efekt eklendi: %s", name)
        except Exception as e:
            logging.error("Efekt ekleme hatası: %s", e)

    def serialize(self):
        return [
            {"name": fx["name"], "params": fx["instance"].get_params()}
            for fx in self.active_effects
        ]

    def load_from(self, data):
        self.active_effects = []
        for item in data:
            try:
                self.add_effect(item["name"], item.get("params"))
            except Exception:
                continue

    def get_effect(self, name):
        for fx in self.active_effects:
            if fx["name"] == name:
                return fx["instance"]
        return None

    def process(self, audio, fs, bpm=None):
        processed = audio.copy()
        try:
            for fx in self.active_effects:
                processed = fx['instance'](processed, fs)
            return np.clip(processed, -1.0, 1.0)
        except Exception as e:
            logging.error("Efekt işleme hatası: %s", e)
            return processed
