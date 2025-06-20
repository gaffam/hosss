import logging
import numpy as np

try:
    from spleeter.separator import Separator
    SPLEETER_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    SPLEETER_AVAILABLE = False


class RealTimeStemSeparator:
    """Separate audio into stems using Spleeter if available."""

    def __init__(self, model: str = "spleeter:2stems"):
        self.model = model
        if SPLEETER_AVAILABLE:
            self.separator = Separator(model)
        else:
            self.separator = None
            logging.warning("Spleeter not installed, using naive separation")

    def separate(self, audio: np.ndarray, sr: int):
        """Return a dict with stem arrays."""
        if self.separator:
            prediction = self.separator.separate(audio)
            return {k: v for k, v in prediction.items()}
        # naive fallback: simple high/low pass split
        from scipy.signal import butter, lfilter
        if audio.ndim == 1:
            audio = np.expand_dims(audio, 1)
        b, a = butter(2, 300, btype="highpass", fs=sr)
        vocals = lfilter(b, a, audio)
        accompaniment = audio - vocals
        return {"vocals": vocals, "accompaniment": accompaniment}
