import os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica import suggest_progressions, arpeggiate, generate_rhythm


def test_chord_progressions():
    progs = suggest_progressions('C')
    assert isinstance(progs, list)
    assert all(len(p) == 4 for p in progs)


def test_arpeggiator():
    seq = arpeggiate([60, 64, 67], pattern='updown', repeats=1)
    assert seq[0] == 60 and seq[-1] == 64


def test_rhythm_generator():
    pattern = generate_rhythm('techno', length=8)
    assert len(pattern) == 8
