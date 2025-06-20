import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.groove_assistant import GrooveAssistant


def test_groove_length():
    pattern = ['kick', None, 'snare', None]
    ga = GrooveAssistant()
    new_pattern = ga.suggest(pattern)
    assert len(new_pattern) == len(pattern)
