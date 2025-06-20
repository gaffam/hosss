import numpy as np
from typing import List

class GrooveAssistant:
    """Suggest groove variations for a simple drum pattern."""

    def suggest(self, pattern: List[str], style: str = "funk") -> List[str]:
        """Return a new pattern with slight timing offsets."""
        length = len(pattern)
        new_pattern = pattern.copy()
        rng = np.random.default_rng()
        swing = 0.1 if style == "funk" else 0.05
        for i, step in enumerate(pattern):
            if step is None:
                continue
            jitter = rng.uniform(-swing, swing)
            if rng.random() > 0.8:
                new_pattern[i] = step  # unchanged
            else:
                new_pattern[i] = f"{step}:{jitter:+.3f}"  # encode offset
        return new_pattern
