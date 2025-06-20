"""Core audio components with lazy imports."""

import importlib

__all__ = [
    'AudioChain',
    'AudioDeviceManager',
    'Recorder',
    'RealTimeStemSeparator',
    'SampleRecommender',
    'AIRemixer',
    'MediaPlayer',
    'CloudSync',
    'suggest_progressions',
    'GrooveAssistant',
    'generate',
    'generate_euclidean',
]

_module_map = {
    'AudioChain': 'musica.core.chain',
    'AudioDeviceManager': 'musica.core.device',
    'Recorder': 'musica.core.recorder',
    'RealTimeStemSeparator': 'musica.core.stem_separator',
    'SampleRecommender': 'musica.core.sample_recommender',
    'AIRemixer': 'musica.core.ai_remixer',
    'MediaPlayer': 'musica.core.player',
    'CloudSync': 'musica.core.cloud_sync',
    'suggest_progressions': 'musica.core.chord_generator',
    'GrooveAssistant': 'musica.core.groove_assistant',
    'generate': 'musica.core.rhythm_generator',
    'generate_euclidean': 'musica.core.rhythm_generator',
}

def __getattr__(name):
    if name in _module_map:
        module = importlib.import_module(_module_map[name])
        return getattr(module, name)
    raise AttributeError(f"module 'musica.core' has no attribute '{name}'")
