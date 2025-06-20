import os
import sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.stem_separator import RealTimeStemSeparator


def test_separate_basic():
    audio = np.zeros((44100, 2))
    sep = RealTimeStemSeparator()
    stems = sep.separate(audio, 44100)
    assert 'vocals' in stems and 'accompaniment' in stems
    assert stems['vocals'].shape[0] == 44100
