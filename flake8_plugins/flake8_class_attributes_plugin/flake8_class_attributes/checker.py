import ast
from typing import Generator, Tuple, List

from . import __version__ as version
from . model_parts_info import get_model_parts_info
from . class_members_errors import get_class_members_errors


class ClassAttributesChecker:

    name = 'flake8-class-attributes'
    version = version
    options = None

    def __init__(self, tree, filename: str):
        self.filename = filename
        self.tree = tree

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            '--use-class-attributes-order-strict-mode',
            action='store_true',
            parse_from_config=True,
            help='Require more strict order of private class members',
        )
        parser.add_option(
            '--class-attributes-order',
            comma_separated_list=True,
            parse_from_config=True,
            help='Comma-separated list of class attributes to '
                 'configure order manually',
        )

    @classmethod
    def parse_options(cls, options: str) -> None:
        cls.options = options

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        classes = [n for n in ast.walk(self.tree) if isinstance(n, ast.ClassDef)]
        errors: List[Tuple[int, int, str]] = []

        for class_def in classes:
            model_parts_info = get_model_parts_info(class_def)
            errors += get_class_members_errors(model_parts_info, class_def)

        for lineno, col_offset, error_msg in errors:
            yield lineno, col_offset, error_msg, type(self)
