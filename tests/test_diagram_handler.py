"""Test Diagram XML Handler."""

import os
from typing import Generator
import xml.etree.ElementTree as ET

import pytest
from collections import defaultdict
from src.graph import Graph
from src.xml_handler import DiagramXMLHandler


@pytest.fixture
def element(autouse=True):
    class Element:
        def __init__(self, attrib):
            self.attrib = attrib or {}
    return Element


class TestDiagramXMLHandler:

    @pytest.fixture
    def handler(autouse=True):
        return DiagramXMLHandler(file_path='tests/files/class-diagram-example-drawio.xml')

    def test_handler_init(self, handler, mocker):
        assert handler.graph.root == '0'
        assert isinstance(handler.diagram_root, ET.Element)

    def test_iter_elements(self, handler, mocker):
        result = handler.iter_elements()
        assert isinstance(result, Generator)
        assert next(result) == ('1', {'id': '1', 'parent': '0'})
        with pytest.raises(StopIteration):
            next(result)

        assert next(handler.iter_elements(source_element='1', filter='class'))[0] == '41fe28ffb9dbdb2c-1'
        assert len([
            obj for obj, _ in handler.iter_elements(
                source_element='41fe28ffb9dbdb2c-1',
                filter='text',
            )
            if obj in ['41fe28ffb9dbdb2c-2', '41fe28ffb9dbdb2c-4']
        ]) == 2
