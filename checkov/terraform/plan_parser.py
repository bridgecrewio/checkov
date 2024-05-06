from __future__ import annotations

import itertools
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, cast

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.parsers.node import ListNode
from checkov.common.util.consts import LINE_FIELD_NAMES
from checkov.common.util.type_forcers import force_list
from checkov.terraform.context_parsers.tf_plan import parse

SIMPLE_TYPES = (str, int, float, bool)
TF_PLAN_RESOURCE_ADDRESS = CustomAttributes.TF_RESOURCE_ADDRESS
TF_PLAN_RESOURCE_CHANGE_ACTIONS = "__change_actions__"
TF_PLAN_RESOURCE_CHANGE_KEYS = "__change_keys__"
TF_PLAN_RESOURCE_PROVISIONERS = "provisioners"

RESOURCE_TYPES_JSONIFY = {
    "aws_batch_job_definition": "container_properties",
    "aws_ecs_task_definition": "container_definitions",
    "aws_iam_policy": "policy",
    "aws_iam_role": "assume_role_policy",
    "aws_iam_role_policy": "policy",
    "aws_iam_group_policy": "policy",
    "aws_iam_user_policy": "policy",
    "aws_ssoadmin_permission_set_inline_policy": "inline_policy",
    "azurerm_portal_dashboard": "dashboard_properties",
    "aws_vpc_endpoint_policy": "policy",
    "aws_ecr_registry_policy": "policy",
    "aws_acmpca_policy": "policy",
    "aws_api_gateway_rest_api_policy": "policy",
    "aws_backup_vault_policy": "policy",
    "aws_cloudwatch_log_destination_policy": "access_policy",
    "aws_cloudwatch_log_resource_policy": "policy_document",
    "aws_oam_sink_policy": "policy",
    "aws_codebuild_resource_policy": "policy",
    "aws_dynamodb_resource_policy": "policy",
    "aws_ecr_repository_policy": "policy",
    "aws_ecrpublic_repository_policy": "policy",
    "aws_efs_file_system_policy": "policy",
    "aws_elasticsearch_domain_policy": "access_policies",
    "aws_media_store_container_policy": "policy",
    "aws_cloudwatch_event_bus_policy": "policy",
    "aws_schemas_registry_policy": "policy",
    "aws_glue_resource_policy": "policy",
    "aws_iot_policy": "policy",
    "aws_kms_key": "policy",
    "aws_kinesis_resource_policy": "policy",
    "aws_msk_cluster_policy": "policy",
    "aws_networkfirewall_resource_policy": "policy",
    "aws_opensearch_domain_policy": "access_policies",
    "aws_opensearchserverless_access_policy": "policy",
    "aws_redshift_resource_policy": "policy",
    "aws_redshiftserverless_resource_policy": "policy",
    "aws_s3_bucket_policy": "policy",
    "aws_s3control_access_point_policy": "policy",
    "aws_s3control_bucket_policy": "policy",
    "aws_ses_identity_policy": "policy",
    "aws_sesv2_email_identity_policy": "policy",
    "aws_sns_topic_data_protection_policy": "policy",
    "aws_sns_topic_policy": "policy",
    "aws_sqs_queue_policy": "policy",
    "aws_secretsmanager_secret_policy": "policy",
    "aws_vpclattice_auth_policy": "policy",
    "aws_vpclattice_resource_policy": "policy"
}


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


def _hclify(
    obj: dict[str, Any],
    conf: dict[str, Any] | None = None,
    parent_key: str | None = None,
    resource_type: str | None = None,
) -> dict[str, list[Any]]:
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
                # only wrap non-lists into a list
                ret_dict[key] = _clean_simple_type_list([value])

        if _is_list_of_dicts(value):
            child_list = []
            conf_val = conf.get(key, []) if conf else []
            if not isinstance(conf_val, list):
                # this occurs, when a resource in the current state has no value for that argument
                conf_val = [conf_val]

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
        _add_references(obj=obj, conf=conf, return_resource=ret_dict)

    if resource_type and resource_type in RESOURCE_TYPES_JSONIFY:
        # values shouldn't be encapsulated in lists
        dict_value = jsonify(obj=obj, resource_type=resource_type)
        if dict_value is not None:
            ret_dict[RESOURCE_TYPES_JSONIFY[resource_type]] = force_list(dict_value)

    return ret_dict


