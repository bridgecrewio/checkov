from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.consts import LINE_FIELD_NAMES
from checkov.pulumi.mappings import camel_to_snake, get_resource_mapping
from checkov.terraform.plan_parser import _clean_simple_type_list, _hclify
from hcl2 import END_LINE, START_LINE

# https://github.com/pulumi/pulumi/blob/master/sdk/go/common/resource/sig/sig.go
UNKNOWN_VALUES = {
    "1c4a061d-8072-4f0a-a4cb-0ff528b18fe7",  # bool
    "3eeb2bf0-c639-47a8-9e75-3b44932eb421",  # number
    "04da6b54-80e4-46f7-96ec-b56ff0331ba9",  # string
    "6a19a0b0-7e62-4c92-b797-7f8e31da9cc2",  # array
    "030794c1-ac77-496b-92df-f27374a8bd58",  # asset
    "e48ece36-62e2-4504-bad9-02848725956a",  # archive
    "dd056dcd-154b-4c76-9bd3-c8f88648b5ff",  # object
}
# public signatures of special values, not credentials
SIG_KEY = "4dabf18193072939515e22adb298388d"
SECRET_SIG = "1b47061264138c4ac30d75fd1eb44270"  # nosec B105  # checkov:skip=CKV_SECRET_6
OUTPUT_SIG = "d0e6a833031e9bbcd3f4e8bde6ca49a4"
ASSET_SIG = "c44067f5952c0a294b673a41bacd8c17"
ARCHIVE_SIG = "0def7320c3a5731c473e5ecbe6d01bc7"
RESOURCE_REFERENCE_SIG = "5cf8f73096256a8f31e491e813e4eb8e"

PROVIDER_TYPE_PREFIX = "pulumi:providers:"
TF_PROVIDER_NAMES = {"aws": "aws", "gcp": "google", "azure": "azurerm"}

MAX_DEPTH = 64
DEFAULT_PROVIDER_NAME = re.compile(r"^default(_\d+_\d+_\d+\S*)?$")

_INVALID_NAME_CHARS = re.compile(r"[^A-Za-z0-9_-]")


class _Unknown:
    """Marks a value, which is only known after the deployment"""


UNKNOWN = _Unknown()
SECRET_PLACEHOLDER = "[secret]"  # nosec B105  # placeholder, same as in the output of Pulumi


@dataclass
class PulumiResource:
    urn: str
    type: str
    inputs: dict[str, Any]
    property_dependencies: dict[str, list[str]] = field(default_factory=dict)
    start_line: int = 0
    end_line: int = 0

    @property
    def name(self) -> str:
        # urn:pulumi:<stack>::<project>::<type>::<name>, the name itself can contain '::'
        return self.urn.split("::", 3)[-1]


def _unwrap_sig(value: dict[str, Any]) -> Any:
    sig = value.get(SIG_KEY)
    if sig == SECRET_SIG or (sig == OUTPUT_SIG and value.get("secret")):
        # the value is set, but must not end up in the results, same as in the output of 'pulumi preview'
        return SECRET_PLACEHOLDER
    if sig == OUTPUT_SIG:
        return value["value"] if "value" in value else UNKNOWN
    if sig == ASSET_SIG:
        return value.get("path") or value.get("uri") or value.get("text") or UNKNOWN
    if sig == ARCHIVE_SIG:
        return value.get("path") or value.get("uri") or UNKNOWN
    if sig == RESOURCE_REFERENCE_SIG:
        return value.get("id") or value.get("urn") or UNKNOWN
    return value


def translate_value(value: Any, node: dict[str, Any], depth: int = 0) -> Any:
    """Converts a Pulumi input value to its Terraform plan equivalent"""

    if depth > MAX_DEPTH:
        # no check inspects values that deep, this prevents a recursion error later on
        return UNKNOWN
    if isinstance(value, str) and value in UNKNOWN_VALUES:
        return UNKNOWN
    if isinstance(value, dict):
        if SIG_KEY in value:
            unwrapped = _unwrap_sig(value)
            if unwrapped is value:
                return UNKNOWN
            return translate_value(unwrapped, node, depth + 1)
        if node.get("raw"):
            # maps, ex. tags, keep their keys
            result = {}
            for key, val in value.items():
                if not isinstance(key, str) or key in LINE_FIELD_NAMES:
                    continue
                translated = translate_value(val, {"raw": True}, depth + 1)
                if translated is not UNKNOWN:
                    result[key] = translated
            return result
        return translate_inputs(value, node.get("fields", {}), depth + 1)
    if isinstance(value, list):
        items = (translate_value(item, node, depth + 1) for item in value)
        return [item for item in items if item is not UNKNOWN]
    return value


