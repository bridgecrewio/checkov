import yaml


def loads(filename):
    """
    Load the given YAML string
    """
    template = None
    with open(filename, 'r') as stream:
        template = yaml.load(stream, Loader=yaml.FullLoader)
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

    if template:
        template["__startline__"] = 1
        template["__endline__"] = len(file_lines)

    return (template, file_lines)
