import os
import numpy as np
import soundfile as sf
from musica.recorder import Recorder


def test_record(tmp_path):
    rec = Recorder(44100)
    file_path = tmp_path / "out.wav"
    rec.start(str(file_path))
    rec.write(np.zeros((44100, 2)))
    rec.stop()
    assert file_path.exists()
    data, sr = sf.read(str(file_path))
    assert data.shape[0] == 44100
    assert sr == 44100
