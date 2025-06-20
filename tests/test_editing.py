import os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica import trim, reverse, change_gain, normalize, fade_in, fade_out


def test_clip_editing():
    audio = np.ones(1000)
    assert trim(audio, 100, 200).shape[0] == 100
    assert reverse(audio)[0] == 1
    assert np.max(change_gain(audio, 0.5)) == 0.5
    norm = normalize(audio * 0.5)
    assert np.max(norm) == 1.0
    fi = fade_in(audio.copy(), 100)
    assert fi[0] == 0
    fo = fade_out(audio.copy(), 100)
    assert fo[-1] == 0
