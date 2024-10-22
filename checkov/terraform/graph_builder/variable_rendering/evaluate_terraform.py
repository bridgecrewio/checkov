from __future__ import annotations

import ast
import json
import logging
import os
import re
from typing import Any, Union, Optional, List, Dict, Callable, TypeVar, Tuple

from checkov.common.util.type_forcers import force_int
from checkov.common.util.parser_utils import find_var_blocks
import checkov.terraform.graph_builder.variable_rendering.renderer as renderer
from checkov.terraform.graph_builder.variable_rendering.safe_eval_functions import evaluate

T = TypeVar("T", str, int, bool)

# %{ some_text }
DIRECTIVE_EXPR = re.compile(r"\%\{([^\}]*)\}")

# exclude "']" one the right side of the compare via (?!']), this can happen with a base64 encoded string
COMPARE_REGEX = re.compile(r"^(?P<a>.+?)\s*(?P<operator>==|!=|>=|>|<=|<|&&|\|\|)\s*(?P<b>(?!']).+)$")
COMPARE_OPERATORS = (" == ", " != ", " < ", " <= ", " > ", " >= ", " && ", " || ")

CHECKOV_RENDER_MAX_LEN = force_int(os.getenv("CHECKOV_RENDER_MAX_LEN", "10000"))


def evaluate_terraform(input_str: Any, keep_interpolations: bool = True) -> Any:
    if input_str is None or isinstance(input_str, int):
        # no need for further evaluation
        return input_str

    if isinstance(input_str, str) and CHECKOV_RENDER_MAX_LEN and 0 < CHECKOV_RENDER_MAX_LEN < len(input_str):
        logging.debug(f'Rendering was skipped for a {len(input_str)}-character-long string. If you wish to have it '
                      f'evaluated, please set the environment variable CHECKOV_RENDER_MAX_LEN '
                      f'to {str(len(input_str) + 1)} or to 0 to allow rendering of any length')
        return input_str
    evaluated_value = _try_evaluate(input_str)
    if type(evaluated_value) is not str:
        return input_str if callable(evaluated_value) else evaluated_value
    evaluated_value = evaluated_value.replace("\n", "")
    evaluated_value = evaluated_value.replace(",,", ",")

    # if we try to strip interpolations but that does not help evaluation, then we should add them back in the case that
    # the interpolated string is part of a substring, so it can be identified by the "is_variable_dependent" method.
    # For example, the value "abc-${var.x}-xyz" will not be identified as a variable if we remove the interpolation
    # However, if the full value is just an interpolated variable, like ${var.xyz}, then we can leave them off, because
    # it won't affect that method and breaks certain policies and other logic that was written in a specific way
    value_before_removing_interpolations = evaluated_value
    if not keep_interpolations:
        evaluated_value = remove_interpolation(evaluated_value)
    if '${' + evaluated_value + '}' == value_before_removing_interpolations:
        value_before_removing_interpolations = evaluated_value
    value_after_removing_interpolations = evaluated_value

    evaluated_value = evaluate_map(evaluated_value)
    evaluated_value = evaluate_list_access(evaluated_value)
    evaluated_value = strip_double_quotes(evaluated_value)
    evaluated_value = evaluate_directives(evaluated_value)
    evaluated_value = strip_interpolation_marks(evaluated_value)
    evaluated_value = evaluate_conditional_expression(evaluated_value)
    evaluated_value = evaluate_compare(evaluated_value)
    evaluated_value = evaluate_json_types(evaluated_value)
    evaluated_value = handle_for_loop(evaluated_value)
    second_evaluated_value = _try_evaluate(evaluated_value)

    if callable(second_evaluated_value):
        return evaluated_value
    elif not keep_interpolations and second_evaluated_value == value_after_removing_interpolations:
        return value_before_removing_interpolations
    else:
        second_evaluated_value = _eval_merge_as_list(second_evaluated_value)
        return second_evaluated_value


