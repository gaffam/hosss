import logging
import numpy as np

from ..effects_pkg import EffectRack
from .automation import AutomationCurve
from ..utils.synth import SimpleSynth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProductionTrack:
    def __init__(self, fs=44100, live_mode=False):
        self.fs = fs
        self.clips = []
        self.midi_notes = []
        self.volume = 1.0
        self.effect_rack = EffectRack()
        self.automation = AutomationCurve()
        self.synth = SimpleSynth(fs=fs, live_mode=live_mode)
        self.live_mode = live_mode

    def add_clip(self, audio, start_time):
        waveform = audio.mean(axis=1)[:: max(1, len(audio)//100)] if audio.ndim > 1 else audio[:: max(1, len(audio)//100)]
        self.clips.append({"audio": audio, "start": start_time, "waveform": waveform})
        logging.info("Clip eklendi: %ss", start_time)

    def add_midi_note(self, note, velocity, start_time, duration):
        self.midi_notes.append({"note": note, "velocity": velocity, "start": start_time, "duration": duration})
        if not self.live_mode:
            audio = self.synth.synthesize(note, velocity, duration)
            self.add_clip(audio, start_time)
        logging.info("MIDI nota eklendi: %s", note)

    def process(self, block_size, position):
        output = np.zeros((block_size, 2))
        try:
            if self.live_mode:
                for note in self.midi_notes:
                    n_start = int(note["start"] * self.fs)
                    n_end = n_start + int(note["duration"] * self.fs)
                    if position < n_end and position + block_size > n_start:
                        note_audio = self.synth.synthesize(note["note"], note["velocity"], note["duration"])
                        start_idx = max(0, position - n_start)
                        dst = max(0, n_start - position)
                        length = min(block_size - dst, len(note_audio) - start_idx)
                        vol = self.volume * self.automation.value_at((position + dst) / self.fs)
                        output[dst:dst+length] += note_audio[start_idx:start_idx+length] * vol
            for clip in self.clips:
                clip_start = int(clip["start"] * self.fs)
                if clip_start <= position < clip_start + len(clip["audio"]):
                    start = position - clip_start
                    end = min(start + block_size, len(clip["audio"]))
                    vol = self.volume * self.automation.value_at((position) / self.fs)
                    output[:end-start] += clip["audio"][start:end] * vol
            output = self.effect_rack.process(output, self.fs)
            return output
        except Exception as e:
            logging.error("Track işleme hatası: %s", e)
            return output

    def add_effect(self, fx_name, params=None):
        """Add an effect to this track."""
        self.effect_rack.add_effect(fx_name, params)