def jsonify(obj: dict[str, Any], resource_type: str) -> dict[str, Any] | None:
    """Tries to create a dict from a string of a supported resource type attribute"""

    jsonify_key = RESOURCE_TYPES_JSONIFY[resource_type]
    if jsonify_key in obj:
        try:
            return cast("dict[str, Any]", json.loads(obj[jsonify_key]))
        except json.JSONDecodeError:
            logging.debug(
                f"Attribute {jsonify_key} of resource type {resource_type} is not json encoded {obj[jsonify_key]}"
            )

    return None


def _prepare_resource_block(
    resource: dict[str, Any], conf: dict[str, Any] | None, resource_changes: dict[str, dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], str, bool]:
    """hclify resource if pre-conditions met.

    :param resource: tf planned_values resource block
    :param conf: tf configuration resource block
    :param resource_changes: tf resource_changes block
    :returns:
        - resource_block: a list of strings representing the header columns
        - prepared: whether conditions met to prepare data
    """

    resource_block: Dict[str, Dict[str, Any]] = {}
    resource_type = resource["type"]
    resource_block[resource_type] = {}
    prepared = False
    mode = ""
    block_type = ""
    if "mode" in resource:
        mode = resource["mode"]
        block_type = "data" if mode == "data" else "resource"

    # Rare cases where data block appears in resources with same name as resource block and only partial values
    # and where *_module resources don't have values field
    if mode in ("managed", "data"):
        expressions = conf.get("expressions") if conf else None

        resource_conf = _hclify(
            obj=resource.get("values", {"start_line": 0, "end_line": 0}),
            conf=expressions,
            resource_type=resource_type,
        )
        resource_address: str | None = resource.get("address")
        resource_conf[TF_PLAN_RESOURCE_ADDRESS] = resource_address  # type:ignore[assignment]  # special field

        changes = resource_changes.get(resource_address)  # type:ignore[arg-type]  # becaus eit can be None
        if changes:
            resource_conf[TF_PLAN_RESOURCE_CHANGE_ACTIONS] = changes.get("change", {}).get("actions") or []
            resource_conf[TF_PLAN_RESOURCE_CHANGE_KEYS] = changes.get(TF_PLAN_RESOURCE_CHANGE_KEYS) or []

        provisioners = conf.get(TF_PLAN_RESOURCE_PROVISIONERS) if conf else None
        if provisioners:
            resource_conf["provisioner"] = _get_provisioner(provisioners)

        resource_block[resource_type][resource.get("name", "default")] = resource_conf
        prepared = True
    return resource_block, block_type, prepared


def _find_child_modules(
    child_modules: ListNode, resource_changes: dict[str, dict[str, Any]], root_module_conf: dict[str, Any]
) -> dict[str, list[dict[str, dict[str, Any]]]]:
    """ Find all child modules if any. Including any amount of nested child modules.

    :param child_modules: list of terraform child_module objects
    :param resource_changes: a resource address to resource changes dict
    :param root_module_conf: configuration block of the root module
    :returns:
        list of terraform resource blocks
    """

    blocks: dict[str, list[dict[str, dict[str, Any]]]] = {"resource": [], "data": []}
    for child_module in child_modules:
        nested_child_modules = child_module.get("child_modules", [])
        if nested_child_modules:
            nested_blocks = _find_child_modules(
                child_modules=nested_child_modules,
                resource_changes=resource_changes,
                root_module_conf=root_module_conf,
            )
            for block_type, resource_blocks in nested_blocks.items():
                blocks[block_type].extend(resource_blocks)

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
                        if f"{module_address}.{module_call_resource['address']}" == (resource["address"].rsplit('[', 1)[0] if resource["address"][-1] == "]" else resource["address"])
                    ),
                    None
                )

            resource_block, block_type, prepared = _prepare_resource_block(
                resource=resource,
                conf=module_call_conf,
                resource_changes=resource_changes,
            )
            if prepared is True:
                if block_type == "resource":
                    blocks["resource"].append(resource_block)
                elif block_type == "data":
                    blocks["data"].append(resource_block)
    return blocks


def _get_module_call_resources(module_address: str, root_module_conf: dict[str, Any]) -> list[dict[str, Any]]:
    """Extracts the resources from the 'module_calls' block under 'configuration'"""

    for module_name in module_address.split("."):
        if module_name == "module":
            # module names are always prefixed with 'module.', therefore skip it
            continue
        root_module_conf = root_module_conf.get("module_calls", {}).get(module_name, {}).get("module", {})

    return cast("list[dict[str, Any]]", root_module_conf.get("resources", []))


