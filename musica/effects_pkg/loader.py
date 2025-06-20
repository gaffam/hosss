import importlib
import pkgutil
import os
from types import ModuleType
from typing import Dict, Type


class EffectInterface:
    """Base class for effect plugins providing parameter handling."""

    def __init__(self, **kwargs):
        pass

    def __call__(self, audio, sample_rate):  # pragma: no cover - to be overridden
        return audio

    # The following helpers allow GUI editors to introspect and modify effect
    # parameters dynamically. Default implementations work with subclasses that
    # store attributes directly on ``self``.
    def get_params(self):
        return {
            k: getattr(self, k)
            for k in dir(self)
            if not k.startswith("_") and isinstance(getattr(self, k), (int, float))
        }

    def set_params(self, **params):
        for k, v in params.items():
            if hasattr(self, k):
                setattr(self, k, v)


class PluginLoader:
    """Dynamically load effect plugins from a directory."""

    def __init__(self, package: str = "musica.plugins"):
        self.package = package
        self.plugins: Dict[str, Type[EffectInterface]] = {}
        self.load_plugins()

    def load_plugins(self):
        package = importlib.import_module(self.package)
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{self.package}.{name}")
            cls = self._find_effect_class(module)
            if cls:
                self.plugins[name.lower()] = cls

    def _find_effect_class(self, module: ModuleType):
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, EffectInterface) and obj is not EffectInterface:
                return obj
        return None

    def create(self, name: str, **params) -> EffectInterface:
        cls = self.plugins.get(name.lower())
        if cls is None:
            raise ValueError(f"Effect not found: {name}")
        return cls(**params)
