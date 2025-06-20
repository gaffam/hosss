from importlib import import_module

_pkg = import_module('musica.effects_pkg.plugins')
__all__ = getattr(_pkg, '__all__', [])
__path__ = _pkg.__path__
globals().update({name: getattr(_pkg, name) for name in __all__})
