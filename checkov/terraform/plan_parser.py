from __future__ import annotations

import itertools
from typing import Optional, Tuple, Dict, List, Any

from checkov.common.parsers.node import DictNode, ListNode
from checkov.terraform.context_parsers.tf_plan import parse

SIMPLE_TYPES = (str, int, float, bool)
TF_PLAN_RESOURCE_ADDRESS = "__address__"
TF_PLAN_RESOURCE_CHANGE_ACTIONS = "__change_actions__"


def _is_simple_type(obj: Any) -> bool:
    if obj is None:
        return True
    if isinstance(obj, SIMPLE_TYPES):
        return True
    return False


def _is_list_of_simple_types(obj: Any) -> bool:
    if not isinstance(obj, list):
        return False
    for i in obj:
        if not _is_simple_type(i):
            return False
    return True


def _is_list_of_dicts(obj: Any) -> bool:
    if not isinstance(obj, list):
        return False
    for i in obj:
        if isinstance(i, dict):
            return True
    return False


def _hclify(obj: DictNode, conf: Optional[DictNode] = None, parent_key: Optional[str] = None) -> Dict[str, List[Any]]:
    ret_dict = {}
    if not isinstance(obj, dict):
        raise Exception("this method receives only dicts")
    if hasattr(obj, "start_mark") and hasattr(obj, "end_mark"):
        obj["start_line"] = obj.start_mark.line
        obj["end_line"] = obj.end_mark.line
    for key, value in obj.items():
        if _is_simple_type(value) or _is_list_of_simple_types(value):
            if parent_key == "tags":
                ret_dict[key] = value
            else:
                ret_dict[key] = _clean_simple_type_list([value])

        if _is_list_of_dicts(value):
            child_list = []
            conf_val = conf.get(key, []) if conf else []
            for internal_val, internal_conf_val in itertools.zip_longest(value, conf_val):
                if isinstance(internal_val, dict):
                    child_list.append(_hclify(internal_val, internal_conf_val, parent_key=key))
            if key == "tags":
                ret_dict[key] = [child_list]
            else:
                ret_dict[key] = child_list
        if isinstance(value, dict):
            child_dict = _hclify(value, parent_key=key)
            if parent_key == "tags":
                ret_dict[key] = child_dict
            else:
                ret_dict[key] = [child_dict]
    if conf and isinstance(conf, dict):
        found_ref = False
        for conf_key in conf.keys() - obj.keys():
            conf_value = conf[conf_key]
            if not isinstance(conf_value, dict):
                continue

            ref = next((x for x in conf_value.get("references", []) if not x.startswith(("var.", "local."))), None)
            if ref:
                ret_dict[conf_key] = [ref]
                found_ref = True
        if not found_ref:
            for value in conf.values():
                if isinstance(value, dict) and "references" in value.keys():
                    ret_dict["references_"] = value["references"]

    return ret_dict


def _prepare_resource_block(
    resource: DictNode, conf: Optional[DictNode], resource_changes: dict[str, dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], bool]:
    """hclify resource if pre-conditions met.

    :param resource: tf planned_values resource block
    :param conf: tf configuration resource block
    :param resource_changes: tf resource_changes block

    :returns:
        - resource_block: a list of strings representing the header columns
        - prepared: whether conditions met to prepare data
    """

    resource_block: Dict[str, Dict[str, Any]] = {}
    resource_block[resource["type"]] = {}
    prepared = False
    mode = ""
    if "mode" in resource:
        mode = resource.get("mode")
    # Rare cases where data block appears in resources with same name as resource block and only partial values
    # and where *_module resources don't have values field
    if mode == "managed":
        expressions = conf.get("expressions") if conf else None

        resource_conf = _hclify(resource.get("values", {}), expressions)
        resource_address = resource.get("address")
        resource_conf[TF_PLAN_RESOURCE_ADDRESS] = resource_address

        changes = resource_changes.get(resource_address)
        if changes:
            resource_conf[TF_PLAN_RESOURCE_CHANGE_ACTIONS] = changes.get("change", {}).get("actions") or []

        resource_block[resource["type"]][resource.get("name", "default")] = resource_conf
        prepared = True
    return resource_block, prepared


