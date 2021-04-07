import re

from checkov.terraform.variable_rendering.safe_eval_functions import SAFE_EVAL_DICT
# condition ? true_val : false_val -> (condition, true_val, false_val)
from checkov.terraform.parser_utils import find_var_blocks

CONDITIONAL_EXPR = r'([^\?]+)\?([^:]+)\:([^:]+)'

# {key1 = value1, key2 = value2, ...}
MAP_REGEX = r'\{(?:\s*[\S]+\s*\=\s*[\S]+\s*\,)*(?:\s*[\S]+\s*\=\s*[\S]+\s*)\}'

# {key:val}[key]
MAP_WITH_ACCESS = re.compile(r'(?P<d>{(?:.*?:.*?)+(,?:.*?:.*?)*})\s*(?P<access>\[[^\]]+\])')

LIST_PATTERN = r'(?P<d>\[([^\[\]]+?)+(\,[^\[\]]+?)*\])'

KEY_VALUE_REGEX = r'([\S]+)\s*\=\s*([\S]+)'

# %{ some_text }
DIRECTIVE_EXPR = r'\%\{([^\}]*)\}'

COMPARE_REGEX = re.compile(r'^(?P<a>.+)(?P<operator>==|!=|>=|>|<=|<|&&|\|\|)+(?P<b>.+)$')


def evaluate_terraform(input_str, keep_interpolations=True):
    evaluated_value = _try_evaluate(input_str)
    if type(evaluated_value) is not str:
        return input_str if callable(evaluated_value) else evaluated_value
    evaluated_value = evaluated_value.replace("\n", "")
    evaluated_value = evaluated_value.replace(",,", ",")
    if not keep_interpolations:
        evaluated_value = remove_interpolation(evaluated_value)
    evaluated_value = evaluate_map(evaluated_value)
    evaluated_value = evaluate_list_access(evaluated_value)
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


def replace_string_value(original_str, str_to_replace, replaced_value, keep_origin=True):
    if original_str is None or type(original_str) not in (str, list):
        return original_str

    if type(original_str) is list:
        for i, item in enumerate(original_str):
            original_str[i] = replace_string_value(item, str_to_replace, replaced_value, keep_origin)
            if type(replaced_value) in [int, float, bool]:
                original_str[i] = evaluate_terraform(original_str[i])
            return original_str

    if str_to_replace not in original_str:
        return original_str if keep_origin else str_to_replace

    string_without_interpolation = remove_interpolation(original_str, str_to_replace)
    return string_without_interpolation.replace(str_to_replace, str(replaced_value)).replace(' ', '')


def remove_interpolation(original_str, var_to_clean: str=None):
    # get all variable references in string
    # remove from the string all ${} or '${}' occurrences
    var_blocks = find_var_blocks(original_str)
    var_blocks.reverse()
    for block in var_blocks:
        if block.full_str.startswith("${") and block.full_str.endswith("}") and (not var_to_clean or block.var_only == var_to_clean):
            full_str_start = original_str.find(block.full_str)
            full_str_end = full_str_start + len(block.full_str)
            if full_str_start > 0 and full_str_end <= len(original_str) - 2 and original_str[full_str_start-1] == "'" and original_str[full_str_start-1] == original_str[full_str_end] and "." in block.full_str:
                # checking if ${} is wrapped with '' like : '${}'
                original_str = original_str[:full_str_start-1] + block.full_str + original_str[full_str_end+1:]
            original_str = original_str.replace(block.full_str, block.var_only)
    return original_str


def strip_double_quotes(input_str):
    if input_str.startswith('"') and input_str.endswith('"'):
        input_str = input_str[1:-1]
    return input_str


def evaluate_conditional_expression(input_str):
    condition = re.match(CONDITIONAL_EXPR, input_str)
    while condition:
        groups = condition.groups()
        if len(groups) != 3:
            return input_str
        evaluated_condition = evaluate_terraform(groups[0])
        condition_substr = input_str[condition.start():condition.end()]
        if convert_to_bool(evaluated_condition):
            true_val = str(evaluate_terraform(groups[1]))
            input_str = input_str.replace(condition_substr, true_val)
        else:
            false_val = str(evaluate_terraform(groups[2]))
            input_str = input_str.replace(condition_substr, false_val)
        condition = re.match(CONDITIONAL_EXPR, input_str)

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
    # first replace maps ":" with "="
    all_curly_brackets = find_brackets_pairs(input_str, "{", "}")
    for curly_match in all_curly_brackets:
        curly_start = curly_match["start"]
        curly_end = curly_match["end"]
        replaced_matching_map = input_str[curly_start:curly_end+1].replace("=", ":")
        input_str = input_str.replace(input_str[curly_start:curly_end+1], replaced_matching_map)

    # find map access like {a: b}[a] and extract the right value - b
    all_square_brackets = find_brackets_pairs(input_str, "[", "]")

    curr_square_match = 0
    for curly_match in all_curly_brackets:
        curly_start = curly_match["start"]
        curly_end = curly_match["end"]
        for i in range(curr_square_match, len(all_square_brackets)):
            curr_square_match = i
            square_match = all_square_brackets[i]
            square_start = square_match["start"]
            square_end = square_match["end"]
            if square_start > curly_end and (square_start == curly_end + 1 or all(c == ' ' for c in input_str[curly_end + 1:square_start])):
                origin_match_str = input_str[curly_start:square_end + 1]
                map_access = input_str[square_start+1:square_end]
                if not map_access.startswith('"') and not map_access.endswith('"'):
                    origin_match_str = origin_match_str.replace(f'[{map_access}]', f'["{map_access}"]')
                evaluated = _try_evaluate(origin_match_str)
                if evaluated:
                    input_str = input_str.replace(input_str[curly_start:square_end + 1], str(evaluated))
                    break

    return input_str


def convert_to_bool(bool_str):
    if bool_str in ['true', '"true"', 'True', '"True"', 1, '1']:
        return True
    elif bool_str in ['false', '"false"', 'False', '"False"', 0, '0']:
        return False
    else:
        return bool_str


def evaluate_list_access(input_str):
    # find list access like [a, b, c][0] and extract the right value - a

    all_square_brackets = find_brackets_pairs(input_str, "[", "]")
    prev_start = -1
    prev_end = -1
    for match in all_square_brackets:
        if (match["start"] == prev_end + 1 or all(c == ' ' for c in input_str[prev_end+1:match["start"]])) and prev_start != -1:
            curr_str = input_str[match["start"]+1:match["end"]]
            if curr_str.isnumeric():
                evaluated = _try_evaluate(input_str[prev_start:match["end"]+1])
                if evaluated:
                    input_str = input_str.replace(input_str[prev_start:match["end"]+1], str(evaluated))
        prev_start = match["start"]
        prev_end = match["end"]

    return input_str


def find_brackets_pairs(input_str, starting, closing):
    brackets_pairs = [-1] * len(input_str)
    unmatched_open = []

    for i, c in enumerate(input_str):
        if c == starting:
            unmatched_open.append(i)
        elif c == closing and len(unmatched_open) > 0:
            brackets_pairs[unmatched_open[-1]] = i
            unmatched_open = unmatched_open[:-1]

    all_brackets = []
    for start, end in enumerate(brackets_pairs):
        if end != -1:
            all_brackets.append({"start": start, "end": end})
    return all_brackets
