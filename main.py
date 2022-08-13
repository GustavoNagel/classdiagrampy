"""Main script."""

import re
from src.document_writer import DocumentWriter
from src.graph import Graph
from src.xml_handler import DiagramXMLHandler


file_name = 'class-diagram-example-drawio.xml'
output_file = 'auto_generated_file.py'

diagram_handler = DiagramXMLHandler(file_name)
my_graph = Graph(
    edges=[
        (obj.attrib['parent'], obj.attrib['id'])
        for obj in diagram_handler.findall()
        if obj.attrib.get('parent')
    ],
    oriented=True,
)

attrib_regex = re.compile(r'\+ (\w+)\: (\w+)')
method_regex = re.compile(r'\+ (\w+)\(([\w\s\d\:\,\*]*)\)\: ?(\w+)')
params_regex = re.compile(r'(?:^|\, ?)(\w+)(?: ?\*)?(?:\: ?(\w+))?')

class_list = []
for class_id, _class in diagram_handler.iter_elements(my_graph['1'], filter='class'):
    class_content = {'id': class_id, 'name': _class.get('value'), 'attributes': [], 'methods': []}
    for _, text_attributes in diagram_handler.iter_elements(my_graph[class_id], filter='text'):
        class_content['attributes'].extend(re.findall(attrib_regex, text_attributes.get('value')))
        _methods = re.findall(method_regex, text_attributes.get('value'))
        for _method in map(list, _methods):
            params = re.findall(params_regex, _method[1])
            _method[1] = params
            class_content['methods'].append(_method)
    class_list.append(class_content)


def find_in_class_list(id, class_list):
    return next((_class for _class in class_list if _class.get('id') == id), None)


for _, link_attributes in diagram_handler.iter_elements(my_graph['1'], filter='link'):
    print('Found', link_attributes['source'], link_attributes['target'])
    end_arrow = re.match(r'endArrow=(\w+);', link_attributes['style']).group(1)
    if end_arrow == 'block':
        source = find_in_class_list(link_attributes['source'], class_list)
        target = find_in_class_list(link_attributes['target'], class_list)
        if source and target and target.get('name'):
            source['superclass_name'] = target['name']


document_writer = DocumentWriter(class_list)

with open(output_file, 'w') as file:
    file.write(document_writer.mount())

# if __name__ == "__main__":