def _is_provider_key(key: str) -> bool:
    """key is a valid provider"""
    return (key.startswith('module.') or key.startswith('__') or key in {'start_line', 'end_line'})


def _get_provider(template: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Returns the provider dict"""

    provider_map: dict[str, dict[str, Any]] = {}
    provider_config = template.get("configuration", {}).get("provider_config")

    if provider_config and isinstance(provider_config, dict):
        for provider_key, provider_data in provider_config.items():
            if _is_provider_key(key=provider_key):
                # Not a provider, skip
                continue
            provider_map[provider_key] = {}
            for field, value in provider_data.get('expressions', {}).items():
                if field in LINE_FIELD_NAMES or not isinstance(value, dict):
                    continue  # don't care about line #s or non dicts
                expression_value = value.get('constant_value', None)
                if expression_value:
                    provider_map[provider_key][field] = expression_value

    return provider_map


def _get_resource_changes(template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Returns a resource address to resource changes dict"""

    resource_changes_map = {}
    resource_changes = template.get("resource_changes")

    if resource_changes and isinstance(resource_changes, list):
        for resource in resource_changes:
            resource_changes_map[resource["address"]] = resource
            changes = []

            # before + after are None when resources are created/destroyed, so make them safe
            change_before = resource["change"]["before"] or {}
            change_after = resource["change"]["after"] or {}

            for field, value in change_before.items():
                if field in LINE_FIELD_NAMES:
                    continue  # don't care about line #s
                if value != change_after.get(field):
                    changes.append(field)

            resource_changes_map[resource["address"]][TF_PLAN_RESOURCE_CHANGE_KEYS] = changes

    return resource_changes_map


def _add_references(obj: dict[str, Any], conf: dict[str, Any], return_resource: dict[str, Any]) -> None:
    """Adds references to the resources in the TF plan definition"""

    for conf_key, conf_value in conf.items():
        if not isinstance(conf_value, dict) or "references" not in conf_value:
            # only interested in dict with a "references" key
            continue

        ref = next((x for x in conf_value["references"] or [] if not x.startswith(("var.", "local."))), None)
        if ref:
            if conf_key not in obj:
                return_resource[conf_key] = [ref]
            elif obj[conf_key] is None:
                return_resource[conf_key] = [ref]
            elif isinstance(obj[conf_key], list) and any(obj_value is None for obj_value in obj[conf_key]):
                return_resource[conf_key] = [[obj_value for obj_value in obj[conf_key] if obj_value is not None] + [ref]]

            return_resource.setdefault(CustomAttributes.REFERENCES, []).append(conf_value["references"])


def parse_tf_plan(tf_plan_file: str, out_parsing_errors: Dict[str, str]) -> Tuple[Optional[Dict[str, Any]], Optional[List[Tuple[int, str]]]]:
    """
    :type tf_plan_file: str - path to plan file
    :rtype: tf_definition dictionary and template_lines of the plan file
    """
    tf_definition: Dict[str, Any] = {"provider": [], "resource": [], "data": []}
    template, template_lines = parse(tf_plan_file, out_parsing_errors)
    if not template:
        return None, None

    provider = _get_provider(template=template)
    if bool(provider):
        tf_definition["provider"].append(provider)

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
        resource_block, block_type, prepared = _prepare_resource_block(
            resource=resource,
            conf=conf,
            resource_changes=resource_changes,
        )
        if prepared is True:
            if block_type == "resource":
                tf_definition["resource"].append(resource_block)
            elif block_type == "data":
                tf_definition["data"].append(resource_block)
    child_modules = template.get("planned_values", {}).get("root_module", {}).get("child_modules", [])
    root_module_conf = template.get("configuration", {}).get("root_module", {})
    # Terraform supports modules within modules so we need to search
    # in nested modules to find all resource blocks
    module_blocks = _find_child_modules(
        child_modules=child_modules,
        resource_changes=resource_changes,
        root_module_conf=root_module_conf,
    )
    for block_type, resource_blocks in module_blocks.items():
        tf_definition[block_type].extend(resource_blocks)
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


def _get_provisioner(input_data: List[Any]) -> List[Any]:
    result = []
    for item in input_data:
        key = item['type']
        command_value = item['expressions']['command']
        if not isinstance(command_value, list):
            command_value = [command_value]
        transformed_item = {key: {'command': command_value}}
        result.append(transformed_item)
    return result
