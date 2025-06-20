import numpy as np
from scipy.signal import lfilter


class SimpleSynth:
    """Tiny synthesizer producing basic waveforms.

    The synth now supports a resonant low-pass filter, an amplitude envelope
    (ADSR) and a simple LFO for basic modulation.  These additions make it
    usable for more interesting sound design experiments while keeping the
    implementation minimal.
    """

    def __init__(
        self,
        wave: str = "sine",
        fs: int = 44100,
        live_mode: bool = False,
        cutoff: float = 20000.0,
        resonance: float = 0.0,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.8,
        release: float = 0.1,
        lfo_rate: float = 0.0,
        lfo_depth: float = 0.0,
        lfo_target: str = "pitch",
    ):
        self.wave = wave
        self.fs = fs
        self.live_mode = live_mode
        self.cutoff = cutoff
        self.resonance = resonance
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.lfo_rate = lfo_rate
        self.lfo_depth = lfo_depth
        self.lfo_target = lfo_target

    def _osc(self, freq, t):
        if self.wave == 'square':
            return np.sign(np.sin(2 * np.pi * freq * t))
        if self.wave == 'saw':
            return 2 * (t * freq - np.floor(0.5 + t * freq))
        if self.wave == 'triangle':
            return 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        return np.sin(2 * np.pi * freq * t)

    def _envelope(self, length: int) -> np.ndarray:
        a = int(self.attack * self.fs)
        d = int(self.decay * self.fs)
        r = int(self.release * self.fs)
        a = min(a, length)
        d = min(d, max(0, length - a))
        r = min(r, max(0, length - a - d))
        sustain_len = max(0, length - a - d - r)
        env = np.zeros(length)
        idx = 0
        if a > 0:
            env[:a] = np.linspace(0, 1, a, False)
            idx += a
        if d > 0:
            env[idx:idx+d] = np.linspace(1, self.sustain, d, False)
            idx += d
        if sustain_len > 0:
            env[idx:idx+sustain_len] = self.sustain
            idx += sustain_len
        if r > 0:
            env[idx:idx+r] = np.linspace(self.sustain, 0, r)
        return env

    def _lowpass(self, signal: np.ndarray, cutoff: float) -> np.ndarray:
        # simple biquad low-pass filter with resonance mapped to Q
        omega = 2 * np.pi * cutoff / self.fs
        q = max(0.1, 1.0 - self.resonance + 1e-6)
        alpha = np.sin(omega) / (2 * q)
        cos_w = np.cos(omega)
        b0 = (1 - cos_w) / 2
        b1 = 1 - cos_w
        b2 = (1 - cos_w) / 2
        a0 = 1 + alpha
        a1 = -2 * cos_w
        a2 = 1 - alpha
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1 / a0, a2 / a0])
        return lfilter(b, a, signal)

    def synthesize(self, note: int, velocity: int, duration: float):
        freq = 440.0 * 2 ** ((note - 69) / 12)
        n_samples = int(self.fs * duration)
        t = np.linspace(0, duration, n_samples, False)

        if self.lfo_rate > 0 and self.lfo_depth > 0 and self.lfo_target == "pitch":
            lfo = 1 + self.lfo_depth * np.sin(2 * np.pi * self.lfo_rate * t)
            osc = self._osc(freq * lfo, t)
        else:
            osc = self._osc(freq, t)

        env = self._envelope(n_samples)
        wave = osc * env * (velocity / 127.0)

        if self.cutoff < self.fs / 2:
            cutoff = self.cutoff
            if self.lfo_rate > 0 and self.lfo_target == "filter":
                mod = 1 + self.lfo_depth * np.sin(2 * np.pi * self.lfo_rate * t)
                cutoff = np.clip(cutoff * mod, 20, self.fs / 2 - 100)
                filtered = np.zeros_like(wave)
                for i, c in enumerate(cutoff):
                    filtered[i] = self._lowpass(np.array([wave[i]]), c)[0]
            else:
                filtered = self._lowpass(wave, cutoff)
            wave = filtered

        return np.repeat(wave[:, None], 2, axis=1)

    def synthesize_part(self, note: int, velocity: int, start: float, length: int):
        freq = 440.0 * 2 ** ((note - 69) / 12)
        t = start + np.arange(length) / self.fs
        if self.lfo_rate > 0 and self.lfo_depth > 0 and self.lfo_target == "pitch":
            lfo = 1 + self.lfo_depth * np.sin(2 * np.pi * self.lfo_rate * t)
            osc = self._osc(freq * lfo, t)
        else:
            osc = self._osc(freq, t)
        env = self._envelope(length)
        wave = osc * env * (velocity / 127.0)
        if self.cutoff < self.fs / 2:
            wave = self._lowpass(wave, self.cutoff)
        return np.repeat(wave[:, None], 2, axis=1)
