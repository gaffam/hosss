from __future__ import annotations

import logging
import numpy as np

from ..node import AudioNode

try:  # optional dependency
    from dawdreamer import dawdreamer as _dd
except Exception:  # pragma: no cover - missing optional dependency
    _dd = None

logger = logging.getLogger(__name__)

class PluginHostNode(AudioNode):
    """Wrap an external plugin as an :class:`AudioNode`."""

    def __init__(self, plugin_path: str, fs: int = 44100, block_size: int = 512):
        super().__init__()
        self.plugin_path = plugin_path
        self.fs = fs
        self.block_size = block_size
        self.available = False
        if _dd is None:
            logger.warning("dawdreamer not available; PluginHostNode disabled")
            self.engine = None
            self.plugin = None
            self.playback = None
            return
        try:
            self.engine = _dd.RenderEngine(fs, block_size)
            self.plugin = self.engine.make_plugin_processor("plugin", plugin_path)
            self.plugin.record = True
            self.playback = self.engine.make_playback_processor(
                "input", np.zeros((2, block_size), dtype=np.float32)
            )
            dag = {
                "processors": [
                    {"name": "input"},
                    {"name": "plugin"},
                ],
                "connections": [
                    ("input", "plugin"),
                ],
            }
            self.engine.load_graph(dag)
            self.available = True
        except Exception as exc:  # pragma: no cover - runtime dependency
            logger.warning("Failed to load plugin %s: %s", plugin_path, exc)
            self.engine = None
            self.plugin = None
            self.playback = None

    def process(self, block_size: int) -> None:
        inp = (
            self.inputs[0].buffer
            if self.inputs
            else np.zeros((block_size, 2), dtype=np.float32)
        )
        if not self.available:
            self.buffer = inp
            return
        try:
            if inp.shape[0] != self.block_size:
                # resize to expected block size
                resized = np.zeros((self.block_size, inp.shape[1]), dtype=np.float32)
                n = min(self.block_size, inp.shape[0])
                resized[:n] = inp[:n]
                inp = resized
            self.playback.set_data(inp.T.astype(np.float32))
            self.engine.render(self.block_size / self.fs)
            out = self.plugin.get_audio().T
            self.buffer = out.astype(np.float32)
        except Exception as exc:
            logger.error("Plugin processing failed: %s", exc)
            self.buffer = inp
