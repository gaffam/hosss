from musica.effects_pkg.loader import EffectInterface

class ReverbEffect(EffectInterface):
    def __init__(self, room_size=0.5, damping=0.5, wet=0.3):
        self.room_size = room_size
        self.damping = damping
        self.wet = wet
        self.buffer = [0.0] * 44100

    def __call__(self, audio, sample_rate):
        import numpy as np
        wet = np.zeros_like(audio)
        for i in range(len(audio)):
            self.buffer.insert(0, audio[i].mean() * self.room_size)
            wet[i] = self.buffer[int(sample_rate * 0.03)] * (1 - self.damping)
            self.buffer.pop()
        return audio * (1 - self.wet) + wet * self.wet

    def get_params(self):
        return {
            "room_size": self.room_size,
            "damping": self.damping,
            "wet": self.wet,
        }

    def set_params(self, **params):
        for k in ("room_size", "damping", "wet"):
            if k in params:
                setattr(self, k, params[k])
