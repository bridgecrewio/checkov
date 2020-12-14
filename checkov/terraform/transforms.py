from typing import Dict, Any

import dpath


PATHS_TO_WRAP_IN_EVAL_MARKERS = [
    # References in "depends_on" blocks, example: "aws_instance.leader"  --> "${aws_instance.leader}"
    "resource/*/*/depends_on",

    # Variable types
    "variable/*/type"
]

INNER_WRAP_LEVEL_PATTERNS: Dict[str, str] = {
    "data": "*/*/*",            # data.[].<source>.<name>.<value>.[]
    "locals": "*",              # locals.[].<name>.[]
    "module": "*/*",            # module.[].<name>.<value>.[]
    "output": "*/*",            # output.[].<name>.<value>.[]
    "provider": "*/*",          # provider.[].<type>.<name>.[]
    "resource": "*/*/*",        # resource.[].<type>.<name>.<value>.[]
    "variable": "*/*",          # variable.[].<name>.<value>.[]
}


def transform_hcl1(data_map: Dict[str, Any]) -> Dict[str, Any]:
    """
Performs an in-place modification of the given data_map to make data parsed with the HCL 1 parser look like
it came from the HCL 2 parser.
    :param data_map     Map containing terraform data which will be modified in-place (also returned).

    :return     `data_map` for easy chaining.
    """
    for path in PATHS_TO_WRAP_IN_EVAL_MARKERS:
        for key, value_maybe_list in dpath.search(data_map, path, yielded=True):
            if isinstance(value_maybe_list, str):
                if not value_maybe_list.startswith("${"):
                    dpath.set(data_map, key, "${" + value_maybe_list + "}")

            if isinstance(value_maybe_list, list):
                for index, value in enumerate(value_maybe_list):
                    # Make sure it's not already wrapped somehow or not a string
                    if isinstance(value, str) and not value.startswith("${"):
                        value_maybe_list[index] = "${" + value + "}"

    for k, v in data_map.items():
        layers_to_unwrap = 0
        expand_pattern = None
        if k in ["resource", "data"]:
            layers_to_unwrap = 2
            expand_pattern = "*/*"
        if k in ["module", "variable", "output", "provider"]:
            layers_to_unwrap = 1
            expand_pattern = "*"

        if isinstance(v, dict):
            _list_wrap_after_layers(v, layers_to_unwrap,
                                    # HACK ALERT: This is super hacky but stems from the problem that we
                                    #             can't tell the difference between an object and a map value
                                    #             in HCL 1. There are some smarts in `_list_wrap_after_layers`
                                    #             as well, but this is some extra assumption of the data to
                                    #             try to call out top-level blocks which aren't (generally)
                                    #             deep and so should be treated as values rather than nested
                                    #             object blocks. Of course, this doesn't really work reliably
                                    #             because different providers may do things different.
                                    #             Do the best we can. ¯\_(ツ)_/¯
                                    k not in ["data", "locals", "output"])

        # Wrap outer layers
        if layers_to_unwrap > 0:
            top_list = []
            data_map[k] = top_list
            for path, data in dpath.search(v, expand_pattern, yielded=True):
                submap = {}
                dpath.new(submap, path, data)
                top_list.append(submap)
        else:
            data_map[k] = [v]

    return data_map


def _list_wrap_after_layers(data: Dict[str, Any], bypass_layers: int, keep_unwrapping: bool):
    for k, v in data.items():
        if bypass_layers <= 0:
            data[k] = [v]
            if keep_unwrapping and isinstance(v, dict):
                _list_wrap_after_layers(v, 0, keep_unwrapping)

        elif isinstance(v, dict):
            _list_wrap_after_layers(v, bypass_layers - 1, keep_unwrapping)
