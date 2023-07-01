"""Main script."""

import re
from src.document_writer import DocumentWriter
from src.xml_handler import DiagramXMLHandler


def check_if_abstract(_class):
    abstract_ref = re.search(r' ?\{[Aa]bstract\}', _class.get('value'))
    if abstract_ref:
        _class['superclass_name'] = 'ABC'
        return True, _class['value'].replace(abstract_ref.group(0), '')

    return False, _class['value']


def set_attributes_and_methods(class_content: dict, diagram_handler: DiagramXMLHandler):
    attrib_regex = re.compile(r'\+ (\w+)\: ?(\w+)?')
    method_regex = re.compile(r'\+ (\w+)\(([\w\s\d\:\,\*]*)\)\: ?(\w+)?')
    params_regex = re.compile(r'(?:^|\, ?)(\w+)(?: ?\*)?(?:\: ?(\w+))?')

    for _, text_attributes in diagram_handler.iter_elements(class_content['id'], filter='text'):
        class_content['attributes'].extend(re.findall(attrib_regex, text_attributes.get('value')))
        _methods = re.findall(method_regex, text_attributes.get('value'))
        for _method in map(list, _methods):
            params = re.findall(params_regex, _method[1])
            _method[1] = params
            class_content['methods'].append(_method)


def find_in_class_list(id, class_list):
    return next((_class for _class in class_list if _class.get('id') == id), None)


def generate_class_list(diagram_handler: DiagramXMLHandler, page_id: str):
    class_list = []
    for class_id, _class in diagram_handler.iter_elements(page_id, filter='class'):
        is_abstract, name = check_if_abstract(_class)
        class_content = {
            'id': class_id,
            'name': name,
            'attributes': [],
            'methods': [],
            'is_abstract': is_abstract,
        }
        set_attributes_and_methods(class_content, diagram_handler)
        class_list.append(class_content)

    for _, link_attributes in diagram_handler.iter_elements(page_id, filter='link'):
        # Inheritance
        end_arrow = re.match(r'endArrow=(\w+);', link_attributes['style'])
        if end_arrow and end_arrow.group(1) == 'block':
            source = find_in_class_list(link_attributes['source'], class_list)
            target = find_in_class_list(link_attributes['target'], class_list)
            if source and target and target.get('name'):
                source['superclass_name'] = target['name']

    return class_list


def run():
    file_name = 'class-diagram-services-banking-drawio.xml'
    output_file = 'auto_generated_file{suffix}.py'

    diagram_handler = DiagramXMLHandler(file_name)

    count = 0
    for page_id, _ in diagram_handler.iter_elements():
        class_list = generate_class_list(diagram_handler, page_id)
        document_writer = DocumentWriter(class_list)

        file_suffix = f'_{count}' if count else ''
        with open(output_file.format(suffix=file_suffix), 'w') as file:
            file.write(document_writer.mount())
        count += 1


if __name__ == "__main__":
    run()
