"""Basic audio clip editing helpers."""

import numpy as np


def trim(audio: np.ndarray, start: int, end: int) -> np.ndarray:
    """Return a slice of ``audio`` between start and end samples."""
    start = max(0, start)
    end = min(len(audio), end)
    return audio[start:end]


def reverse(audio: np.ndarray) -> np.ndarray:
    """Return the reversed audio."""
    return audio[::-1]


def change_gain(audio: np.ndarray, factor: float) -> np.ndarray:
    """Multiply audio by ``factor``."""
    return np.clip(audio * factor, -1.0, 1.0)


def normalize(audio: np.ndarray) -> np.ndarray:
    """Normalize audio peak to 1.0."""
    peak = np.max(np.abs(audio)) or 1.0
    return audio / peak


def fade_in(audio: np.ndarray, length: int) -> np.ndarray:
    """Apply a linear fade in."""
    length = min(length, len(audio))
    fade = np.linspace(0.0, 1.0, length)
    audio[:length] *= fade
    return audio


def fade_out(audio: np.ndarray, length: int) -> np.ndarray:
    """Apply a linear fade out."""
    length = min(length, len(audio))
    fade = np.linspace(1.0, 0.0, length)
    audio[-length:] *= fade
    return audio
