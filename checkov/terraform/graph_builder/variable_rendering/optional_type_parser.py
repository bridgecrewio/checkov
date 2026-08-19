"""Parse Terraform optional() type constraints and merge their defaults into variable values."""
from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

from checkov.common.util.data_structures_utils import pickle_deepcopy

logger = logging.getLogger(__name__)

_NO_DEFAULT = object()  # sentinel: optional() has no second argument


def _iter_chars(s: str, start: int = 0) -> Iterator[tuple[int, str, bool]]:
    """Yield ``(index, char, in_string)`` for each character, handling escapes and quotes.

    *in_string* is ``True`` for characters inside quoted strings or escape sequences.
    Consumers that only care about structural characters can simply ``if in_string: continue``.
    """
    in_single = False
    in_double = False
    escape_next = False
    for i in range(start, len(s)):
        c = s[i]
        if escape_next:
            escape_next = False
            yield i, c, True
            continue
        if c == "\\":
            escape_next = True
            yield i, c, True
            continue
        if c == "'" and not in_double:
            in_single = not in_single
            yield i, c, True
            continue
        if c == '"' and not in_single:
            in_double = not in_double
            yield i, c, True
            continue
        yield i, c, in_single or in_double


def _parse_optional_defaults_from_type(type_str: Any) -> dict[str, Any]:
    """Parse a Terraform type constraint string and extract default values from optional() calls.

    Returns:
      {"type": "RSA-HSM", "size": 2048}
    """
    type_str = _unwrap_type_str(type_str)
    if not type_str:
        return {}
    defaults, _ = _parse_object_fields(type_str)
    return defaults


def apply_optional_defaults(value: Any, type_str: Any) -> Any:
    """Apply optional() default values from a type constraint to a variable value.

    Recursively merges missing keys from optional() defaults into the value based
    on the type structure.  Handles nested objects at arbitrary depth --
    ``pickle_deepcopy`` is called once at the top level; all recursive operations
    work in-place on the copy.
    """
    type_str = _unwrap_type_str(type_str)
    if not type_str:
        return value

    defaults, field_types = _parse_object_fields(type_str)
    has_nested = _has_nested_objects(field_types)
    if not defaults and not has_nested:
        return value

    wrapper_type = _get_wrapper_type(type_str)

    # Handles object({...}) and also list/set/tuple(object({...})) when the
    # graph builder has unwrapped a single-element list into a plain dict.
    if wrapper_type in ("object", "list", "set", "tuple") and isinstance(value, dict):
        if not _needs_merge(value, defaults, field_types):
            return value
        value = pickle_deepcopy(value)
        _merge_defaults_into_dict(value, defaults)
        _recurse_into_fields(value, field_types)
        return value

    if wrapper_type in ("list", "set", "tuple") and isinstance(value, list):
        if not any(_needs_merge(item, defaults, field_types)
                   for item in value if isinstance(item, dict)):
            return value
        value = pickle_deepcopy(value)
        for item in value:
            if isinstance(item, dict):
                _merge_defaults_into_dict(item, defaults)
                _recurse_into_fields(item, field_types)
        return value

    if wrapper_type == "map" and isinstance(value, dict):
        if not any(_needs_merge(v, defaults, field_types)
                   for v in value.values() if isinstance(v, dict)):
            return value
        value = pickle_deepcopy(value)
        for v in value.values():
            if isinstance(v, dict):
                _merge_defaults_into_dict(v, defaults)
                _recurse_into_fields(v, field_types)
        return value

    return value


