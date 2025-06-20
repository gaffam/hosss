import os
import logging
import numpy as np
try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except Exception:  # pragma: no cover - optional dependency
    TORCH_AVAILABLE = False
import soundfile as sf
import librosa

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIRemixer:
    """AI based remix generator - simple sample layering."""

    def __init__(self, fs=44100):
        self.fs = fs
        self.samples = {}

    def load_samples(self, sample_dir):
        try:
            for file in os.listdir(sample_dir):
                if file.endswith(('.wav', '.flac')):
                    name = os.path.splitext(file)[0]
                    with sf.SoundFile(os.path.join(sample_dir, file)) as f:
                        self.samples[name] = f.read()
            logging.info("%d sample yüklendi", len(self.samples))
        except FileNotFoundError:
            logging.error("Sample dizini bulunamadı: %s", sample_dir)

    def generate_remix(self, description, bpm=120, duration=60, key="C"):
        try:
            tokens = description.lower().split()
            style = "trap" if "trap" in tokens else "house"
            elements = []
            if "bass" in tokens:
                elements.extend(["kick", "bass"])
            if "vocal" in tokens:
                elements.append("vocal")
            if TORCH_AVAILABLE:
                output = torch.zeros((int(duration * self.fs), 2), dtype=torch.float32)
            else:
                output = np.zeros((int(duration * self.fs), 2))
            beat_samples = int(self.fs * 60 / bpm / 4)
            for i in range(0, len(output), beat_samples):
                for elem in elements:
                    if elem in self.samples and np.random.random() > 0.3:
                        sample = self.samples[elem]
                        start = i % len(output)
                        end = min(start + len(sample), len(output))
                        if TORCH_AVAILABLE:
                            output[start:end] += torch.tensor(sample[:end-start])
                        else:
                            output[start:end] += sample[:end-start]
            return output.cpu().numpy() if TORCH_AVAILABLE else output
        except Exception as e:
            logging.error("AI Remix hatası: %s", e)
            return np.zeros((int(duration * self.fs), 2))
