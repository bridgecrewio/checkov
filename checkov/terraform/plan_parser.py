from checkov.terraform.context_parsers.tf_plan import parse

simple_types = [str, int, float, bool]


def _is_simple_type(obj):
    for simple_type in simple_types:
        if isinstance(obj, simple_type) or obj == None:
            return True
    return False


def _is_list_of_simple_types(l):
    if not isinstance(l, list):
        return False
    for i in l:
        if not _is_simple_type(i):
            return False
    return True


def _is_list_of_dicts(l):
    if not isinstance(l, list):
        return False
    for i in l:
        if isinstance(i, dict):
            return True
    return False


def _hclify(obj):
    ret_dict = {}
    if not isinstance(obj, dict):
        raise Exception("this method receives only dicts")
    if hasattr(obj, 'start_mark') and hasattr(obj, "end_mark"):
        obj["start_line"] = obj.start_mark.line
        obj["end_line"] = obj.end_mark.line
    for key, value in obj.items():
        if _is_simple_type(value) or _is_list_of_simple_types(value):
            ret_dict[key] = [value]

        if _is_list_of_dicts(value):
            child_list = []
            for internal_val in value:
                child_list.append(_hclify(internal_val))
            ret_dict[key] = child_list
        if isinstance(value, dict):
            child_dict = _hclify(value)
            ret_dict[key] = [child_dict]
    return ret_dict


def parse_tf_plan(tf_plan_file):
    """

    :type tf_plan_file: str - path to plan file
    :rtype: tf_definition dictionary
    """
    tf_defintions = {}
    tf_defintions[tf_plan_file] = {}
    tf_defintions[tf_plan_file]['resource'] = []
    template, template_lines = parse(tf_plan_file)
    if not template:
        return None, None
    for resource in template.get('planned_values', {}).get("root_module", {}).get("resources", []):
        resource_block = {}
        resource_block[resource['type']] = {}
        resource_block[resource['type']][resource.get('name', "default")] = _hclify(resource['values'])
        tf_defintions[tf_plan_file]['resource'].append(resource_block)
    for child_module in template.get('planned_values', {}).get("root_module", {}).get("child_modules",[]):
        for resource in child_module.get("resources", []):
            resource_block = {}
            resource_block[resource['type']] = {}
            resource_block[resource['type']][resource.get('name', "default")] = _hclify(resource['values'])
            tf_defintions[tf_plan_file]['resource'].append(resource_block)

    return tf_defintions, template_lines
