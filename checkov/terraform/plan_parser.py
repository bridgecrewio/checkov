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


def _hclify(obj, parent_key=None):
    ret_dict = {}
    if not isinstance(obj, dict):
        raise Exception("this method receives only dicts")
    if hasattr(obj, 'start_mark') and hasattr(obj, "end_mark"):
        obj["start_line"] = obj.start_mark.line
        obj["end_line"] = obj.end_mark.line
    for key, value in obj.items():
        if _is_simple_type(value) or _is_list_of_simple_types(value):
            if parent_key == "tags":
                ret_dict[key] = value
            else:
                ret_dict[key] = [value]

        if _is_list_of_dicts(value):
            child_list = []
            for internal_val in value:
                child_list.append(_hclify(internal_val))
            ret_dict[key] = child_list
        if isinstance(value, dict):
            child_dict = _hclify(value, key)
            if parent_key == "tags":
                ret_dict[key] = child_dict
            else:
                ret_dict[key] = [child_dict]
    return ret_dict

def _prepare_resource_block(resource):
    """
    hclify resource if pre-conditions met.
    :type: resource: dict: tf resource block
    :rtype: resource_block: dict: hclifyed if conditions met
    :rtype: prepared: boolean: whether conditions met to prepare data
    """
    resource_block = {}
    resource_block[resource['type']] = {}
    prepared = False
    mode = ""
    if 'mode' in resource:
        mode = resource.get("mode")
    # Rare cases where data block appears in resources with same name as resource block and only partial values
    # and where *_module resources don't have values field
    if mode == "managed" and 'values' in resource:
        resource_block[resource['type']][resource.get("name", "default")] = _hclify(resource['values'])
        prepared = True
    return resource_block, prepared

def _find_child_modules(child_modules):
    """
    Find all child modules if any. Including any amount of nested child modules.
    :type: child_modules: list of tf child_module objects
    :rtype: resource_blocks: list of hcl resources
    """
    resource_blocks = []
    for child_module in child_modules:
        if child_module.get("child_modules",[]):
            nested_child_modules = child_module.get("child_modules",[])
            nested_blocks = _find_child_modules(nested_child_modules)
            for resource in nested_blocks:
                resource_blocks.append(resource)
        for resource in child_module.get("resources", []):
            resource_block, prepared = _prepare_resource_block(resource)
            if prepared is True:
                resource_blocks.append(resource_block)
    return resource_blocks


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
        resource_block, prepared = _prepare_resource_block(resource)
        if prepared is True:
            tf_defintions[tf_plan_file]['resource'].append(resource_block)
    child_modules = template.get('planned_values', {}).get("root_module", {}).get("child_modules",[])
    # Terraform supports modules within modules so we need to search
    # in nested modules to find all resource blocks
    resource_blocks = _find_child_modules(child_modules)
    for resource in resource_blocks:
        tf_defintions[tf_plan_file]['resource'].append(resource)
    return tf_defintions, template_lines