def _parse_object_fields(type_str: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse object fields, returning (defaults, field_types).

    defaults: field_name -> default value for optional(type, default) fields
    field_types: field_name -> unwrapped type string for ALL fields (used for recursive descent)
    """
    object_content = _extract_object_content(type_str)
    if not object_content:
        return {}, {}

    defaults: dict[str, Any] = {}
    field_types: dict[str, str] = {}
    fields = _split_at_top_level(object_content, ",")
    for field in fields:
        field = field.strip()
        field_name, field_value = _parse_field_definition(field)
        if field_name is None or field_value is None:
            continue
        # Unwrap ${...} from field values
        field_value = _strip_interpolation(field_value)
        field_types[field_name] = field_value
        if field_value.startswith("optional("):
            default_val = _extract_optional_default(field_value)
            if default_val is not _NO_DEFAULT:
                defaults[field_name] = default_val

    return defaults, field_types


def _merge_defaults_into_dict(d: dict[str, Any], defaults: dict[str, Any]) -> None:
    """Merge optional defaults into a dict for keys that are missing."""
    for key, default_value in defaults.items():
        if key not in d:
            d[key] = default_value


def _has_nested_objects(field_types: dict[str, str]) -> bool:
    """Return True if any field type contains a nested object({...})."""
    return any("object(" in _extract_optional_inner_type(ft) for ft in field_types.values())


def _needs_merge(d: dict[str, Any], defaults: dict[str, Any], field_types: dict[str, str]) -> bool:
    """Check if a dict needs any defaults applied (top-level or nested)."""
    if any(k not in d for k in defaults):
        return True
    # Conservative: if any present field could contain nested objects, assume work needed.
    # The recursive functions handle the "nothing to do" case naturally.
    for field_name, field_type in field_types.items():
        if field_name not in d:
            continue
        inner_type = _extract_optional_inner_type(field_type)
        if "object(" in inner_type and isinstance(d[field_name], (dict, list)):
            return True
    return False


def _recurse_into_fields(d: dict[str, Any], field_types: dict[str, str]) -> None:
    """Recursively apply optional defaults to nested object fields (in-place).

    When the graph builder has unwrapped a single-element list into a plain dict
    but the type says ``list(object({...}))``, the value is re-wrapped into a
    list after enrichment so downstream consumers (for_each, find_in_dict) see
    the correct type.
    """
    for field_name, field_type in field_types.items():
        if field_name not in d:
            continue
        inner_type = _extract_optional_inner_type(field_type)
        if "object(" not in inner_type:
            continue
        nested_defaults, nested_field_types = _parse_object_fields(inner_type)
        if not nested_defaults and not _has_nested_objects(nested_field_types):
            continue
        wrapper = _get_wrapper_type(inner_type)
        # Re-wrap single-element list that the graph builder unwrapped into a dict
        if wrapper in ("list", "set", "tuple") and isinstance(d[field_name], dict):
            _merge_defaults_into_dict(d[field_name], nested_defaults)
            _recurse_into_fields(d[field_name], nested_field_types)
            d[field_name] = [d[field_name]]
        else:
            _apply_in_place(d[field_name], wrapper, nested_defaults, nested_field_types)


def _apply_in_place(value: Any, wrapper_type: str, defaults: dict[str, Any],
                    field_types: dict[str, str]) -> None:
    """Apply defaults in-place for a given wrapper type (no copy -- already deep-copied)."""
    if wrapper_type in ("object", "list", "set", "tuple") and isinstance(value, dict):
        # Handles object({...}) and single-element lists unwrapped by the graph builder
        _merge_defaults_into_dict(value, defaults)
        _recurse_into_fields(value, field_types)
    elif wrapper_type in ("list", "set", "tuple") and isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                _merge_defaults_into_dict(item, defaults)
                _recurse_into_fields(item, field_types)
    elif wrapper_type == "map" and isinstance(value, dict):
        for v in value.values():
            if isinstance(v, dict):
                _merge_defaults_into_dict(v, defaults)
                _recurse_into_fields(v, field_types)


def _unwrap_type_str(type_str: Any) -> str | None:
    """Unwrap type_str from list or ${...} wrapper, returning a plain string or None."""
    if isinstance(type_str, list):
        if len(type_str) == 1 and isinstance(type_str[0], str):
            type_str = type_str[0]
        else:
            logger.debug(f"type_str is a list with {len(type_str)} elements; expected 1, skipping optional parsing")
            return None
    if not isinstance(type_str, str):
        return None
    type_str = type_str.strip()
    if type_str.startswith("${") and type_str.endswith("}"):
        type_str = type_str[2:-1].strip()
    return type_str if type_str else None


def _get_wrapper_type(type_str: str) -> str:
    """Get the outermost type wrapper (e.g., 'list', 'object', 'map')."""
    paren_idx = type_str.find("(")
    if paren_idx == -1:
        return type_str
    return type_str[:paren_idx].strip()


def _strip_interpolation(s: str) -> str:
    """Strip ${...} wrapper and surrounding quotes from a value string.

    The HCL parser adds a layer of backslash-escaping at each nesting level,
    so after stripping quotes/interpolation we also unescape ``\\'`` -> ``'``
    and ``\\"`` -> ``"``.
    """
    s = s.strip()
    # Strip surrounding single quotes: '${...}' -> ${...}
    if s.startswith("'") and s.endswith("'"):
        s = s[1:-1].strip()
    # Strip surrounding double quotes: "${...}" -> ${...}
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1].strip()
    # Strip ${...} interpolation wrapper
    if s.startswith("${") and s.endswith("}"):
        s = s[2:-1].strip()
    # Unescape backslash quoting from HCL parser nesting.  Each nesting
    # level adds another escape layer (e.g. \' -> \\\' -> \\\\\\\'), so we
    # keep unescaping until the string stabilises.  Each iteration removes at
    # least one backslash, so the loop is bounded by len(s).
    while "\\" in s:
        unescaped = s.replace("\\'", "'").replace('\\"', '"')
        if unescaped == s:
            break
        s = unescaped
    return s


def _extract_object_content(type_str: str) -> str | None:
    """Find and extract the content of the first object({...}) in the type string.

    Handles wrappers like list(object({...})), set(object({...})), etc.
    Returns the content between the outer { and matching }.
    """
    search_str = "object({"
    idx = type_str.find(search_str)
    if idx == -1:
        return None

    brace_start = idx + len(search_str) - 1  # position of {
    depth = 0
    for i, c, in_string in _iter_chars(type_str, start=brace_start):
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return type_str[brace_start + 1 : i]
    return None


def _parse_field_definition(field: str) -> tuple[str | None, str | None]:
    """Parse a key-value pair separated by ``:`` or ``=``.

    Handles type fields (``'name': '${string}'``) and HCL map literals
    inside default values (``{env = "prod"}``).
    Returns (field_name, field_value) or (None, None) if unparseable.
    """
    sep_idx = _find_top_level_separator(field, ":")
    if sep_idx != -1:
        name = field[:sep_idx].strip().strip("'\"")
        value = field[sep_idx + 1 :].strip()
        return name, value

    sep_idx = _find_top_level_separator(field, "=")
    if sep_idx != -1:
        name = field[:sep_idx].strip().strip("'\"")
        value = field[sep_idx + 1 :].strip()
        return name, value

    return None, None


def _find_top_level_separator(s: str, sep: str) -> int:
    """Find the position of the first top-level separator character.

    Skips separators inside parentheses, braces, brackets, or strings.
    Returns -1 if not found.
    """
    depth_paren = depth_brace = depth_bracket = 0
    for i, c, in_string in _iter_chars(s):
        if in_string:
            continue
        if c == "(":
            depth_paren += 1
        elif c == ")":
            depth_paren -= 1
        elif c == "{":
            depth_brace += 1
        elif c == "}":
            depth_brace -= 1
        elif c == "[":
            depth_bracket += 1
        elif c == "]":
            depth_bracket -= 1
        elif c == sep and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
            return i
    return -1


def _split_at_top_level(s: str, delimiter: str) -> list[str]:
    """Split a string at a delimiter that is at the top level (not inside brackets or strings)."""
    result: list[str] = []
    seg_start = 0
    depth_paren = depth_brace = depth_bracket = 0
    for i, c, in_string in _iter_chars(s):
        if in_string:
            continue
        if c == "(":
            depth_paren += 1
        elif c == ")":
            depth_paren -= 1
        elif c == "{":
            depth_brace += 1
        elif c == "}":
            depth_brace -= 1
        elif c == "[":
            depth_bracket += 1
        elif c == "]":
            depth_bracket -= 1
        elif c == delimiter and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
            result.append(s[seg_start:i])
            seg_start = i + 1
    trailing = s[seg_start:]
    if trailing:
        result.append(trailing)
    return result


def _extract_optional_inner_type(field_type: str) -> str:
    """Strip optional() wrapper and return the inner type argument.

    For ``optional(map(object({...})), {})``, returns ``map(object({...}))``.
    Non-optional types pass through unchanged.
    """
    if not field_type.startswith("optional("):
        return field_type
    inner = field_type[len("optional("):]
    close_idx = _find_matching_close_paren(inner)
    if close_idx == -1:
        return field_type
    parts = _split_at_top_level(inner[:close_idx], ",")
    return parts[0].strip()


def _extract_optional_default(optional_expr: str) -> Any:
    """Extract the default value from an optional(type, default) expression.

    Returns _NO_DEFAULT sentinel if there is no default (only one argument).
    """
    if not optional_expr.startswith("optional("):
        return _NO_DEFAULT

    inner = optional_expr[len("optional(") :]
    # Find the matching closing paren
    close_idx = _find_matching_close_paren(inner)
    if close_idx == -1:
        return _NO_DEFAULT

    inner = inner[:close_idx]

    # Find the first top-level comma (separating type from default)
    parts = _split_at_top_level(inner, ",")
    if len(parts) < 2:
        return _NO_DEFAULT  # No default value

    # Everything after the first comma is the default value
    default_str = ",".join(parts[1:]).strip()
    return _parse_default_value(default_str)


def _find_matching_close_paren(s: str) -> int:
    """Find the position of the matching closing ')' for an already-opened '('."""
    depth = 1
    for i, c, in_string in _iter_chars(s):
        if in_string:
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _parse_default_value(value_str: str) -> Any:
    """Convert a default value string from a type constraint to a Python value.

    String defaults are plain (no embedded quotes) and booleans are
    Python-style (True/False) as produced by the HCL parser.
    """
    value_str = value_str.strip()

    # String literal -- strip quotes to produce plain string (matching default value format)
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]

    # Boolean -- the HCL parser converts to Python bools, but also handle HCL lowercase
    if value_str in ("true", "True"):
        return True
    if value_str in ("false", "False"):
        return False

    # Null
    if value_str in ("null", "None"):
        return None

    # Integer
    try:
        return int(value_str)
    except ValueError:
        pass

    # Float
    try:
        return float(value_str)
    except ValueError:
        pass

    # Empty dict/map
    if value_str == "{}":
        return {}

    # Empty list/tuple
    if value_str == "[]":
        return []

    # Non-empty dict/map: {key = "val1", key2 = "val2"}
    if value_str.startswith("{") and value_str.endswith("}"):
        return _parse_hcl_map(value_str)

    # Non-empty list: ["a", "b"]
    if value_str.startswith("[") and value_str.endswith("]"):
        return _parse_hcl_list(value_str)

    # Unresolvable -- return as string
    logger.debug(f"Could not parse optional default value: {value_str}")
    return value_str


def _parse_hcl_map(map_str: str) -> dict[str, Any]:
    """Parse an HCL-style map literal like {key = "val1", key2 = "val2"}."""
    inner = map_str[1:-1].strip()
    if not inner:
        return {}

    result: dict[str, Any] = {}
    fields = _split_at_top_level(inner, ",")
    for field in fields:
        name, value = _parse_field_definition(field.strip())
        if name is not None and value is not None:
            result[name] = _parse_default_value(value)
    return result


def _parse_hcl_list(list_str: str) -> list[Any]:
    """Parse an HCL-style list literal like ["a", "b", 1]."""
    inner = list_str[1:-1].strip()
    if not inner:
        return []

    result: list[Any] = []
    items = _split_at_top_level(inner, ",")
    for item in items:
        result.append(_parse_default_value(item.strip()))
    return result
