import re

from checkov.graph.terraform.utils.utils import INTERPOLATION_PATTERN
from checkov.graph.terraform.variable_rendering.safe_eval_functions import SAFE_EVAL_DICT

# condition ? true_val : false_val -> (condition, true_val, false_val)
CONDITIONAL_EXPR = r'([^\s]+)\?([^\s^\:]+)\:([^\s^\:]+)'

# {key1 = value1, key2 = value2, ...}
MAP_REGEX = r'\{(?:\s*[\S]+\s*\=\s*[\S]+\s*\,)+(?:\s*[\S]+\s*\=\s*[\S]+\s*)\}'

KEY_VALUE_REGEX = r'([\S]+)\s*\=\s*([\S]+)'

# %{ some_text }
DIRECTIVE_EXPR = r'\%\{([^\}]*)\}'

COMPARE_REGEX = re.compile(r'^(?P<a>.+)(?P<operator>==|!=|>=|>|<=|<|&&|\|\|)+(?P<b>.+)$')


def evaluate_terraform(input_str):
    evaluated_value = _try_evaluate(input_str)
    if type(evaluated_value) is not str:
        return input_str if callable(evaluated_value) else evaluated_value
    evaluated_value = evaluate_map(evaluated_value)
    evaluated_value = strip_double_quotes(evaluated_value)
    evaluated_value = evaluate_directives(evaluated_value)
    evaluated_value = evaluate_conditional_expression(evaluated_value)
    evaluated_value = evaluate_compare(evaluated_value)
    second_evaluated_value = _try_evaluate(evaluated_value)

    return evaluated_value if callable(second_evaluated_value) else second_evaluated_value


def _try_evaluate(input_str):
    try:
        return eval(input_str, {"__builtins__": None}, SAFE_EVAL_DICT) # nosec
    except Exception:
        try:
            return eval(f'"{input_str}"', {"__builtins__": None}, SAFE_EVAL_DICT) # nosec
        except Exception:
            return input_str


def replace_string_value(original_str, str_to_replace, replaced_value):
    if type(original_str) is list:
        for i, item in enumerate(original_str):
            original_str[i] = replace_string_value(item, str_to_replace, replaced_value)
            return original_str

    if str_to_replace not in original_str:
        return original_str

    string_without_interpolation = re.sub(INTERPOLATION_PATTERN, '', original_str)
    return string_without_interpolation.replace(str_to_replace, replaced_value)


def strip_double_quotes(input_str):
    if input_str.startswith('"') and input_str.endswith('"'):
        input_str = input_str[1:-1]
    return input_str


def evaluate_conditional_expression(input_str):
    conditions = re.findall(CONDITIONAL_EXPR, re.sub(r'\s', '', input_str))
    for condition in conditions:
        if len(condition) != 3:
            return input_str
        evaluated_condition = evaluate_terraform(condition[0])
        if convert_to_bool(evaluated_condition):
            return evaluate_terraform(condition[1])
        return evaluate_terraform(condition[2])
    return input_str


def evaluate_compare(input_str):
    """
    :param input_str: string like "a && b" (supported operators: ==, != , <, <=, >, >=, && , ||)
    :return: evaluation of the expression
    """
    if type(input_str) is str and re.search(COMPARE_REGEX, input_str) and 'for' not in input_str:
        compare_parts = re.search(COMPARE_REGEX, input_str).groupdict()
        a = compare_parts.get('a')
        b = compare_parts.get('b')
        op = compare_parts.get('operator')
        if a and b and op:
            try:
                return apply_binary_op(evaluate_terraform(a), evaluate_terraform(b), op)
            except TypeError or SyntaxError:
                return input_str

    return input_str


def apply_binary_op(a, b, operator):
    # apply the operator after verifying that a and b have the same type.
    operators = {
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>': lambda a, b: a > b,
        '>=': lambda a, b: a >= b,
        '<': lambda a, b: a < b,
        '<=': lambda a, b: a <= b,
        '&&': lambda a, b: a and b,
        '||': lambda a, b: a or b
    }
    type_a = type(a)
    type_b = type(b)

    if type_a != type_b:
        try:
            temp_b = type_a(b)
            if type_a == bool:
                temp_b = bool(convert_to_bool(b))
            return operators[operator](a, temp_b)
        except Exception:
            temp_a = type_b(a)
            if type_b == bool:
                temp_a = bool(convert_to_bool(a))
            return operators[operator](temp_a, b)
    else:
        return operators[operator](a, b)


def evaluate_directives(input_str):
    if re.search(DIRECTIVE_EXPR, input_str) is None:
        return input_str

    # replace `%{if <BOOL>}%{true_val}%{else}%{false_val}%{endif}` pattern with `<BOOL> ? true_val : false_val`
    matching_directives = re.findall(DIRECTIVE_EXPR, input_str)
    if len(matching_directives) == 3:
        if re.search(r'\bif\b', matching_directives[0]) and re.search(r'\belse\b', matching_directives[1]) and re.search(r'\bendif\b', matching_directives[2]):
            split_by_directives = re.split(DIRECTIVE_EXPR, input_str)
            edited_str = ''
            for part in split_by_directives:
                if re.search(r'\bif\b', part):
                    part = part.replace('if', '%{') + ' ? '
                    part = re.sub(r'\s', '', part)
                if re.search(r'\belse\b', part):
                    part = part.replace('else', ':')
                    part = re.sub(r'\s', '', part)
                if re.search(r'\bendif\b', part):
                    part = part.replace('endif', '}')
                    part = re.sub(r'\s', '', part)
                edited_str += part
            input_str = edited_str

    matching_directives = re.split(DIRECTIVE_EXPR, input_str)
    evaluated_string_parts = []
    for str_part in matching_directives:
        evaluated_string_parts.append(evaluate_terraform(str_part))
    return ''.join(evaluated_string_parts)


def evaluate_map(input_str):
    matching_maps = re.findall(MAP_REGEX, input_str)
    for matching_map in matching_maps:
        # replaced_matching_map = f'"{matching_map.replace("=", ":")}"'
        replaced_matching_map = matching_map.replace("=", ":")
        input_str = input_str.replace(matching_map, replaced_matching_map)
    return input_str


def convert_to_bool(bool_str):
    if bool_str in ['true', '"true"', 'True', '"True"', 1, '1']:
        return True
    elif bool_str in ['false', '"false"', 'False', '"False"', 0, '0']:
        return False
    else:
        return bool_str
