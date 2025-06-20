"""Basic music theory helpers for scales and chords."""

from typing import List

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# mode intervals in semitones from root
MODES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],  # natural minor
    'dorian': [0, 2, 3, 5, 7, 9, 10],
}

class Scale:
    """Represent a musical scale."""

    def __init__(self, root: str, mode: str = 'major') -> None:
        if root not in NOTE_NAMES:
            raise ValueError(f"Unknown root note {root}")
        if mode not in MODES:
            raise ValueError(f"Unknown mode {mode}")
        self.root = root
        self.mode = mode
        self.intervals = MODES[mode]

    @property
    def notes(self) -> List[str]:
        root_idx = NOTE_NAMES.index(self.root)
        return [NOTE_NAMES[(root_idx + i) % 12] for i in self.intervals]


def get_diatonic_chords(scale: Scale) -> List[str]:
    """Return the basic diatonic triads for ``scale``."""
    notes = scale.notes
    qualities_map = {
        'major': ['','m','m','','','m','dim'],
        'minor': ['m','dim','','m','m','',''],
    }
    qualities = qualities_map.get(scale.mode, [''] * 7)
    extended = notes + notes[:4]
    chords = []
    for i in range(7):
        name = extended[i]
        quality = qualities[i] if i < len(qualities) else ''
        if quality == 'dim':
            chords.append(f"{name}dim")
        elif quality == 'm':
            chords.append(f"{name}m")
        else:
            chords.append(name)
    return chords
