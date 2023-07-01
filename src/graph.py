"""Basic Graph.

This structure consists of "nodes" called "vertices".
Nodes are connected with one another by edges.
"""

from collections import defaultdict


class Graph:
    """Basic Graph.

    :edges: a list of edges to use in graph creation.
    :oriented: flag for graph which orientation matters.
    """

    def __init__(self, edges: list[tuple] | None = None, oriented: bool = False):
        self._graph_dict = defaultdict(set)
        self.oriented = oriented
        self.add_edges(edges or [])

    def get_all_vertices(self) -> set:
        return set(self._graph_dict.keys())

    def get_all_edges(self) -> list[tuple]:
        return [
            (source, target)
            for source in self._graph_dict.keys() for target in self._graph_dict[source]
        ]

    def add_edges(self, edges: list[tuple]):
        for source, target in edges:
            self.add_edge(source, target)

    def add_edge(self, source: str, target: str):
        """Generate a link between two vertices."""
        self._graph_dict[source].add(target)
        if not self.oriented:
            self._graph_dict[target].add(source)

    def __len__(self):
        return len(self._graph_dict)

    def __iter__(self):
        self._iter_obj = iter(dict(self._graph_dict))
        return self._iter_obj

    def __next__(self):
        return next(self._iter_obj)

    def __str__(self):
        return f'{self.__class__.__name__}({dict(self._graph_dict)})'

    def __getitem__(self, vertex: str) -> set:
        return self._graph_dict[vertex]


class RootedTreeGraph(Graph):
    """Rooted Tree Graph.

    :edges: a list of edges to use in rooted tree graph creation.
    """

    def __init__(self, edges):
        super().__init__(edges, oriented=True)

    @property
    def root(self):
        return self._get_root()

    def _get_root(self):
        vertices = self.get_all_vertices()
        target_vertices = set()
        for elem in self._graph_dict.values():
            target_vertices.update(elem)
        root = vertices - target_vertices
        return next(iter(root)) if len(root) == 1 else None
