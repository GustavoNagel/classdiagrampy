"""Test Basic Graph."""

import pytest
from collections import defaultdict
from src.graph import Graph


class TestBasicGraph:

    @pytest.fixture
    def fake_edges(self, autouse=True):
        return [('A', 'B'), ('B', 'C'), ('B', 'D'), ('C', 'E'), ('C', 'F')]

    @pytest.fixture
    def testing_graph(self, fake_edges, autouse=True):
        return Graph(fake_edges)

    def test_empty_init(self, mocker):
        mocked_add_edges = mocker.patch.object(Graph, 'add_edges')
        graph = Graph()
        assert getattr(graph, 'oriented') is False
        assert isinstance(getattr(graph, '_graph_dict'), defaultdict)
        mocked_add_edges.assert_called_with([])

    def test_init_from_edges(self, mocker, fake_edges):
        mocked_add_edges = mocker.patch.object(Graph, 'add_edges')
        graph = Graph(edges=fake_edges.copy(), oriented=True)
        assert getattr(graph, 'oriented') is True
        assert isinstance(getattr(graph, '_graph_dict'), defaultdict)
        mocked_add_edges.assert_called_with(fake_edges)

    def test_get_edges_and_vertices(self, testing_graph):
        all_edges = testing_graph.get_all_edges()
        assert ('A', 'B') in all_edges and ('B', 'A') in all_edges
        assert testing_graph.get_all_vertices() == {'A', 'B', 'C', 'D', 'E', 'F'}
        assert len(all_edges) == 10
        assert testing_graph['C'] == {'B', 'E', 'F'}

    def test_add_edges(self, testing_graph):
        assert len(testing_graph.get_all_edges()) == 10
        assert 'G' not in testing_graph.get_all_vertices()
        assert len(testing_graph) == 6
        testing_graph.add_edges([('A', 'F'), ('F', 'G')])
        assert len(testing_graph.get_all_edges()) == 14
        assert 'G' in testing_graph.get_all_vertices()
        assert len(testing_graph) == 7

    def test_iter(self, testing_graph):
        vertices = 'ABCDEF'
        for vertex in testing_graph:
            vertices = vertices.replace(vertex, '')
        assert not vertices