def _eval_merge_as_list(eval_value: Any) -> Any:
    """
    Edge case for an eval in eval.
    UT for this: test_jsonpath_equals_ecs_with_merge
    """
    if eval_value and isinstance(eval_value, list) and isinstance(eval_value[0], str) and eval_value[0].startswith('merge'):
        return _try_evaluate(eval_value[0])
    return eval_value


def _try_evaluate(input_str: Union[str, bool]) -> Any:
    try:
        return evaluate(input_str)  # type:ignore[arg-type]
    except Exception:
        try:
            return evaluate(f'"{input_str}"')
        except Exception:
            try:
                # Sometimes eval can fail on correct terraform input like 'true'/'false',
                # as python's values are with capital T/F.
                # However, json does know how to handle it, so we use it instead.
                if isinstance(input_str, str):
                    return json.loads(input_str)
                return input_str
            except Exception:
                return input_str


def replace_string_value(original_str: Any, str_to_replace: str, replaced_value: str, keep_origin: bool = True) -> Any:
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

    string_without_interpolation = remove_interpolation(original_str, str_to_replace, escape_unrendered=False)
    return string_without_interpolation.replace(str_to_replace, str(replaced_value))


def _string_changed_except_interpolation(str_before: str, str_after: str) -> bool:
    return abs(len(str_before) - len(str_after)) != 3


def _find_new_value_for_interpolation(origin_str: str, str_to_replace: str, new_value: str) -> str:
    """
    This function checks whether we should escape the interpolated value, to avoid syntax error.
    Example:
        origin_str = "${lookup({'a': ${local.protocol1}},\"a\",\"https\")}"
        If we don't escape local.protocol1, the lookup function will fail, i.e -
          invalid - ${lookup({'a': local.protocol1},\"a\",\"https\")}
          valid - ${lookup({'a': 'local.protocol1'},\"a\",\"https\")}
    Default to return is new_value
    """
    try:
        # First part - checking if not-escaped is valid.
        not_escaped = origin_str.replace(str_to_replace, new_value)
        first_evaluated = evaluate_terraform(not_escaped)
        if _string_changed_except_interpolation(not_escaped, first_evaluated):
            # checking if the len difference != 3 checks if we didn't only remove the '${}'
            return new_value
        second_evaluated = _try_evaluate(first_evaluated)
        if first_evaluated != second_evaluated and _string_changed_except_interpolation(not_escaped, second_evaluated):
            return new_value

        # Second part - checking if escaped is valid
        escaped_new_value = f"'{new_value}'"
        escaped = origin_str.replace(str_to_replace, escaped_new_value)
        first_evaluated = evaluate_terraform(escaped)
        if escaped != first_evaluated and _string_changed_except_interpolation(escaped, first_evaluated):
            return escaped_new_value
        second_evaluated = _try_evaluate(first_evaluated)
        if first_evaluated != second_evaluated:
            return escaped_new_value
        else:
            return new_value
    except Exception:
        return new_value


def remove_interpolation(original_str: str, var_to_clean: Optional[str] = None, escape_unrendered: bool = True) -> str:
    # get all variable references in string
    # remove from the string all ${} or '${}' occurrences
    var_blocks = find_var_blocks(original_str)
    var_blocks.reverse()
    for block in var_blocks:
        if (
            block.full_str.startswith("${")
            and block.full_str.endswith("}")
            and (not var_to_clean or block.var_only == var_to_clean)
        ):
            full_str_start = original_str.find(block.full_str)
            full_str_end = full_str_start + len(block.full_str)
            if (
                full_str_start > 0
                and full_str_end <= len(original_str) - 2
                and original_str[full_str_start - 1] == "'"
                and original_str[full_str_start - 1] == original_str[full_str_end]
                and "." in block.full_str
            ):
                # checking if ${} is wrapped with '' like : '${}'
                original_str = original_str[:full_str_start - 1] + block.full_str + original_str[full_str_end + 1:]
                if escape_unrendered:
                    block.var_only = f"'{block.var_only}'"
                else:
                    block.var_only = _find_new_value_for_interpolation(original_str, block.full_str, block.var_only)
            original_str = original_str.replace(block.full_str, block.var_only)
    return original_str


