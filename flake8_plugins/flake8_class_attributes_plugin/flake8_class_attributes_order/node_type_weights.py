import warnings

from typing import List, Mapping, Dict
from typing_extensions import Final


NON_STRICT_NODE_TYPE_WEIGHTS: Final[Mapping[str, int]] = {
    'docstring': 0,
    'pass': 1,
    'meta_class': 2,
    'nested_class': 3,

    'constant': 4,
    'field': 5,
    'outer_field': 6,

    'if': 7,
    'expression': 8,

    '__new__': 9,
    '__init__': 10,
    '__post_init__': 11,
    '__str__': 12,

    'save': 13,
    'delete': 14,

    'property_method': 20,
    'private_property_method': 20,
    'static_method': 22,
    'private_static_method': 22,
    'class_method': 24,
    'private_class_method': 24,
    'method': 26,
    'magic_method': 27,
    'private_method': 27,
}

STRICT_NODE_TYPE_WEIGHTS: Final[Mapping[str, int]] = {
    'docstring': 0,
    'pass': 1,
    'meta_class': 2,
    'nested_class': 3,

    'constant': 4,
    'field': 5,
    'outer_field': 6,

    'if': 7,
    'expression': 8,

    '__new__': 9,
    '__init__': 10,
    '__post_init__': 11,
    '__str__': 12,

    'save': 13,
    'delete': 14,

    'property_method': 20,
    'private_property_method': 21,
    'static_method': 22,
    'private_static_method': 23,
    'class_method': 24,
    'private_class_method': 25,
    'method': 26,
    'magic_method': 27,
    'private_method': 28,
}

FIXED_NODE_TYPE_WEIGHTS: Final[Dict[str, int]] = {
    'docstring': 0,
    'pass': 1,
    'expression': 2,
    'if': 3,
}

CONFIGURABLE_NODE_TYPES: Final[Mapping[str, List[str]]] = {
    'nested_class': ['nested_class'],
    'meta_class': ['meta_class', 'nested_class'],

    'field': ['field'],
    'constant': ['constant', 'field'],
    'outer_field': ['outer_field', 'field'],

    'method': ['method'],
    'magic_method': ['magic_method', 'method'],
    '__new__': ['__new__', 'magic_method', 'method'],
    '__init__': ['__init__', 'magic_method', 'method'],
    '__post_init__': ['__post_init__', 'magic_method', 'method'],
    '__str__': ['__str__', 'magic_method', 'method'],

    'private_method': ['private_method', 'method'],

    'save': ['save', 'method'],
    'delete': ['delete', 'method'],

    'property_method': ['property_method', 'method'],
    'private_property_method': ['private_property_method', 'property_method', 'method'],
    'static_method': ['static_method', 'method'],
    'private_static_method': ['private_static_method', 'static_method', 'method'],
    'class_method': ['class_method', 'method'],
    'private_class_method': ['private_class_method', 'class_method', 'method'],
}


def get_node_weights(options=None) -> Mapping[str, int]:
    use_strict_mode = bool(options.use_class_attributes_order_strict_mode)
    class_attributes_order = options.class_attributes_order

    if use_strict_mode and class_attributes_order:
        warnings.warn(
            'Both options that are exclusive provided: --use-class-attributes-order-strict-mode '
            'and --class-attributes-order. Order defined in --class-attributes-order will be used '
            'to check against.',
            Warning,
        )

    if class_attributes_order:
        node_type_weights = FIXED_NODE_TYPE_WEIGHTS.copy()
        node_to_configured_weight = {
            node_type: weight for weight, node_type in enumerate(
                class_attributes_order,
                start=len(node_type_weights))
        }

        for node_type, node_type_path in CONFIGURABLE_NODE_TYPES.items():
            for node_type_or_supertype in node_type_path:
                if node_type_or_supertype in node_to_configured_weight:
                    node_type_weights[node_type] = node_to_configured_weight[node_type_or_supertype]
                    break

        return node_type_weights

    if use_strict_mode:

        return STRICT_NODE_TYPE_WEIGHTS

    return NON_STRICT_NODE_TYPE_WEIGHTS
