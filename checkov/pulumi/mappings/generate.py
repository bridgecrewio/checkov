"""Generates the Pulumi -> Terraform mapping files used by the Pulumi runner.

Dev-only, not used at scan time. Inputs per provider:
- the Pulumi provider ``schema.json`` and ``bridge-metadata.json`` of a release
  (https://github.com/pulumi/pulumi-<provider>/tree/<version>/provider/cmd/pulumi-resource-<provider>)
- the Terraform provider schema (``terraform providers schema -json``) of the upstream version the Pulumi provider
  bridges (see "Upgrade terraform-provider-..." in its release notes).

Last generated from pulumi-aws v7.53.0 (TF aws 6.71.0), pulumi-gcp v10.2.2 (TF google-beta 8.9.0)
and pulumi-azure v6.40.2 (TF azurerm 4.81.0).

Usage:
    python -m checkov.pulumi.mappings.generate --tf-schema schemas.json \
        --provider aws aws-schema.json aws-bridge-metadata.json \
        --provider gcp gcp-schema.json gcp-bridge-metadata.json \
        --provider azure azure-schema.json azure-bridge-metadata.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from checkov.pulumi.mappings import camel_to_snake

TF_PROVIDERS = {
    "aws": ("registry.terraform.io/hashicorp/aws", "aws_"),
    "gcp": ("registry.terraform.io/hashicorp/google-beta", "google_"),
    "azure": ("registry.terraform.io/hashicorp/azurerm", "azurerm_"),
}
LETTER_DIGIT = re.compile(r"(?<=[a-z])(?=[0-9])")
DIGIT_LETTER = re.compile(r"(?<=[0-9])(?=[a-z])")
# renames in the Pulumi bridge, which can't be derived from the names
MANUAL_RENAMES = {
    "aws:apigateway/basePathMapping:BasePathMapping": {"restApi": "api_id"},
    "aws:apigateway/vpcLink:VpcLink": {"targetArn": "target_arns"},
    "aws:elasticbeanstalk/environment:Environment": {"version": "version_label"},
    "aws:lambda/function:Function": {"code": "filename"},
    "aws:lambda/layerVersion:LayerVersion": {"code": "filename"},
}
# renames for all resources of a provider
PROVIDER_RENAMES = {"pulumiLabels": "terraform_labels"}
# deprecated resources without own Terraform schema, ex. aws_s3_bucket_v2_compat
TF_TYPE_SUFFIXES = ("_v2_compat", "_legacy")
MAX_DEPTH = 8
RAW_REFS = ("pulumi.json#/Any", "pulumi.json#/Json")
CHECKOV_ROOT = Path(__file__).parents[2]  # checkov package


def checked_tf_types() -> set[str]:
    """All Terraform resource types referenced by a Python or YAML Terraform check"""

    from checkov.terraform.checks.resource.registry import resource_registry

    types = set(resource_registry.checks.keys())
    pattern = re.compile(r"^(aws|google|azurerm)_\w+$")

    def collect(obj: Any) -> None:
        if isinstance(obj, dict):
            for value in obj.values():
                collect(value)
        elif isinstance(obj, list):
            for value in obj:
                collect(value)
        elif isinstance(obj, str) and pattern.match(obj):
            types.add(obj)

    for path in (CHECKOV_ROOT / "terraform/checks/graph_checks").rglob("*.yaml"):
        collect(yaml.safe_load(path.read_text(encoding="utf-8")))
    return types


def name_candidates(snake: str) -> list[str]:
    """TF names the Pulumi property could originate from, ex. 'use32_bit_worker' -> 'use_32_bit_worker'"""

    split = LETTER_DIGIT.sub("_", snake)
    bases = [snake, split, DIGIT_LETTER.sub("_", split)]
    candidates: list[str] = []
    for name in bases:
        candidates.append(name)
        if name.endswith("ies"):
            candidates.append(f"{name[:-3]}y")
        if name.endswith("ices"):
            candidates.append(f"{name[:-4]}ex")  # indices
        if name.endswith("ses"):
            candidates.append(f"{name[:-3]}sis")  # kineses
        if name.endswith("ii"):
            candidates.append(f"{name[:-1]}us")  # radii
        if name.endswith("es"):
            candidates.append(name[:-2])
        if name.endswith("s"):
            candidates.append(name[:-1])
    return candidates


def renamed_candidates(snake: str, tf_fields: set[str]) -> list[str]:
    """Explicitly renamed fields in the bridge, ex. Lambda 'name' -> 'function_name', 'restApi' -> 'rest_api_id'"""

    singulars = name_candidates(snake)
    return sorted(
        t for t in tf_fields
        if any(t in (f"{s}_id", f"{s}_name", f"{s}_arn") or t.endswith(f"_{s}") for s in singulars)
    )


class Generator:
    def __init__(self, pulumi_schema: dict[str, Any]) -> None:
        self.types: dict[str, Any] = pulumi_schema.get("types", {})
        self.unmatched: list[str] = []

    @staticmethod
    def _is_compatible(prop: dict[str, Any], tf_field: dict[str, Any]) -> bool:
        """A Pulumi list can't originate from a Terraform scalar, ex. 'routingRules' is the block 'routing_rule'"""

        if prop.get("type") != "array" or "nesting_mode" in tf_field:
            return True
        return isinstance(tf_field.get("type"), list)

    def _has_object_variant(self, prop: dict[str, Any]) -> bool:
        """ex. policies are strings, which can be passed as PolicyDocument object, but not enums like CannedAcl"""

        for variant in prop.get("oneOf") or []:
            ref = variant.get("$ref", "")
            if ref.startswith("#/types/") and self.types.get(ref[len("#/types/"):], {}).get("type") == "object":
                return True
        return False

    def _resolve(self, prop: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, bool]:
        """Returns (is_array, object properties or None, is_raw_map)"""

        is_array = prop.get("type") == "array"
        item = prop.get("items", {}) if is_array else prop
        ref = item.get("$ref", "")
        if ref.endswith(RAW_REFS) or (item.get("type") == "object" and "additionalProperties" in item):
            return is_array, None, True
        if ref.startswith("#/types/"):
            obj_type = self.types.get(ref[len("#/types/"):], {})
            if obj_type.get("type") == "object":
                return is_array, obj_type.get("properties", {}), False
        return is_array, None, False

    def fields(self, props: dict[str, Any], tf_block: dict[str, Any], path: str, report: bool = True) -> dict[str, Any]:
        tf_fields: dict[str, Any] = {**tf_block.get("attributes", {}), **tf_block.get("block_types", {})}
        # prefer settable fields, ex. azurerm_frontdoor block 'backend_pool' over computed-only 'backend_pools'
        settable = {
            name for name, field in tf_fields.items()
            if not field.get("computed") or field.get("optional") or field.get("required") or "nesting_mode" in field
        }
        result: dict[str, Any] = {}
        if path.count(".") > MAX_DEPTH:
            # recursive types (ex. WAFv2 statements) are not inspected that deep by any check
            return result
        matches: dict[str, str] = dict(MANUAL_RENAMES.get(path, {}))
        matches.update({k: v for k, v in PROVIDER_RENAMES.items() if k in props and v in tf_fields})
        for name, prop in props.items():
            if name in matches:
                continue
            snake = camel_to_snake(name)
            candidates = [c for c in name_candidates(snake) if c in tf_fields and self._is_compatible(prop, tf_fields[c])]
            if not report and snake in candidates:
                # outputs have the exact name, ex. 'locations' and not the settable 'location'
                tf_name: str | None = snake
            else:
                tf_name = next((c for c in candidates if c in settable), None) or next(iter(candidates), None)
            if tf_name:
                matches[name] = tf_name
        unmatched_tf = set(tf_fields) - set(matches.values())
        for name, prop in props.items():
            if name not in matches:
                candidates = [
                    c for c in renamed_candidates(camel_to_snake(name), unmatched_tf)
                    if self._is_compatible(prop, tf_fields[c])
                ]
                if len(candidates) == 1:
                    matches[name] = candidates[0]
                    unmatched_tf.discard(candidates[0])

        for name, prop in props.items():
            snake = camel_to_snake(name)
            tf_name = matches.get(name)
            if tf_name is None:
                if report:
                    self.unmatched.append(f"{path}.{name}")
                continue

            node: dict[str, Any] = {}
            if tf_name != snake:
                node["name"] = tf_name
            is_array, obj_props, is_raw = self._resolve(prop)
            tf_field = tf_fields[tf_name]
            if "nesting_mode" in tf_field:
                tf_is_list = tf_field["nesting_mode"] in ("list", "set")
                nested_block = tf_field.get("block", {})
            else:
                tf_type = tf_field.get("type")
                tf_is_list = isinstance(tf_type, list) and tf_type[0] in ("list", "set")
                nested_block = {}
                inner = tf_type[1] if tf_is_list else tf_type
                if isinstance(inner, list) and inner[0] == "object":
                    nested_block = {"attributes": {k: {"type": v} for k, v in inner[1].items()}}
            if tf_is_list and not is_array:
                # TF list with max items one, represented as a single value in Pulumi
                node["one"] = True
            if prop.get("type") == "string" and self._has_object_variant(prop):
                # JSON string, which can be passed as object, ex. policy documents
                node["json"] = True
            elif is_raw:
                node["raw"] = True
            elif obj_props is not None:
                nested = self.fields(obj_props, nested_block, f"{path}.{name}", report)
                if nested:
                    node["fields"] = nested
            if node:
                result[name] = node
        return result