def strip_double_quotes(input_str: str) -> str:
    if input_str.startswith('"') and input_str.endswith('"'):
        input_str = input_str[1:-1]
    return input_str


def strip_interpolation_marks(input_str: str) -> str:
    if input_str.startswith("${") and input_str.endswith("}"):
        # remove the needed char length of the interpolation marks
        input_str = input_str[2:-1]
    return input_str


def evaluate_conditional_expression(input_str: str) -> str:
    if input_str.startswith("['${") and input_str.endswith("}']"):
        condition = find_conditional_expression_groups(input_str[4:-3])
        if condition is not None:
            input_str = input_str[4:-3]
    else:
        condition = find_conditional_expression_groups(input_str)
    if condition is None:
        return input_str

    while condition:
        groups, start, end = condition
        if len(groups) != 3:
            return input_str
        evaluated_condition = evaluate_compare(groups[0])
        if type(evaluated_condition) is str:
            evaluated_condition = evaluate_terraform(groups[0])
        condition_substr = input_str[start:end]
        bool_evaluated_condition = convert_to_bool(evaluated_condition)
        if bool_evaluated_condition is True:
            true_val = str(evaluate_terraform(groups[1])).strip()
            input_str = input_str.replace(condition_substr, true_val)
        elif bool_evaluated_condition is False:
            false_val = str(evaluate_terraform(groups[2])).strip()
            input_str = input_str.replace(condition_substr, false_val)
        else:
            # in case we didn't succeed to evaluate condition we shouldn't put any value.
            break
        condition = find_conditional_expression_groups(input_str)

    return input_str


def evaluate_compare(input_str: str) -> str | bool | int:
    """
    :param input_str: string like "a && b" (supported operators: ==, != , <, <=, >, >=, && , ||)
    :return: evaluation of the expression
    """
    if isinstance(input_str, str) and "for" not in input_str:
        if not any(operator in input_str for operator in COMPARE_OPERATORS):
            # if an operator doesn't exist in the string, no need to proceed
            return input_str

        match = re.search(COMPARE_REGEX, input_str)
        if match:
            compare_parts = match.groupdict()
            a = compare_parts.get("a")
            b = compare_parts.get("b")
            op = compare_parts.get("operator")
            if a and b and op:
                try:
                    return apply_binary_op(evaluate_terraform(a), evaluate_terraform(b), op)
                except (TypeError, SyntaxError):
                    return input_str

    return input_str


def _handle_literal(input_str: str) -> Any:
    try:
        e = ast.literal_eval(input_str)
        if isinstance(e, list) and len(e) == 1:
            return e[0]
    except (ValueError, SyntaxError):
        pass

    return input_str


def _remove_variable_formatting(input_str: str) -> str:
    return input_str[2:-1] if input_str.startswith(f'{renderer.DOLLAR_PREFIX}{renderer.LEFT_CURLY}') and input_str.endswith(renderer.RIGHT_CURLY) else input_str


def handle_for_loop(input_str: Union[str, int, bool]) -> str | int | bool:
    if isinstance(input_str, str) and renderer.FOR_LOOP in input_str and '?' not in input_str:
        old_input_str = input_str
        input_str = _handle_literal(input_str)
        if isinstance(input_str, str) and renderer.FOR_LOOP in input_str:
            input_str = _remove_variable_formatting(input_str)
            start_bracket_idx = input_str[1:].find(renderer.LEFT_BRACKET)
            end_bracket_idx = renderer.find_match_bracket_index(input_str, start_bracket_idx + 1)
            if start_bracket_idx == -1 or end_bracket_idx == -1:
                return old_input_str

            rendered_statement = input_str[start_bracket_idx:end_bracket_idx + 1].replace('"', '\\"').replace("'", '"')
            new_val: str | None = ''
            if input_str.startswith(renderer.LEFT_CURLY):
                new_val = _handle_for_loop_in_dict(rendered_statement, input_str, end_bracket_idx + 1)
            elif input_str.startswith(renderer.LEFT_BRACKET):
                new_val = _handle_for_loop_in_list(rendered_statement, input_str, end_bracket_idx + 1)
            return new_val if new_val else old_input_str
        else:
            return input_str
    else:
        return input_str


