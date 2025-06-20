import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.rhythm_generator import generate_euclidean


def test_euclidean_length():
    pattern = generate_euclidean(3, 8)
    assert len(pattern) == 8
    assert sum(pattern) == 3
