"""Writer Classes."""


class BaseWriter:
    """Base Writer."""

    required_imports = {}

    def generate_indent(self, n: int) -> str:
        return n * 4 * ' '

    def merge_imports(self, imports):
        for key, value in imports.items():
            self.required_imports.setdefault(key, set()).union(value)

    def recognize_type(self, type_name: str) -> str:
        if not type_name:
            return None
        elif type_name in ('date', 'datetime'):
            self.required_imports.setdefault('datetime', set()).add(type_name)
            return type_name

        if type_name in ('integer', 'string'):
            type_name = type_name[:3]
        try:
            eval(type_name)
        except NameError:
            return None

        return type_name


class DocstringWriter(BaseWriter):
    """Docstring Writer."""

    def __init__(self, multi_line_format: bool = False):
        super().__init__()
        self.multi_line_format = multi_line_format

    default_description = 'Default Docstring.'
    default_indent = {
        'module': 0,
        'class': 1,
        'method': 2,
    }

    def get_one_line_doc(self, indent: int):
        return f'{self.generate_indent(indent)}"""{self.default_description}"""'

    def get_multi_line_doc(self, indent: int):
        _indent = self.generate_indent(indent)
        return f'{_indent}"""\n{_indent}{self.default_description}\n{_indent}"""'

    def get_doc(self, indent: int, multi_line_format: bool = False):
        if not multi_line_format and not self.multi_line_format:
            return self.get_one_line_doc(indent)
        else:
            return self.get_multi_line_doc(indent)

    def get_class_doc(self):
        return self.get_doc(self.default_indent['class'])

    def get_module_doc(self):
        return self.get_doc(self.default_indent['module'])

    def get_method_doc(self):
        return self.get_doc(self.default_indent['method'])


class MethodWriter(BaseWriter):
    """Method Writer."""

    name = ''
    return_type = ''
    params = []

    def _mount_return(self):
        return f' -> {self.return_type}' if self.return_type else ''

    def _mount_params(self):
        prefix, params_text = '', ''
        for param_name, param_type in self.params:
            param_type_text = ''
            if param_type:
                param_type_text = f': {param_type}'
            params_text = f'{params_text}{prefix}{param_name}{param_type_text}'
            if not prefix:
                prefix = ', '
        return params_text

    def __init__(
        self,
        name: str,
        params: list[tuple],
        return_type: str,
        docstring_writer: DocstringWriter = None,
    ):
        super().__init__()
        self.docstring = (docstring_writer or DocstringWriter()).get_method_doc()
        self.name = name
        self.params = list(
            (param_name, self.recognize_type(param_type))
            for param_name, param_type in params
        )
        self.return_type = self.recognize_type(return_type)

    def mount(self):
        return f'{self.generate_indent(1)}def {self.name}({self._mount_params()})' \
               f'{self._mount_return()}:\n{self.docstring}'


class ClassWriter(BaseWriter):
    """Class Writer."""

    name = ''
    superclass_name = ''

    def __init__(
        self,
        name: str,
        attributes: list[str],
        methods: list[tuple],
        docstring_writer: DocstringWriter = None,
        **kwargs,
    ):
        super().__init__()
        self.name = name
        self.attributes = list(
            (attribute_name, self.recognize_type(attribute_type))
            for attribute_name, attribute_type in attributes
        )
        self.methods = methods
        self.docstring_writer = docstring_writer or DocstringWriter()
        self.docstring = self.docstring_writer.get_class_doc()
        if kwargs.get('is_abstract'):
            self.superclass_name = 'ABC'
            self.required_imports.setdefault('abc', set()).add('ABC')
        else:
            self.superclass_name = kwargs.get('superclass_name') or ''

    def _mount_methods(self):
        methods_text = ''
        for method in self.methods:
            method_writer = MethodWriter(*method, docstring_writer=self.docstring_writer)
            methods_text = f'{methods_text}\n{method_writer.mount()}\n'
            self.merge_imports(method_writer.required_imports)

        return methods_text

    def get_attribute_default_value(self, type_description):
        return {
            'int': ' = 0',
            'float': ' = 0.0',
            'str': " = ''",
            'dict': ' = {}',
            'list': ' = []',
            'set': ' = set()',
            'bool': ' = False',
            'date': ': date | None = None',
            'datetime': ': datetime | None = None',
        }.get(type_description) or ' = None'

    def _mount_attributes(self):
        attributes_text = '\n'.join([
            f'{self.generate_indent(1)}{attrib}{self.get_attribute_default_value(attrib_type)}'
            for attrib, attrib_type in self.attributes
        ])
        return f'\n{attributes_text}\n' if attributes_text else ''

    def _mount_superclass(self):
        return f'({self.superclass_name})' if self.superclass_name else ''

    def mount(self):
        return f'class {self.name}{self._mount_superclass()}:\n{self.docstring}\n' \
               f'{self._mount_attributes()}{self._mount_methods()}'


class ImportWriter(BaseWriter):
    """Import Writer."""

    def _mount_imports(self):
        imports_text = ''
        for module_path, entities in self.required_imports.items():
            if entities:
                imports_text = f'{imports_text}\nfrom {module_path} import {", ".join(entities)}'
            else:
                imports_text = f'{imports_text}\nimport {module_path}'
        return imports_text

    def mount(self):
        imports = self._mount_imports()
        return f'{imports}\n' if imports else ''


class DocumentWriter(BaseWriter):
    """Document Writer.

    Responsible for organizing and managing classes and imports.
    Always should use this order:

    1. Docstring Module
    2. PythonImports
    3. OrderedClasses
    """

    docstring_writer = DocstringWriter(multi_line_format=True)
    import_writer = ImportWriter()

    def __init__(self, class_list: list[dict]):
        super().__init__()
        self.classes = class_list
        self.docstring = self.docstring_writer.get_module_doc()

    def _mount_classes(self):
        classes_text = ''
        for _class in self.classes:
            class_writer = ClassWriter(**_class, docstring_writer=self.docstring_writer)
            classes_text = f'{classes_text}\n\n{class_writer.mount()}'
            self.merge_imports(class_writer.required_imports)

        self.import_writer.merge_imports(self.required_imports)
        return classes_text

    def mount(self):
        classes = self._mount_classes()
        return f'{self.docstring}\n{self.import_writer.mount()}{classes}'