def _contains_unknown(value: Any) -> bool:
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, str) and current in UNKNOWN_VALUES:
            return True
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return False


def translate_inputs(inputs: dict[str, Any], fields: dict[str, Any], depth: int = 0) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in inputs.items():
        if not isinstance(key, str) or key.startswith("__"):
            # Pulumi internals, ex. '__defaults'
            continue
        node = fields.get(key, {})
        # ex. policy documents can be passed as objects, Terraform has them as JSON strings
        translated = translate_value(value, {"raw": True} if node.get("json") else node, depth)
        if translated is UNKNOWN:
            continue
        if node.get("json") and isinstance(translated, (dict, list)):
            if _contains_unknown(value):
                # partially unknown documents have a different meaning, Terraform has the whole value unknown
                continue
            translated = json.dumps(translated)
        elif node.get("one") and translated is not None and not isinstance(translated, list):
            translated = [translated]
        result[node.get("name") or camel_to_snake(key)] = translated
    return result


def _translate_provider(resource: PulumiResource) -> tuple[str, dict[str, Any]] | None:
    """Same format as the providers of the Terraform plan parser"""

    tf_name = TF_PROVIDER_NAMES.get(resource.type[len(PROVIDER_TYPE_PREFIX):])
    if not tf_name:
        return None
    # default providers are named after their plugin version, ex. 'default_7_53_0'
    alias = "default" if DEFAULT_PROVIDER_NAME.match(resource.name) else _INVALID_NAME_CHARS.sub("_", resource.name)
    inputs = {key: value for key, value in resource.inputs.items() if key != "version"}
    conf: dict[str, Any] = {
        key: value if isinstance(value, list) else _clean_simple_type_list([value])
        for key, value in translate_inputs(inputs, {}).items()
    }
    conf["start_line"] = [resource.start_line]
    conf["end_line"] = [resource.end_line]
    conf[START_LINE] = [resource.start_line]
    conf[END_LINE] = [resource.end_line]
    conf["alias"] = [alias]
    conf[CustomAttributes.TF_RESOURCE_ADDRESS] = f"{tf_name}.{alias}"
    return f"{tf_name}.{alias}", {tf_name: conf}


def translate_resources(resources: list[PulumiResource]) -> dict[str, list[dict[str, Any]]]:
    """Creates a Terraform plan definition out of Pulumi resources of a single file"""

    providers: dict[str, dict[str, Any]] = {}
    for resource in resources:
        if resource.type.startswith(PROVIDER_TYPE_PREFIX):
            provider = _translate_provider(resource)
            if provider:
                providers.setdefault(*provider)
    resources = [resource for resource in resources if not resource.type.startswith(PROVIDER_TYPE_PREFIX)]

    mapped: list[tuple[PulumiResource, dict[str, Any], str]] = []
    addresses: dict[str, str] = {}
    used_names: set[str] = set()
    next_index: dict[str, int] = {}
    for resource in resources:
        mapping = get_resource_mapping(resource.type)
        if not mapping:
            logging.info(f"[pulumi] no Terraform mapping for resource type {resource.type}, skipping")
            continue
        tf_type = mapping["type"]
        name = _INVALID_NAME_CHARS.sub("_", resource.name) or "default"
        unique_name = name
        while f"{tf_type}.{unique_name}" in used_names:
            idx = next_index.get(f"{tf_type}.{name}", 2)
            next_index[f"{tf_type}.{name}"] = idx + 1
            unique_name = f"{name}_{idx}"
        used_names.add(f"{tf_type}.{unique_name}")
        addresses[resource.urn] = f"{tf_type}.{unique_name}"
        mapped.append((resource, mapping, unique_name))

    tf_resources: list[dict[str, Any]] = []
    for resource, mapping, name in mapped:
        fields = mapping.get("fields", {})
        values = translate_inputs(resource.inputs, fields)
        values["start_line"] = resource.start_line
        values["end_line"] = resource.end_line

        # property dependencies point to other resources, like references in a Terraform configuration
        expressions: dict[str, Any] = {}
        for key, dependencies in resource.property_dependencies.items():
            references: list[str] = []
            for urn in dependencies:
                address = addresses.get(urn)
                if address:
                    references.extend((f"{address}.id", address))
            if not references:
                continue
            node = fields.get(key, {})
            # unknown values are replaced by the reference, like in the Terraform plan parser
            expressions[node.get("name") or camel_to_snake(key)] = {"references": references}

        conf = _hclify(obj=values, conf=expressions, resource_type=mapping["type"])
        conf[CustomAttributes.TF_RESOURCE_ADDRESS] = addresses[resource.urn]  # type:ignore[assignment]  # special field
        tf_resources.append({mapping["type"]: {name: conf}})

    return {"provider": list(providers.values()), "resource": tf_resources, "data": []}
