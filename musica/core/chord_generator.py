"""Small helper for chord progressions."""

from typing import List

from ..utils.theory import Scale, get_diatonic_chords


def suggest_progressions(key: str, mode: str = "major") -> List[List[str]]:
    """Return a few diatonic 4-chord progressions for ``key`` and ``mode``."""
    scale = Scale(key, mode)
    chords = get_diatonic_chords(scale)
    if len(chords) < 4:
        return []
    return [chords[i:i + 4] for i in range(len(chords) - 3)]