def _extract_expression_from_statement(statement: str, start_expression_idx: int) -> str:
    """
    statement: [ for val in ["v", "k"] : val ]
    start_expression_idx: len(" for val in ["v", "k"]")
    output: "val"

    statement: { for val in {"name": "a", "val": "val"} : val.name => true }
    start_expression_idx: len(" for val in {"name": "a", "val": "val"}")
    output: val.name => true
    """
    return statement[start_expression_idx + len(renderer.KEY_VALUE_SEPERATOR):-1]


def _handle_for_loop_in_dict(object_to_run_on: str, statement: str, start_expression_idx: int) -> Optional[str]:
    try:
        evaluated_object_to_run_on: list[dict[str, Any]] = ast.literal_eval(object_to_run_on.replace(' ', ''))
    except (ValueError, SyntaxError):
        return None
    expression = _extract_expression_from_statement(statement, start_expression_idx)
    split_expression = expression.replace(' ', '').split(renderer.FOR_EXPRESSION_DICT)
    if len(split_expression) != 2:
        return None
    k_expression, v_expression = split_expression
    obj_key = statement.split(' ')[1]
    if k_expression.startswith(f'{obj_key}.'):
        k_expression = k_expression.replace(f'{obj_key}.', '')
    rendered_result = {}
    for obj in evaluated_object_to_run_on:
        val_to_assign = obj if statement.startswith(f'{renderer.LEFT_CURLY}{renderer.FOR_LOOP} {v_expression}') else evaluate_terraform(v_expression)
        try:
            rendered_result[obj[k_expression]] = val_to_assign
        except (TypeError, KeyError):
            return None
    return json.dumps(rendered_result)


def _handle_for_loop_in_list(object_to_run_on: str, statement: str, start_expression_idx: int) -> Optional[str]:
    try:
        evaluated_object_to_run_on: list[Any] = ast.literal_eval(object_to_run_on.replace(' ', ''))
    except (ValueError, SyntaxError):
        return None
    expression = _extract_expression_from_statement(statement, start_expression_idx)
    if renderer.LOOKUP in expression:
        return None
    if renderer.DOLLAR_PREFIX in expression:
        return _handle_for_loop_in_list_of_dicts(
            object_to_run_on=evaluated_object_to_run_on,
            statement=statement,
            expression=expression,
        )

    rendered_result = []
    for obj in evaluated_object_to_run_on:
        val_to_assign = obj if statement.startswith(f'{renderer.LEFT_BRACKET}{renderer.FOR_LOOP} {expression}') else evaluate_terraform(expression)
        rendered_result.append(val_to_assign)
    return json.dumps(rendered_result)


def _handle_for_loop_in_list_of_dicts(object_to_run_on: list[Any], statement: str, expression: str) -> str:
    rendered_result = []
    loop_key = f"${{{statement.split(' ')[1]}."  # ex. "${val."
    if loop_key in expression:
        for obj in object_to_run_on:
            val_to_assign = expression
            if isinstance(obj, dict):
                for obj_key, obj_value in obj.items():
                    replace_value = f"{loop_key}{obj_key}}}"  # ex. "${val.name}"
                    if replace_value in val_to_assign:
                        if isinstance(obj_value, (list, dict)):
                            obj_value = json.dumps(obj_value)
                        if isinstance(obj_value, (bool, int)) or obj_value is None:
                            # need to also remove the surrounding quotes
                            val_to_assign = val_to_assign.replace(f"'{replace_value}'", str(obj_value))
                        else:
                            val_to_assign = val_to_assign.replace(replace_value, obj_value)
            try:
                # it should be a JSON, but better be safe than sorry
                val_to_assign = ast.literal_eval(val_to_assign)
            except (ValueError, SyntaxError):
                # ignore unparsable expressions
                continue
            rendered_result.append(val_to_assign)
    return json.dumps(rendered_result)


