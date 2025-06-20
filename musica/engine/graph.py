from __future__ import annotations

from typing import List, Set

from .node import AudioNode

class AudioGraph:
    """Manage a graph of audio nodes and run them in topological order."""

    def __init__(self, output_node: AudioNode):
        self.output_node = output_node
        self.nodes: List[AudioNode] = []
        self._sorted_nodes: List[AudioNode] = []

    def build_graph(self) -> None:
        visited: Set[AudioNode] = set()
        order: List[AudioNode] = []

        def visit(node: AudioNode) -> None:
            if node in visited:
                return
            visited.add(node)
            for inp in node.inputs:
                visit(inp)
            order.append(node)

        visit(self.output_node)
        self.nodes = list(visited)
        self._sorted_nodes = order

    def process_graph(self, block_size: int):
        if not self._sorted_nodes:
            self.build_graph()
        for node in self._sorted_nodes:
            node.process(block_size)
        return self.output_node.buffer
