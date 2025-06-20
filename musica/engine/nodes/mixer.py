from __future__ import annotations

import numpy as np

from ..node import AudioNode

class MixerNode(AudioNode):
    """Mixes all input buffers together."""

    def process(self, block_size: int) -> None:
        if not self.inputs:
            self.buffer = np.zeros((block_size, 2))
            return
        out = np.zeros((block_size, 2))
        for node in self.inputs:
            buf = node.buffer
            if buf is None or len(buf) < block_size:
                buf = np.zeros((block_size, 2))
            out += buf[:block_size]
        self.buffer = np.clip(out, -1.0, 1.0)
