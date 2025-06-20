import json
import os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".musica_settings.json")
DEFAULTS = {
    "api_key": "",
    "monthly_api_calls": 0,
    "last_call_month": "",
    "share_data": False,
}


def load_settings():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = DEFAULTS.copy()
    for k, v in DEFAULTS.items():
        data.setdefault(k, v)
    return data


def save_settings(settings):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
