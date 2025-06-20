import json
import os

# Config Okuma
try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    CONFIG = {
        "devices_dir": "devices",
        "default_profile": {
            "device_id": "realtek_alc1220",
            "name": "Realtek ALC1220",
            "manufacturer": "Realtek",
            "type": "Integrated Audio",
            "driver_type": ["WASAPI"],
            "bit_depth": [16, 24],
            "sample_rates": [44100, 48000, 96000],
            "recommended_sample_rate": 44100,
            "default_buffer_size": 256,
            "min_buffer_size": 128,
            "max_buffer_size": 1024,
            "latency_tolerance": "medium",
            "dsd_support": False,
            "dac_chip": "Realtek ALC1220",
            "phantom_power": False
        }
    }

# List of available plugin names. Additional plugins can be placed under
# musica/plugins and will be detected at runtime.
EFFECTS_LIST = [
    "reverb",
    "compressor",
    "flanger",
]

SHORTCUTS = {
    "play_deck1": "Q", "play_deck2": "W", "play_deck3": "E", "play_deck4": "R",
    "cue_deck1": "A", "cue_deck2": "S", "cue_deck3": "D", "cue_deck4": "F",
    "load_deck": "Ctrl+O", "mic_toggle": "T", "media_scan": "Ctrl+S",
    "master_volume_up": "+", "master_volume_down": "-",
    "crossfader_left": "Left", "crossfader_right": "Right",
    "pad_1": "1", "pad_2": "2", "pad_3": "3", "pad_4": "4",
    "pad_5": "5", "pad_6": "6", "pad_7": "7", "pad_8": "8",
    "pad_9": "Z", "pad_10": "X", "pad_11": "C", "pad_12": "V",
    "pad_13": "B", "pad_14": "N", "pad_15": "M", "pad_16": ",",
    "effect_select": "F1-F12",
    "play_pause_player": "Space", "next_track": "Right", "prev_track": "Left",
    "midi_note": "Q", "midi_copy": "C", "midi_paste": "V",
    "metronome_toggle": "M"
}
