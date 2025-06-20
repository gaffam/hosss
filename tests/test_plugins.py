import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.plugin_loader import PluginLoader


def test_plugin_loader():
    loader = PluginLoader()
    assert 'reverb' in loader.plugins
    fx = loader.create('reverb')
    assert hasattr(fx, '__call__')
