import yaml
from yaml.loader import SafeLoader

def loads(filename):
    """
    Load the given YAML string
    """
    template = None
    with open(filename, 'r') as stream:

        template = list(yaml.load_all(stream, Loader=SafeLineLoader))

    # Convert an empty file to an empty dict
    if template is None:
        template = {}

    return template


def load(filename):
    """
    Load the given YAML file
    """

    content = ''

    with open(filename) as fp:
        content = fp.read()
        fp.seek(0)
        file_lines = [(ind + 1, line) for (ind, line) in
                      list(enumerate(fp.readlines()))]

    template = loads(filename)

    return (template, file_lines)


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        #mapping['__line__'] = node.start_mark.line + 1
        mapping['__startline__'] = node.start_mark.line + 1
        mapping['__endline__'] = node.end_mark.line + 1
        return mapping