def _find_child_modules(
    child_modules: ListNode, resource_changes: dict[str, dict[str, Any]], root_module_conf: dict[str, Any]
) -> List[Dict[str, Dict[str, Any]]]:
    """ Find all child modules if any. Including any amount of nested child modules.

    :param child_modules: list of terraform child_module objects
    :param resource_changes: a resource address to resource changes dict
    :param root_module_conf: configuration block of the root module
    :returns:
        list of terraform resource blocks
    """

    resource_blocks = []
    for child_module in child_modules:
        nested_child_modules = child_module.get("child_modules", [])
        if nested_child_modules:
            nested_blocks = _find_child_modules(
                child_modules=nested_child_modules,
                resource_changes=resource_changes,
                root_module_conf=root_module_conf
            )
            for resource in nested_blocks:
                resource_blocks.append(resource)

        module_address = child_module.get("address", "")
        module_call_resources = _get_module_call_resources(
            module_address=module_address,
            root_module_conf=root_module_conf,
        )

        for resource in child_module.get("resources", []):
            module_call_conf = None
            if module_address and module_call_resources:
                module_call_conf = next(
                    (
                        module_call_resource
                        for module_call_resource in module_call_resources
                        if f"{module_address}.{module_call_resource['address']}" == resource["address"]
                    ),
                    None
                )

            resource_block, prepared = _prepare_resource_block(
                resource=resource,
                conf=module_call_conf,
                resource_changes=resource_changes,
            )
            if prepared is True:
                resource_blocks.append(resource_block)
    return resource_blocks


def _get_module_call_resources(module_address: str, root_module_conf: dict[str, Any]) -> list[dict[str, Any]]:
    """Extracts the resources from the 'module_calls' block under 'configuration'"""

    for module_name in module_address.split("."):
        if module_name == "module":
            # module names are always prefixed with 'module.', therefore skip it
            continue
        root_module_conf = root_module_conf.get("module_calls", {}).get(module_name, {}).get("module", {})

    return root_module_conf.get("resources", [])


def _get_resource_changes(template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Returns a resource address to resource changes dict"""

    resource_changes_map = {}

    resource_changes = template.get("resource_changes")
    if resource_changes and isinstance(resource_changes, list):
        resource_changes_map = {
            change.get("address", ""): change
            for change in resource_changes
        }

    return resource_changes_map


def parse_tf_plan(tf_plan_file: str, out_parsing_errors: Dict[str, str]) -> Tuple[Optional[Dict[str, Any]], Optional[List[Tuple[int, str]]]]:
    """
    :type tf_plan_file: str - path to plan file
    :rtype: tf_definition dictionary and template_lines of the plan file
    """
    tf_definition: Dict[str, Any] = {"resource": []}
    template, template_lines = parse(tf_plan_file, out_parsing_errors)
    if not template:
        return None, None

    resource_changes = _get_resource_changes(template=template)

    for resource in template.get("planned_values", {}).get("root_module", {}).get("resources", []):
        conf = next(
            (
                x
                for x in template.get("configuration", {}).get("root_module", {}).get("resources", [])
                if x["type"] == resource["type"] and x["name"] == resource["name"]
            ),
            None,
        )
        resource_block, prepared = _prepare_resource_block(
            resource=resource,
            conf=conf,
            resource_changes=resource_changes,
        )
        if prepared is True:
            tf_definition["resource"].append(resource_block)
    child_modules = template.get("planned_values", {}).get("root_module", {}).get("child_modules", [])
    root_module_conf = template.get("configuration", {}).get("root_module", {})
    # Terraform supports modules within modules so we need to search
    # in nested modules to find all resource blocks
    resource_blocks = _find_child_modules(
        child_modules=child_modules,
        resource_changes=resource_changes,
        root_module_conf=root_module_conf,
    )
    for resource in resource_blocks:
        tf_definition["resource"].append(resource)
    return tf_definition, template_lines


def _clean_simple_type_list(value_list: List[Any]) -> List[Any]:
    """
    Given a list of simple types return a cleaned list of simple types.
    Converts booleans that are input as strings back to booleans to maintain consistent expectations for later evaluation.
    Sometimes Terraform Plan will output Map values as strings regardless of boolean input.
    """
    for i in range(len(value_list)):
        if isinstance(value_list[i], str):
            lower_case_value = value_list[i].lower()
            if lower_case_value == "true":
                value_list[i] = True
            if lower_case_value == "false":
                value_list[i] = False
    return value_list
