import requests
import numpy as np
import soundfile as sf
from io import BytesIO
from datetime import datetime

from .user_settings import load_settings, save_settings

class SoundGenerator:
    """Generate audio using the Hugging Face inference API."""

    API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Hugging Face API anahtarı gereklidir.")
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def generate(self, prompt_text: str, duration_seconds: int = 5):
        print(f"'{prompt_text}' için bulut sunucusuna istek gönderiliyor...")
        payload = {"inputs": f"{prompt_text}, {duration_seconds} seconds long"}
        try:
            resp = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=60)
            resp.raise_for_status()
            with sf.SoundFile(BytesIO(resp.content)) as f:
                audio = f.read(dtype='float32')
                sr = f.samplerate
        except Exception as e:  # pragma: no cover - network
            print(f"Bulut AI ile ses üretimi sırasında bir hata oluştu: {e}")
            return None, 0
        self._update_usage()
        print("Ses başarıyla üretildi ve alındı.")
        return audio, sr

    def _update_usage(self):
        settings = load_settings()
        now = datetime.now().strftime("%Y-%m")
        if settings.get("last_call_month") != now:
            settings["monthly_api_calls"] = 0
            settings["last_call_month"] = now
        settings["monthly_api_calls"] = settings.get("monthly_api_calls", 0) + 1
        save_settings(settings)
