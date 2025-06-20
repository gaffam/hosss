import os
import sys
import numpy as np
import soundfile as sf
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.sample_recommender import SampleRecommender


def test_recommend(tmp_path):
    sr = 22050
    t = np.linspace(0, 1, sr, False)
    sine = 0.1 * np.sin(2 * np.pi * 440 * t)
    fname = tmp_path / 'a.wav'
    sf.write(fname, sine, sr)
    rec = SampleRecommender(str(tmp_path))
    results = rec.recommend(rec.index['a.wav']['tempo'], rec.index['a.wav']['key'])
    assert 'a.wav' in results
