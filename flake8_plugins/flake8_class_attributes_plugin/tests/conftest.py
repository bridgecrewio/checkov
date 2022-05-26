import ast
import os

from flake8.options.manager import OptionManager

from flake8_plugins.flake8_class_attributes_plugin.flake8_class_attributes.checker import ClassAttributesChecker


def run_validator_for_test_file(filename, max_annotations_complexity=None,
                                strict_mode=False, attributes_order=None):
    test_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'test_files',
        filename,
    )
    with open(test_file_path, 'r') as file_handler:
        raw_content = file_handler.read()
    tree = ast.parse(raw_content)

    options = OptionManager('flake8_class_attributes_order', '0.1.3')
    options.use_class_attributes_order_strict_mode = strict_mode
    options.class_attributes_order = attributes_order
    ClassAttributesChecker.parse_options(options)

    checker = ClassAttributesChecker(tree=tree, filename=filename)
    if max_annotations_complexity:
        checker.max_annotations_complexity = max_annotations_complexity

    return list(checker.run())
