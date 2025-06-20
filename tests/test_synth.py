import os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.synth import SimpleSynth

def test_synth_length():
    synth = SimpleSynth(fs=22050)
    audio = synth.synthesize(69, 100, 0.5)
    assert audio.shape[0] == int(22050 * 0.5)
    assert audio.shape[1] == 2
    assert np.all(np.abs(audio) <= 1.0)


def test_synth_envelope_filter():
    synth = SimpleSynth(fs=22050, cutoff=500.0, resonance=0.5, attack=0.01)
    audio = synth.synthesize(60, 127, 0.1)
    # should still produce stereo samples within range
    assert audio.shape[1] == 2
    assert np.all(np.abs(audio) <= 1.0)
