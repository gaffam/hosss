import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.theory import Scale, get_diatonic_chords


def test_scale_notes():
    scale = Scale('C', 'major')
    assert scale.notes[0] == 'C'
    assert scale.notes[3] == 'F'


def test_diatonic_chords():
    scale = Scale('C', 'major')
    chords = get_diatonic_chords(scale)
    assert chords[0] == 'C'
    assert chords[1] == 'Dm'
