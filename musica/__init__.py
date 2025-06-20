"""Musica Pro Omnibus package."""

from .effects_pkg.loader import PluginLoader, EffectInterface
from .production.project_manager import ProjectManager
try:
    from .core.stem_separator import RealTimeStemSeparator
    from .core.groove_assistant import GrooveAssistant
except Exception:  # pragma: no cover - optional dependencies like sounddevice
    RealTimeStemSeparator = None
    GrooveAssistant = None
try:  # optional dependency: librosa
    from .core.sample_recommender import SampleRecommender
except Exception:  # pragma: no cover - skip if missing deps
    SampleRecommender = None
from .core.cloud_sync import CloudSync
from .core.recorder import Recorder
from .sound_generator import SoundGenerator
from .user_settings import load_settings, save_settings
from .production.automation import AutomationCurve
from .utils.synth import SimpleSynth
from .production.audio_editing import (
    trim,
    reverse,
    change_gain,
    normalize,
    fade_in,
    fade_out,
)
from .core.chord_generator import suggest_progressions
from .utils.arpeggiator import arpeggiate
from .core.rhythm_generator import generate as generate_rhythm, generate_euclidean
from .utils.theory import Scale, get_diatonic_chords

__all__ = [
    'PluginLoader',
    'EffectInterface',
    'ProjectManager',
    'RealTimeStemSeparator',
    'GrooveAssistant',
    'SampleRecommender',
    'CloudSync',
    'Recorder',
    'SoundGenerator',
    'load_settings',
    'save_settings',
    'AutomationCurve',
    'SimpleSynth',
    'trim',
    'reverse',
    'change_gain',
    'normalize',
    'fade_in',
    'fade_out',
    'suggest_progressions',
    'arpeggiate',
    'generate_rhythm',
    'generate_euclidean',
    'Scale',
    'get_diatonic_chords',
]
from .engine import (
    AudioGraph,
    AudioNode,
    SineNode,
    MixerNode,
    OutputNode,
    PluginHostNode,
)

__all__ += [
    'AudioGraph',
    'AudioNode',
    'SineNode',
    'MixerNode',
    'OutputNode',
    'PluginHostNode',
]
