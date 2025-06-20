from musica.effects_pkg.loader import EffectInterface

class CompressorEffect(EffectInterface):
    def __init__(self, threshold_db=-24.0, ratio=4.0, wet=0.3):
        self.threshold = 10 ** (threshold_db / 20)
        self.ratio = ratio
        self.wet = wet

    def __call__(self, audio, sample_rate):
        import numpy as np
        mag = np.abs(audio)
        gain = np.ones_like(mag)
        mask = mag > self.threshold
        gain[mask] = (self.threshold + (mag[mask] - self.threshold) / self.ratio) / mag[mask]
        comp = audio * gain
        return audio * (1 - self.wet) + comp * self.wet

    def get_params(self):
        import math
        return {
            "threshold_db": 20 * math.log10(self.threshold),
            "ratio": self.ratio,
            "wet": self.wet,
        }

    def set_params(self, **params):
        if "threshold_db" in params:
            self.threshold = 10 ** (params["threshold_db"] / 20)
        if "ratio" in params:
            self.ratio = params["ratio"]
        if "wet" in params:
            self.wet = params["wet"]
