from musica.effects_pkg.loader import EffectInterface

class FlangerEffect(EffectInterface):
    def __init__(self, depth=0.005, rate=0.5, wet=0.3):
        self.depth = depth
        self.rate = rate
        self.wet = wet

    def __call__(self, audio, sample_rate):
        import numpy as np
        length = len(audio)
        time = np.arange(length) / sample_rate
        mod = np.sin(2 * np.pi * self.rate * time) * self.depth * sample_rate
        idx = np.clip(np.arange(length) + mod.astype(int), 0, length - 1)
        fl = audio[idx.astype(int)]
        return audio * (1 - self.wet) + fl * self.wet

    def get_params(self):
        return {"depth": self.depth, "rate": self.rate, "wet": self.wet}

    def set_params(self, **params):
        for k in ("depth", "rate", "wet"):
            if k in params:
                setattr(self, k, params[k])
