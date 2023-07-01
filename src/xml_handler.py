"""XML Handler to get diagram root."""

import xml.etree.ElementTree as ET
from src.graph import RootedTreeGraph


class DiagramXMLHandler:
    """Implement methods that work in diagram root directly."""

    def __init__(self, file_path: str):
        tree = ET.parse(file_path)
        file_root = tree.getroot()
        self.diagram_root = file_root.find('./diagram/mxGraphModel/root')
        self.graph = self.get_graph()

    def get_edges(self):
        return [
            (obj.attrib['parent'], obj.attrib['id'])
            for obj in self.findall()
            if obj.attrib.get('parent')
        ]

    def get_graph(self):
        return RootedTreeGraph(edges=self.get_edges())

    def find_elem_by_id(self, id: str):
        return self.diagram_root.find(f"./mxCell[@id='{id}']")

    def findall(self):
        return self.diagram_root.findall('mxCell')

    def is_class(self, element):
        return element.attrib.get('style') and element.attrib['style'].startswith('swimlane')

    def is_text(self, element):
        return element.attrib.get('style') and element.attrib['style'].startswith('text')

    def is_link(self, element):
        return all(element.attrib.get(attrib_name) for attrib_name in ('source', 'target'))

    def iter_elements(self, source_element: str = None, filter: str = None):
        for id in self.graph[source_element or self.graph.root]:
            element = self.find_elem_by_id(id)
            if not filter or eval(f'self.is_{filter}')(element):
                yield id, element.attrib

