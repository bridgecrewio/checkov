from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Optional


@dataclass
class VarBlockMatch:
    full_str: str       # Example: ${local.foo}
    var_only: str       # Example: local.fop

    def replace(self, original: str, replaced: str):
        self.full_str = self.full_str.replace(original, replaced)
        self.var_only = self.var_only.replace(original, replaced)


class ParserMode(Enum):
    # Note: values are just for debugging.
    EVAL = "${"
    MAP = "{"
    STRING_SINGLE_QUOTE = "'"
    STRING_DOUBLE_QUOTE = '"'
    PARAMS = "("
    ARRAY = "["

    @staticmethod
    def is_string(mode: str) -> bool:
        return mode == ParserMode.STRING_SINGLE_QUOTE or mode == ParserMode.STRING_DOUBLE_QUOTE

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


def find_var_blocks(value: str) -> List[VarBlockMatch]:
    """
    Find and return all the var blocks within a given string. Order is important and may contain portions of
    one another.
    """

    to_return: List[VarBlockMatch] = []

    mode_stack: List[ParserMode] = []
    eval_start_pos_stack: List[int] = []            # location of first char inside brackets
    preceding_dollar = False
    preceding_string_escape = False
    for index, c in enumerate(value):
        current_mode = "  " if not mode_stack else mode_stack[-1]

        # Print statement of power...
        # print(f"{str(index).ljust(3, ' ')} {c} {'$' if preceding_dollar else ' '} "
        #       f"{'`' if preceding_string_escape else ' '} "
        #       f"{current_mode.ljust(2)} - {mode_stack}")

        if c == "$":
            if preceding_dollar:     # ignore double $
                preceding_dollar = False
                continue

            preceding_dollar = True
            continue

        if c == "{" and preceding_dollar:
            mode_stack.append(ParserMode.EVAL)
            eval_start_pos_stack.append(index + 1)  # next char
            preceding_dollar = False
            continue
        elif c == "\\" and ParserMode.is_string(current_mode):
            preceding_string_escape = True
            continue

        preceding_dollar = False

        if c == "}":
            if current_mode == ParserMode.EVAL:
                mode_stack.pop()
                start_pos = eval_start_pos_stack.pop()
                eval_string = value[start_pos: index]
                to_return.append(VarBlockMatch("${" + eval_string + "}", eval_string))
            elif current_mode == ParserMode.MAP:
                mode_stack.pop()
        elif c == "]" and current_mode == ParserMode.ARRAY:
            mode_stack.pop()
        elif c == ")" and current_mode == ParserMode.PARAMS:
            mode_stack.pop()
        elif c == '"':
            if preceding_string_escape:
                preceding_string_escape = False
                continue
            elif current_mode == ParserMode.STRING_DOUBLE_QUOTE:
                mode_stack.pop()
            else:
                mode_stack.append(ParserMode.STRING_DOUBLE_QUOTE)
        elif c == "'":
            if preceding_string_escape:
                preceding_string_escape = False
                continue
            elif current_mode == ParserMode.STRING_SINGLE_QUOTE:
                mode_stack.pop()
            else:
                mode_stack.append(ParserMode.STRING_SINGLE_QUOTE)
        elif c == "{":
            # NOTE: Can't be preceded by a dollar sign (that was checked earlier)
            if not ParserMode.is_string(current_mode):
                mode_stack.append(ParserMode.MAP)
        elif c == "[":                                      # do we care?
            if not ParserMode.is_string(current_mode):
                mode_stack.append(ParserMode.ARRAY)
        elif c == "(":                                      # do we care?
            if not ParserMode.is_string(current_mode):
                mode_stack.append(ParserMode.PARAMS)
        elif c == "?" and current_mode == ParserMode.EVAL:  # ternary
            # If what's been processed in the ternary so far is "true" or "false" (boolean or string type)
            # then nothing special will happen here and only the full expression will be returned.
            # Anything else will be treated as an unresolved variable block.
            start_pos = eval_start_pos_stack[-1]        # DO NOT pop: there's no separate eval start indicator
            eval_string = value[start_pos: index].strip()

            # HACK ALERT: For the cases with the trailing quotes, see:
            #             test_hcl2_load_assumptions.py -> test_weird_ternary_string_clipping
            if eval_string not in {"true", "false", '"true"', '"false"', 'true"', 'false"'}:
                # REMINDER: The eval string is not wrapped in a eval markers since they didn't really
                #           appear in the original value. If they're put in, substitution doesn't
                #           work properly.
                to_return.append(VarBlockMatch(eval_string, eval_string))

        preceding_string_escape = False

    return to_return


def split_merge_args(value: str) -> Optional[List[str]]:
    """
    Split arguments of a merge function. For example, "merge(local.one, local.two)" would
    call this function with a value of "local.one, local.two" which would return
    ["local.one", "local.two"]. If the value cannot be unpacked, None will be returned.
    """
    if not value:
        return None

    # There are a number of splitting scenarios depending on whether variables or
    # direct maps are used:
    #           merge({tag1="foo"},{tag2="bar"})
    #           merge({tag1="foo"},local.some_tags)
    #           merge(local.some_tags,{tag2="bar"})
    #           merge(local.some_tags,local.some_other_tags)
    # Also, the number of arguments can vary, things can be nested, strings are evil...
    # See tests/terraform/test_parser_var_blocks.py for many examples.

    to_return = []
    current_arg_buffer = ""
    processing_str_escape = False
    inside_collection_stack = []        # newest at position 0, contains the terminator for the collection
    for c in value:
        if c == "," and not inside_collection_stack:
            current_arg_buffer = current_arg_buffer.strip()
            # Note: can get a zero-length buffer when there's a double comman. This can
            #       happen with multi-line args (see parser_internals test)
            if len(current_arg_buffer) != 0:
                to_return.append(current_arg_buffer)
            current_arg_buffer = ""
        else:
            current_arg_buffer += c

        processing_str_escape = _str_parser_loop_collection_helper(c,
                                                                   inside_collection_stack,
                                                                   processing_str_escape)

    current_arg_buffer = current_arg_buffer.strip()
    if len(current_arg_buffer) > 0:
        to_return.append(current_arg_buffer)

    if len(to_return) == 0:
        return None
    return to_return



def _str_parser_loop_collection_helper(c: str, inside_collection_stack: List[str],
                                       processing_str_escape: bool) -> bool:
    """
    This function handles dealing with tracking when a char-by-char state loop is inside a
    "collection" (map, array index, method args, string).

    :param c:       Active character
    :param inside_collection_stack:     Stack of terminators for collections. This will be modified by
                                        this function. The active terminator will be at position 0.


    :return: value to set for `processing_str_escape`
    """
    inside_a_string = False
    if inside_collection_stack:
        terminator = inside_collection_stack[0]

        if terminator == '"' or terminator == "'":
            if processing_str_escape:
                processing_str_escape = False
                return processing_str_escape
            elif c == "\\":
                processing_str_escape = True
                return processing_str_escape
            else:
                inside_a_string = True

        if c == terminator:
            del inside_collection_stack[0]
            return processing_str_escape

    if not inside_a_string:
        if c == '"':
            inside_collection_stack.insert(0, '"')
        elif c == "'":
            inside_collection_stack.insert(0, "'")
        elif c == "{":
            inside_collection_stack.insert(0, "}")
        elif c == "[":
            inside_collection_stack.insert(0, "]")
        elif c == "(":
            inside_collection_stack.insert(0, ")")

    return processing_str_escape
