import os
import numpy as np
from typing import List, Dict
import librosa

class SampleRecommender:
    """Recommend samples from a library based on key and tempo."""

    def __init__(self, library_dir: str):
        self.library_dir = library_dir
        self.index: Dict[str, Dict[str, float]] = {}
        self._scan()

    def _scan(self):
        for file in os.listdir(self.library_dir):
            if not file.endswith((".wav", ".flac")):
                continue
            path = os.path.join(self.library_dir, file)
            try:
                y, sr = librosa.load(path, mono=True, duration=10)
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                f0 = librosa.yin(
                    y,
                    fmin=librosa.note_to_hz("C2"),
                    fmax=librosa.note_to_hz("C7"),
                    sr=sr,
                )
                note = librosa.hz_to_note(np.median(f0))
                self.index[file] = {"tempo": float(tempo), "key": note}
            except Exception:
                continue

    def recommend(self, tempo: float, key: str) -> List[str]:
        matches = []
        for name, meta in self.index.items():
            if abs(meta["tempo"] - tempo) < 5 and meta["key"] == key:
                matches.append(name)
        return matches
