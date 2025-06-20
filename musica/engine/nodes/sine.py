from __future__ import annotations

import numpy as np

from ..node import AudioNode

class SineNode(AudioNode):
    """A simple sine wave oscillator."""

    def __init__(self, frequency: float = 440.0, fs: int = 44100):
        super().__init__()
        self.frequency = frequency
        self.fs = fs
        self.phase = 0.0

    def process(self, block_size: int) -> None:
        t = (np.arange(block_size) + self.phase) / self.fs
        self.buffer = np.repeat(np.sin(2 * np.pi * self.frequency * t)[:, None], 2, axis=1)
        self.phase += block_size
        self.phase %= self.fs
