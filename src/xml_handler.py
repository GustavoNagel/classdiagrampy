"""XML Handler to get diagram root."""

import xml.etree.ElementTree as ET


class DiagramXMLHandler:
    """Implement methods that work in diagram root directly."""

    def __init__(self, file_path: str):
        tree = ET.parse(file_path)
        file_root = tree.getroot()
        self.diagram_root = file_root.find('./diagram/mxGraphModel/root')

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

    def iter_elements(self, element_ids, filter: str = None):
        for id in element_ids:
            element = self.find_elem_by_id(id)
            if not filter or eval(f'self.is_{filter}')(element):
                yield id, element.attrib