def evaluate_json_types(input_str: Any) -> Any:
    # https://www.terraform.io/docs/language/functions/jsonencode.html
    if isinstance(input_str, str) and input_str.startswith("jsonencode("):
        return input_str.replace("true", "True").replace("false", "False").replace("null", "None")

    return input_str


def apply_binary_op(a: Optional[Union[str, int, bool]], b: Optional[Union[str, int, bool]], operator: str) -> bool | int | str:
    # apply the operator after verifying that a and b have the same type.
    operators: Dict[str, Callable[[T, T], bool | int | str]] = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        "&&": lambda a, b: a and b,
        "||": lambda a, b: a or b,
    }
    type_a = type(a)
    type_b = type(b)

    if type_a != type_b:
        try:
            temp_b = type_a(b)  # type:ignore[misc,arg-type]
            if isinstance(a, bool) and b:
                temp_b = bool(convert_to_bool(b))
            return operators[operator](a, temp_b)  # type:ignore[type-var]
        except Exception:
            temp_a = type_b(a)  # type:ignore[misc,arg-type]
            if isinstance(b, bool) and a:
                temp_a = bool(convert_to_bool(a))
            return operators[operator](temp_a, b)  # type:ignore[type-var]
    else:
        return operators[operator](a, b)  # type:ignore[type-var]


def evaluate_directives(input_str: str) -> str:
    if "%{" not in input_str:
        # no need to proceed further
        return input_str

    if re.search(DIRECTIVE_EXPR, input_str) is None:
        return input_str

    # replace `%{if <BOOL>}%{true_val}%{else}%{false_val}%{endif}` pattern with `<BOOL> ? true_val : false_val`
    matching_directives = re.findall(DIRECTIVE_EXPR, input_str)
    if len(matching_directives) == 3:
        if (
            re.search(r"\bif\b", matching_directives[0])
            and re.search(r"\belse\b", matching_directives[1])
            and re.search(r"\bendif\b", matching_directives[2])
        ):
            split_by_directives = re.split(DIRECTIVE_EXPR, input_str)
            edited_str = ""
            for part in split_by_directives:
                if re.search(r"\bif\b", part):
                    part = part.replace("if", "%{") + " ? "
                    part = re.sub(r"\s", "", part)
                if re.search(r"\belse\b", part):
                    part = part.replace("else", ":")
                    part = re.sub(r"\s", "", part)
                if re.search(r"\bendif\b", part):
                    part = part.replace("endif", "}")
                    part = re.sub(r"\s", "", part)
                edited_str += part
            input_str = edited_str

    matching_directives = re.split(DIRECTIVE_EXPR, input_str)
    evaluated_string_parts = []
    for str_part in matching_directives:
        evaluated_string_parts.append(evaluate_terraform(str_part))

    # Handle evaluation results which are integer / boolean
    evaluated_string_parts = [v if isinstance(v, str) else str(v) for v in evaluated_string_parts]
    return "".join(evaluated_string_parts)


def evaluate_map(input_str: str) -> str:
    # first replace maps ":" with "="
    all_curly_brackets = find_brackets_pairs(input_str, "{", "}")
    if "=" in input_str:
        for curly_match in all_curly_brackets:
            curly_start = curly_match["start"]
            curly_end = curly_match["end"]
            replaced_matching_map = ' ' + input_str[curly_start: curly_end + 1] + ' '
            for i in range(1, len(replaced_matching_map) - 1):
                if replaced_matching_map[i] == "=" and replaced_matching_map[i - 1] not in ["=", "!"] and replaced_matching_map[i + 1] != "=":
                    replaced_matching_map = f'{replaced_matching_map[:i]}:{replaced_matching_map[i + 1:]}'
            input_str = input_str.replace(input_str[curly_start : curly_end + 1], replaced_matching_map[1:-1])

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
            if square_start > curly_end and (
                square_start == curly_end + 1 or all(c == " " for c in input_str[curly_end + 1 : square_start])
            ):
                origin_match_str = input_str[curly_start : square_end + 1]
                map_access = input_str[square_start + 1 : square_end]
                if not map_access.startswith('"') and not map_access.endswith('"'):
                    origin_match_str = origin_match_str.replace(f"[{map_access}]", f'["{map_access}"]')
                evaluated = _try_evaluate(origin_match_str)
                if evaluated:
                    input_str = input_str.replace(input_str[curly_start : square_end + 1], str(evaluated))
                    break

    return input_str


