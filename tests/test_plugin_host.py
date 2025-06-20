import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
import numpy as np
from musica.engine import AudioGraph, SineNode, MixerNode, OutputNode, PluginHostNode

class DummyOutput(OutputNode):
    def __init__(self, fs=44100):
        super().__init__(fs, start_stream=False)
        self.written = []
    def process(self, block_size:int):
        inp = self.inputs[0].buffer if self.inputs else np.zeros((block_size,2))
        self.buffer = inp
        self.written.append(inp.copy())

def test_plugin_host_passthrough():
    sine = SineNode(440.0, fs=100)
    host = PluginHostNode("/nonexistent/plugin.vst3", fs=100, block_size=100)
    out = DummyOutput(fs=100)
    host.connect(sine)
    out.connect(host)
    graph = AudioGraph(out)
    graph.build_graph()
    buf = graph.process_graph(100)
    expected = np.sin(2*np.pi*440*np.arange(100)/100)
    assert np.allclose(buf[:,0], expected, atol=1e-6)
