"""Cloud project synchronization utilities."""

import os
import json
from threading import Thread
import logging

try:
    from flask import Flask, send_from_directory, request
    CLOUD_AVAILABLE = True
except Exception:  # pragma: no cover
    CLOUD_AVAILABLE = False


class CloudSync:
    """Synchronize project files via a simple Flask server."""

    def __init__(self, project_manager, directory="cloud"):
        self.pm = project_manager
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.app = None
        if CLOUD_AVAILABLE:
            self.app = Flask(__name__)
            self.app.add_url_rule("/push/<name>", "push", self._push, methods=["POST"])
            self.app.add_url_rule("/pull/<name>", "pull", self._pull)
        logging.info("CloudSync initialized at %s", self.directory)

    # ------------------------------------------------------------------
    def start(self, host="0.0.0.0", port=5001):  # pragma: no cover - network
        if not self.app:
            logging.warning("Flask unavailable, cloud server not started")
            return
        Thread(target=lambda: self.app.run(host=host, port=port), daemon=True).start()

    # ------------------------------------------------------------------
    def push(self, name: str, data: dict):
        path = os.path.join(self.directory, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logging.info("Project %s pushed to cloud", name)
        return path

    def pull(self, name: str) -> dict:
        path = os.path.join(self.directory, f"{name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.pm.save(name, data)
        logging.info("Project %s pulled from cloud", name)
        return data

    # Flask endpoints --------------------------------------------------
    def _push(self, name):  # pragma: no cover - network
        data = request.get_json()
        self.push(name, data)
        return {"status": "ok"}

    def _pull(self, name):  # pragma: no cover - network
        return send_from_directory(self.directory, f"{name}.json")
