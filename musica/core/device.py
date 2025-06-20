import json
import os
import logging
import sounddevice as sd

from .config import CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AudioDeviceManager:
    """Manage audio device configuration and detection."""

    def __init__(self):
        self.devices_dir = CONFIG.get("devices_dir", "devices")
        self.default_profile = CONFIG.get("default_profile")
        self.profiles = {}
        self.current_device = None
        self.load_profiles()

    def load_profiles(self):
        try:
            os.makedirs(self.devices_dir, exist_ok=True)
            for file in os.listdir(self.devices_dir):
                if file.endswith(".json"):
                    with open(os.path.join(self.devices_dir, file), 'r') as f:
                        profile = json.load(f)
                        self.profiles[profile["device_id"]] = profile
            self.profiles[self.default_profile["device_id"]] = self.default_profile
            logging.info("%d ses kartı profili yüklendi", len(self.profiles))
        except Exception as e:
            logging.error("Profil yükleme hatası: %s", e)

    def detect_device(self):
        try:
            devices = sd.query_devices()
            detected = devices[sd.default.device["output"]]["name"].lower()
            for device_id, profile in self.profiles.items():
                if device_id in detected or profile["name"].lower() in detected:
                    self.current_device = profile
                    return profile
            self.current_device = self.default_profile
            return self.default_profile
        except Exception as e:
            logging.error("Cihaz algılama hatası: %s", e)
            return self.default_profile

    def configure_audio(self, fs=None, buffer_size=None):
        if not self.current_device:
            self.detect_device()
        profile = self.current_device
        fs = fs or profile["recommended_sample_rate"]
        buffer_size = buffer_size or profile["default_buffer_size"]
        try:
            sd.default.samplerate = fs
            sd.default.blocksize = buffer_size
            sd.default.device = sd.default.device["output"]
            logging.info("Ses yapılandırıldı: %s, %dHz, %d buffer", profile['name'], fs, buffer_size)
            return True, ""
        except Exception as e:
            logging.error("Ses yapılandırma hatası: %s", e)
            return False, str(e)
