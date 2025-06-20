from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
import numpy as np

class AudioNode(ABC):
    """Base class for all audio processing nodes."""

    def __init__(self):
        self.inputs: List[AudioNode] = []
        self.buffer: np.ndarray | None = None

    def connect(self, node: 'AudioNode') -> None:
        if node not in self.inputs:
            self.inputs.append(node)

    def disconnect(self, node: 'AudioNode') -> None:
        if node in self.inputs:
            self.inputs.remove(node)

    @abstractmethod
    def process(self, block_size: int) -> None:
        """Process audio into ``self.buffer`` of shape (block_size, 2)."""
        pass