def convert_to_bool(bool_str: Union[str, int]) -> Union[str, int, bool]:
    if bool_str in ["true", '"true"', "True", '"True"', 1, "1"]:
        return True
    elif bool_str in ["false", '"false"', "False", '"False"', 0, "0"]:
        return False
    else:
        return bool_str


def evaluate_list_access(input_str: str) -> str:
    # find list access like [a, b, c][0] and extract the right value - a

    all_square_brackets = find_brackets_pairs(input_str, "[", "]")
    prev_start = -1
    prev_end = -1
    for match in all_square_brackets:
        if (
            match["start"] == prev_end + 1 or all(c == " " for c in input_str[prev_end + 1 : match["start"]])
        ) and prev_start != -1:
            curr_str = input_str[match["start"] + 1 : match["end"]]
            if curr_str.isnumeric():
                evaluated = _try_evaluate(input_str[prev_start : match["end"] + 1])
                if evaluated:
                    input_str = input_str.replace(input_str[prev_start : match["end"] + 1], str(evaluated))
        prev_start = match["start"]
        prev_end = match["end"]

    return input_str


def find_brackets_pairs(input_str: str, starting: str, closing: str) -> List[Dict[str, int]]:
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
        if end != -1 and end - start > 1:
            all_brackets.append({"start": start, "end": end})
    return all_brackets


def find_conditional_expression_groups(input_str: str) -> Optional[Tuple[List[str], int, int]]:
    """
    from condition ? true_val : false_val return [condition, true_val, false_val]
    """
    if '?' not in input_str or ':' not in input_str:
        return None
    if input_str.index('?') > input_str.rindex(':'):
        return None
    brackets_pairs = {
        '[': ']',
        '{': '}',
        '(': ')'
    }
    str_keys = {'\'', '"'}

    stack: list[tuple[str, int]] = []
    groups = []
    end_stack = []

    def _update_stack_if_needed(char: str, i: int) -> None:
        # can be true only if the char in str_keys or in brackets_pairs.values()
        if stack and stack[-1][0] == char:
            stack.pop(len(stack) - 1)
        elif char in brackets_pairs:
            stack.append((brackets_pairs[char], i))
        elif char in str_keys:
            stack.append((char, i))

    def _find_separator_index(separator: str, input_str: str, start: int, update_end_stack: bool = False) -> Optional[int]:
        for i in range(start, len(input_str)):
            char = input_str[i]
            if char == separator:
                if not stack or stack in end_stack:
                    return i
                if update_end_stack:
                    end_stack.extend(stack)
                    return i
            _update_stack_if_needed(char, i)

        return None

    # find first separator
    first_separator = _find_separator_index('?', input_str, 0, update_end_stack=True)
    if first_separator is None:
        return None
    start = 0 if not stack else stack[-1][1]
    groups.append(input_str[start:first_separator])

    # find second separator
    second_separator = _find_separator_index(':', input_str, first_separator)
    if second_separator is None:
        return None
    groups.append(input_str[first_separator + 1:second_separator])

    if not stack:
        groups.append(input_str[second_separator + 1:])
        return groups, 0, len(input_str)

    start = stack[-1][1]
    end = len(input_str)
    for i in range(second_separator + 1, len(input_str)):
        char = input_str[i]
        _update_stack_if_needed(char, i)
        if not stack:
            end = i + 1
            break
        if len(stack) + 1 == len(end_stack):
            end = i
            break

    groups.append(input_str[second_separator + 1:end])

    return groups, start, end
