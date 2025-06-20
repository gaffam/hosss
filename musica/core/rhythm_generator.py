"""Tiny rhythm pattern helper."""

from typing import List
import numpy as np

STYLES = {
    "techno": ["kick", None, None, "snare", "kick", None, None, None],
    "trap": ["kick", "hat", "snare", "hat", "kick", "hat", "snare", "hat"],
}


def generate(style: str = "techno", length: int = 8) -> List[str]:
    base = STYLES.get(style, STYLES["techno"])
    pattern = [base[i % len(base)] for i in range(length)]
    # random slight variations
    rng = np.random.default_rng()
    return [step if rng.random() > 0.2 else None for step in pattern]


def generate_euclidean(beats: int, steps: int) -> List[int]:
    """Generate a Euclidean rhythm pattern of ``steps`` length."""
    if beats <= 0 or steps <= 0 or beats > steps:
        raise ValueError("Invalid beats/steps")

    pattern = []
    counts = []
    remainders = []
    divisor = steps - beats
    remainders.append(beats)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level += 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)

    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)
        else:
            for _ in range(counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)

    build(level)
    return pattern[:steps]
