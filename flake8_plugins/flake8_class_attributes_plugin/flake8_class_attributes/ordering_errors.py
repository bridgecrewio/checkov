import ast
from typing import Tuple, List, Union


def get_ordering_errors(model_parts_info) -> List[Tuple[int, int, str]]:
    errors = []
    for model_part, next_model_part in zip(model_parts_info, model_parts_info[1:] + [None]):
        if (
            next_model_part
            and model_part['model_name'] == next_model_part['model_name']
            and model_part['weight'] > next_model_part['weight']
        ):
            errors.append((
                model_part['node'].lineno,
                model_part['node'].col_offset,
                'CCE001 {0}.{1} should be after {0}.{2}'.format(
                    model_part['model_name'],
                    get_node_name(model_part['node'], model_part['type']),
                    get_node_name(next_model_part['node'], next_model_part['type']),
                ),
            ))
        if model_part['type'] in ['expression', 'if']:
            errors.append((
                model_part['node'].lineno,
                model_part['node'].col_offset,
                'CCE002 Class level expression detected in class {0}, line {1}'.format(
                    model_part['model_name'],
                    model_part['node'].lineno,
                ),
            ))
    return errors


def get_class_members_errors(model_parts_info) -> List[Tuple[int, int, str]]:
    errors = []
    forbidden_types = ['field']
    for model_part in model_parts_info:
        if model_part['type'] in forbidden_types:
            node_name = get_node_name(model_part['node'], model_part['type'])
            errors.append((
                    model_part['node'].lineno,
                    model_part['node'].col_offset,
                    f"CCE003 Class level {model_part['type']} '{node_name}' detected in class {model_part['model_name']}",
                ))
    return errors


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


def get_name_for_field_node_type(node: Union[ast.Assign, ast.AnnAssign]) -> str:
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