def _entry(generator: Generator, token: str, pulumi_resource: dict[str, Any], tf_type: str, tf_resource: dict[str, Any]) -> dict[str, Any]:
    entry: dict[str, Any] = {"type": tf_type}
    input_props = pulumi_resource.get("inputProperties", {})
    fields = generator.fields(input_props, tf_resource["block"], token)
    # some outputs are part of the inputs in a preview, ex. 'tagsAll'
    output_props = {k: v for k, v in pulumi_resource.get("properties", {}).items() if k not in input_props}
    fields.update(generator.fields(output_props, tf_resource["block"], token, report=False))
    if fields:
        entry["fields"] = fields
    return entry


def generate(
    provider: str, pulumi_schema_path: Path, bridge_metadata_path: Path, tf_schemas: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    tf_source, tf_prefix = TF_PROVIDERS[provider]
    tf_resources = tf_schemas["provider_schemas"][tf_source]["resource_schemas"]
    pulumi_schema = json.loads(pulumi_schema_path.read_text(encoding="utf-8"))
    aliasing = json.loads(bridge_metadata_path.read_text(encoding="utf-8"))["auto-aliasing"]["resources"]
    generator = Generator(pulumi_schema)

    resources: dict[str, Any] = {}
    past_tokens: dict[str, str] = {}
    for tf_type, meta in sorted(aliasing.items()):
        token = meta.get("current")
        if not token or not tf_type.startswith(tf_prefix):
            continue
        tf_type = next((tf_type[: -len(s)] for s in TF_TYPE_SUFFIXES if tf_type.endswith(s)), tf_type)
        pulumi_resource = pulumi_schema["resources"].get(token)
        tf_resource = tf_resources.get(tf_type)
        if not pulumi_resource or not tf_resource:
            generator.unmatched.append(f"{token} ({tf_type}): missing schema")
            continue
        resources[token] = _entry(generator, token, pulumi_resource, tf_type, tf_resource)
        for past in meta.get("past", []):
            if past.get("name"):
                past_tokens[past["name"]] = token

    aliases: dict[str, str] = {}
    for past_token, token in sorted(past_tokens.items()):
        if past_token in resources:
            continue
        past_resource = pulumi_schema["resources"].get(past_token)
        if past_resource:
            # deprecated resources, which still exist, can have a different schema
            tf_type = resources[token]["type"]
            resources[past_token] = _entry(generator, past_token, past_resource, tf_type, tf_resources[tf_type])
        else:
            aliases[past_token] = token
    return {"resources": resources, "aliases": aliases}, generator.unmatched


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tf-schema", required=True, type=Path)
    parser.add_argument("--provider", nargs=3, action="append", required=True, metavar=("NAME", "SCHEMA", "METADATA"))
    parser.add_argument("--report", type=Path, help="write unmatched Pulumi properties to this file")
    args = parser.parse_args()

    tf_schemas = json.loads(args.tf_schema.read_text(encoding="utf-8"))
    report: list[str] = []
    for name, schema_path, metadata_path in args.provider:
        mapping, unmatched = generate(name, Path(schema_path), Path(metadata_path), tf_schemas)
        out = Path(__file__).parent / f"{name}.json"
        # one line per resource keeps diffs readable and the file small
        lines = [f"  {json.dumps(k)}: {json.dumps(v, sort_keys=True)}" for k, v in sorted(mapping["resources"].items())]
        out.write_text(
            encoding="utf-8",
            data='{\n "aliases": ' + json.dumps(mapping["aliases"], indent=2, sort_keys=True).replace("\n", "\n ")
            + ',\n "resources": {\n' + ",\n".join(lines) + "\n }\n}\n"
        )
        print(f"{name}: {len(mapping['resources'])} resources, {len(unmatched)} unmatched properties -> {out}")
        report.extend(unmatched)
    if args.report:
        args.report.write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
