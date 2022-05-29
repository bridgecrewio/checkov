import ast


def get_model_parts_info(model_ast):
    parts_info = []
    for child_node in model_ast.body:
        node_type = get_model_node_type(child_node)
        parts_info.append({
            'model_name': model_ast.name,
            'node': child_node,
            'type': node_type
        })
    return parts_info


def get_model_node_type(child_node) -> str:
    direct_node_types_mapping = [
        (ast.If, lambda n: 'if'),
        (ast.Pass, lambda n: 'pass'),
        ((ast.Assign, ast.AnnAssign), lambda n: get_assighment_type(n)),
        ((ast.FunctionDef, ast.AsyncFunctionDef), lambda n: get_funcdef_type(n)),
        (ast.Expr, lambda n: 'docstring' if isinstance(n.value, ast.Str) else 'expression'),
        (ast.ClassDef, lambda n: 'meta_class' if child_node.name == 'Meta' else 'nested_class'),
    ]
    for type_or_type_tuple, type_getter in direct_node_types_mapping:
        if isinstance(child_node, type_or_type_tuple):  # type: ignore
            return type_getter(child_node)


def get_assighment_type(child_node) -> str:
    assignee_node = child_node.target if isinstance(child_node, ast.AnnAssign) else child_node.targets[0]
    assighment_type = 'field'
    if isinstance(assignee_node, ast.Subscript):
        assighment_type = 'expression'
    if isinstance(assignee_node, ast.Name) and is_caps_lock_str(assignee_node.id):
        assighment_type = 'constant'
    if isinstance(child_node.value, ast.Call):
        dump_callable = ast.dump(child_node.value.func)
        if (
            'ForeignKey' in dump_callable
            or 'ManyToManyField' in dump_callable
            or 'OneToOneField' in dump_callable
            or 'GenericRelation' in dump_callable
        ):
            assighment_type = 'outer_field'
    return assighment_type


def get_funcdef_type(child_node) -> str:
    special_methods_names = {
        '__new__',
        '__init__',
        '__post_init__',
        '__str__',
        'save',
        'delete',
    }
    decorator_names_to_types_map = {
        'property': 'property_method',
        'cached_property': 'property_method',
        'staticmethod': 'static_method',
        'classmethod': 'class_method',

        'private_property': 'private_property_method',
        'private_cached_property': 'private_property_method',
        'private_staticmethod': 'private_static_method',
        'private_classmethod': 'private_class_method',
    }
    for decorator_info in child_node.decorator_list:
        if (
            isinstance(decorator_info, ast.Name)
            and decorator_info.id in decorator_names_to_types_map
        ):

            if child_node.name.startswith('_'):
                return decorator_names_to_types_map[f'private_{decorator_info.id}']

            return decorator_names_to_types_map[decorator_info.id]
    funcdef_type = 'method'
    if child_node.name in special_methods_names:
        funcdef_type = child_node.name
    elif child_node.name.startswith('__') and child_node.name.endswith('__'):
        funcdef_type = 'magic_method'
    elif child_node.name.startswith('_'):
        funcdef_type = 'private_method'
    return funcdef_type


def is_caps_lock_str(var_name: str) -> bool:
    return var_name.upper() == var_name
