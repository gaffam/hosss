from __future__ import annotations

import numpy as np

try:  # optional sounddevice dependency
    import sounddevice as sd
except Exception:  # pragma: no cover - fallback if missing
    sd = None

from ..node import AudioNode

class OutputNode(AudioNode):
    """Final node sending audio to the sound device."""

    def __init__(self, fs: int = 44100, start_stream: bool = True):
        super().__init__()
        self.fs = fs
        self.stream = None
        if start_stream and sd is not None:
            try:
                self.stream = sd.OutputStream(samplerate=self.fs, channels=2, blocksize=0)
                self.stream.start()
            except Exception:
                self.stream = None

    def process(self, block_size: int) -> None:
        inp = self.inputs[0].buffer if self.inputs else np.zeros((block_size, 2))
        self.buffer = inp
        if self.stream is not None:
            self.stream.write(inp)
