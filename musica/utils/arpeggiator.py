"""Simple arpeggiator utility."""

from typing import List


def arpeggiate(notes: List[int], pattern: str = "up", repeats: int = 1) -> List[int]:
    """Return an arpeggiated sequence of MIDI notes."""
    seq = []
    if pattern == "down":
        notes = list(reversed(notes))
    for _ in range(repeats):
        seq.extend(notes)
    if pattern == "updown":
        seq.extend(list(reversed(notes))[1:-1])
    return seq
