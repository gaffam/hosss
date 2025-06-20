import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.project_manager import ProjectManager
from musica.production import ProductionTrack
from musica.effects import EffectRack


def test_save_load(tmp_path):
    pm = ProjectManager(directory=tmp_path)
    data = {'a': 1}
    path = pm.save('test', data)
    assert os.path.exists(path)
    loaded = pm.load('test')
    assert loaded == data


def test_project_tracks(tmp_path):
    pm = ProjectManager(directory=tmp_path)
    track = ProductionTrack()
    track.add_midi_note(60, 100, 0.0, 0.1)
    chain = type('C', (), {'effect_rack': EffectRack(), 'production_tracks': [track], 'fs': 44100})()
    pm.save_project('proj', chain)
    track.midi_notes = []
    pm.load_project('proj', chain)
    assert chain.production_tracks[0].midi_notes[0]['note'] == 60
