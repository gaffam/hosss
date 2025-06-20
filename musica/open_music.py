"""Utilities for sharing anonymized project data with the Open Music Library."""
import logging
import requests

UPLOAD_URL = "https://open-music.example.com/submit"  # placeholder


def submit_data(data, url: str = UPLOAD_URL):
    try:  # pragma: no cover - network
        requests.post(url, json=data, timeout=5)
        logging.info("Project data submitted to Open Music Library")
    except Exception as e:  # pragma: no cover - network
        logging.warning("Failed to submit data: %s", e)
