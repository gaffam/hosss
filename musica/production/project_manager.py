import json
import os
import numpy as np

from .track import ProductionTrack
from ..effects_pkg import EffectRack


class ProjectManager:
    """Save and load project state."""

    def __init__(self, directory="projects"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def save(self, name, data):
        path = os.path.join(self.directory, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return path

    def load(self, name):
        path = os.path.join(self.directory, f"{name}.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # New high level helpers ----------------------------------------------
    def save_project(self, name: str, chain) -> str:
        """Serialize ``chain`` state and save to ``name``."""
        data = {
            "effects": chain.effect_rack.serialize(),
            "tracks": [self._serialize_track(t) for t in chain.production_tracks],
        }
        path = self.save(name, data)
        try:
            from ..user_settings import load_settings
            from ..open_music import submit_data

            settings = load_settings()
            if settings.get("share_data"):
                submit_data({
                    "tracks": [
                        {"midi": t["midi"]} for t in data["tracks"]
                    ]
                })
        except Exception:  # pragma: no cover - network/file
            pass
        return path

    def load_project(self, name: str, chain) -> None:
        """Load project ``name`` into ``chain``."""
        data = self.load(name)
        chain.effect_rack.load_from(data.get("effects", []))
        tracks = data.get("tracks", [])
        for idx, tdata in enumerate(tracks):
            if idx < len(chain.production_tracks):
                track = chain.production_tracks[idx]
            else:
                track = ProductionTrack(chain.fs)
                chain.production_tracks.append(track)
            self._apply_track(track, tdata)

    # Internal helpers ------------------------------------------------------
    def _serialize_track(self, track: ProductionTrack) -> dict:
        return {
            "clips": [
                {"audio": clip["audio"].tolist(), "start": clip["start"]}
                for clip in track.clips
            ],
            "midi": track.midi_notes,
            "automation": track.automation.points,
        }

    def _apply_track(self, track: ProductionTrack, data: dict) -> None:
        track.clips = [
            {"audio": np.array(c["audio"], dtype=float), "start": c["start"], "waveform": None}
            for c in data.get("clips", [])
        ]
        track.midi_notes = data.get("midi", [])
        track.automation.points = data.get("automation", [(0.0, 1.0)])
