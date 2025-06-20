import soundfile as sf


class Recorder:
    """Simple audio recorder to capture final output."""

    def __init__(self, fs: int = 44100):
        self.fs = fs
        self._file = None
        self._handle = None
        self.recording = False

    def start(self, filename: str) -> None:
        """Begin writing audio to ``filename``."""
        if self.recording:
            self.stop()
        self._file = filename
        self._handle = sf.SoundFile(
            filename, mode="w", samplerate=self.fs, channels=2
        )
        self.recording = True

    def write(self, data):
        """Append audio block if recording."""
        if self.recording and self._handle is not None:
            self._handle.write(data)

    def stop(self) -> None:
        """Stop recording and close file."""
        if self.recording and self._handle is not None:
            self._handle.close()
        self.recording = False
        self._handle = None
        self._file = None
