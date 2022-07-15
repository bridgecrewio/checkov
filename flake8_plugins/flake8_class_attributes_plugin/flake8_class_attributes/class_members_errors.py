from __future__ import annotations

import ast
from typing import Any

FORBIDDEN_TYPES = {
    "field",
}
SKIP_SPECIAL_ATTRIBUTES = {
    "__code__",
    "__slots__",
}
SKIP_TYPING_CLASSES = {
    "Protocol",
    "TypedDict",
}


def get_class_members_errors(
    model_parts_info: list[dict[str, Any]], class_def: ast.ClassDef
) -> list[tuple[int, int, str]]:
    errors: list[tuple[int, int, str]] = []

    if skip_dataclasses(class_def):
        return errors
    if skip_typed_dicts(class_def):
        return errors
    for model_part in model_parts_info:
        if model_part['type'] in FORBIDDEN_TYPES:
            node_name = get_node_name(model_part['node'], model_part['type'])

            if node_name in SKIP_SPECIAL_ATTRIBUTES:
                continue

            errors.append((model_part['node'].lineno, model_part['node'].col_offset, f"CCE003 Class level {model_part['type']} '{node_name}' detected in class {model_part['model_name']}",))
    return errors


def skip_dataclasses(class_def: ast.ClassDef) -> bool:
    if class_def.decorator_list is not None:
        for decorator in class_def.decorator_list:
            if not isinstance(decorator, ast.Name):
                return True
            if decorator.id == 'dataclass':
                return True
    return False


def skip_typed_dicts(class_def: ast.ClassDef) -> bool:
    if class_def.bases:
        for base in class_def.bases:
            if not isinstance(base, ast.Name):
                return True
            if base.id in SKIP_TYPING_CLASSES:
                return True
    return False


def get_node_name(node, node_type: str):
    special_methods_names = (
        '__new__',
        '__init__',
        '__post_init__',
        '__str__',
        'save',
        'delete',
    )
    name_getters_by_type = [
        ('docstring', lambda n: 'docstring'),
        ('meta_class', lambda n: 'Meta'),
        ('constant', lambda n: n.target.id if isinstance(n, ast.AnnAssign) else n.targets[0].id),  # type: ignore
        ('field', get_name_for_field_node_type),
        (('method',) + special_methods_names, lambda n: n.name),
        ('nested_class', lambda n: n.name),
        ('expression', lambda n: '<class_level_expression>'),
        ('if', lambda n: 'if ...'),
    ]
    for type_postfix, name_getter in name_getters_by_type:
        if node_type.endswith(type_postfix):  # type: ignore
            return name_getter(node)


def get_name_for_field_node_type(node: ast.Assign | ast.AnnAssign) -> str:
    name = '<class_level_assignment>'
    if isinstance(node, ast.AnnAssign):
        name = node.target.id if isinstance(node.target, ast.Name) else name
    elif isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
    elif hasattr(node.targets[0], 'attr'):
        name = node.targets[0].attr  # type: ignore
    elif isinstance(node.targets[0], ast.Tuple):
        name = ', '.join([e.id for e in node.targets[0].elts if isinstance(e, ast.Name)])

    return name
