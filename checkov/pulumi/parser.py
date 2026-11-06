from __future__ import annotations

import json
import logging
import re
from typing import Any

from checkov.cloudformation.parser import cfn_yaml
from checkov.cloudformation.parser.cfn_yaml import ContentType
from checkov.common.util.consts import LINE_FIELD_NAMES, MAX_IAC_FILE_SIZE
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.common.util.secrets import GENERIC_OBFUSCATION_LENGTH
from checkov.pulumi.translator import OUTPUT_SIG, PROVIDER_TYPE_PREFIX, SECRET_SIG, SIG_KEY, PulumiResource

PULUMI_URN_PREFIX = "urn:pulumi:"
MASK = "*" * GENERIC_OBFUSCATION_LENGTH
# the plaintext of a secret value, ex. {"<sig key>": "<secret sig>", "plaintext": "\"password\""}
# provider config, which is shown in code blocks, the other values can contain credentials, ex. 'azure:clientSecret'
NON_SENSITIVE_CONFIG = {"environment", "location", "profile", "project", "region", "version", "zone"}
BOOLEAN_VALUE = re.compile(r"^(true|false)$", re.IGNORECASE)
SECRET_PLAINTEXT = re.compile(r'"plaintext"\s*:\s*"(?:[^"\\]|\\.)*"')

# operations, which don't result in a resource managed by the stack
SKIPPED_OPERATIONS = {
    "delete",
    "delete-replaced",
    "discard",
    "discard-replaced",
    "read",
    "read-discard",
    "read-replacement",
    "remove-pending-replace",
}


def _is_str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _to_resource(state: dict[str, Any], start_line: int, end_line: int) -> PulumiResource | None:
    urn = state.get("urn")
    resource_type = state.get("type")
    inputs = state.get("inputs") or {}
    dependencies = state.get("propertyDependencies") or {}
    if not isinstance(urn, str) or not urn.startswith(PULUMI_URN_PREFIX) or not isinstance(resource_type, str):
        return None
    if not isinstance(inputs, dict) or not isinstance(dependencies, dict):
        return None
    if not state.get("custom") or state.get("delete") or state.get("external"):
        # component resources only group other resources, "custom" is omitted in events, when false.
        # external resources are only read by the stack, ex. 'aws.s3.Bucket.get()'
        return None
    return PulumiResource(
        urn=urn,
        type=resource_type,
        inputs=inputs,
        property_dependencies={
            key: value for key, value in dependencies.items()
            if isinstance(key, str) and key not in LINE_FIELD_NAMES and _is_str_list(value)
        },
        start_line=start_line,
        end_line=end_line,
    )


def _lines(node: Any) -> tuple[int, int]:
    """Line range in the same format as the Terraform plan parser"""

    if hasattr(node, "start_mark") and hasattr(node, "end_mark"):
        return node.start_mark.line, node.end_mark.line
    return 0, 0


def _state_lines(state: dict[str, Any]) -> tuple[int, int]:
    """The resource inputs are the relevant part of a resource state"""

    return _lines(state.get("inputs") or state)


def _config_providers(config: Any, lines: tuple[int, int] | None = None) -> list[PulumiResource]:
    """Default providers are configured via the stack config, ex. 'aws:region'"""

    if not isinstance(config, dict):
        return []
    inputs: dict[str, dict[str, Any]] = {}
    value_lines: dict[str, list[int]] = {}
    for key, value in config.items():
        if isinstance(key, str) and ":" in key and key not in LINE_FIELD_NAMES:
            package, name = key.split(":", 1)
            inputs.setdefault(package, {})[name] = value
            if hasattr(value, "start_mark"):
                value_lines.setdefault(package, []).append(value.start_mark.line)
    providers = []
    for package, package_inputs in inputs.items():
        if lines:
            start_line, end_line = lines
        elif package in value_lines:
            # the config is sorted, the lines only cover the keys of the provider
            start_line, end_line = min(value_lines[package]), max(value_lines[package]) + 1
        else:
            start_line, end_line = 0, 0
        providers.append(
            PulumiResource(
                urn=f"{PULUMI_URN_PREFIX}:::{PROVIDER_TYPE_PREFIX}{package}::default",
                type=f"{PROVIDER_TYPE_PREFIX}{package}",
                inputs=package_inputs,
                start_line=start_line,
                end_line=end_line,
            )
        )
    return providers


def _parse_document(template: dict[str, Any]) -> list[PulumiResource] | None:
    resources: list[PulumiResource] = []
    if isinstance(template.get("steps"), list):
        # pulumi preview --json
        resources.extend(_config_providers(template.get("config")))
        for step in template["steps"]:
            if not isinstance(step, dict) or step.get("op") in SKIPPED_OPERATIONS:
                continue
            state = step.get("newState")
            if isinstance(state, dict):
                resource = _to_resource(state, *_state_lines(state))
                if resource:
                    resources.append(resource)
        return resources
    if isinstance(template.get("deployment"), dict):
        # pulumi stack export
        for state in template["deployment"].get("resources") or []:
            if isinstance(state, dict):
                resource = _to_resource(state, *_state_lines(state))
                if resource:
                    resources.append(resource)
        return resources
    return None


def _parse_events(content: str) -> list[PulumiResource] | None:
    """pulumi preview --json with PULUMI_ENABLE_STREAMING_JSON_PREVIEW, one engine event per line"""

    resources: list[PulumiResource] = []
    is_event_log = False
    for idx, line in enumerate(content.splitlines()):
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict) or "sequence" not in event:
            return None
        is_event_log = True
        if isinstance(event.get("preludeEvent"), dict):
            resources.extend(_config_providers(event["preludeEvent"].get("config"), (idx, idx + 1)))
            continue
        pre_event = event.get("resourcePreEvent")
        metadata = pre_event.get("metadata") if isinstance(pre_event, dict) else None
        if not isinstance(metadata, dict) or metadata.get("op") in SKIPPED_OPERATIONS:
            continue
        state = metadata.get("new")
        if isinstance(state, dict):
            resource = _to_resource(state, idx, idx + 1)
            if resource:
                resources.append(resource)
    return resources if is_event_log else None


def _is_event_log(content: str) -> bool:
    first_line = content.lstrip().split("\n", 1)[0]
    try:
        event = json.loads(first_line)
    except ValueError:
        return False
    return isinstance(event, dict) and "sequence" in event


def _deduplicate(resources: list[PulumiResource]) -> list[PulumiResource]:
    """Replacements and refreshes have multiple steps for the same resource, the last one is the planned state"""

    unique: dict[str, PulumiResource] = {}
    for resource in resources:
        unique.pop(resource.urn, None)
        unique[resource.urn] = resource
    return list(unique.values())


def _is_secret(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    sig = value.get(SIG_KEY)
    return sig == SECRET_SIG or (sig == OUTPUT_SIG and bool(value.get("secret")))


def _is_sensitive_config(key: str, value: Any) -> bool:
    if key.startswith("__"):
        # Pulumi internals, ex. '__defaults'
        return False
    if isinstance(value, (dict, list)):
        return True
    if not isinstance(value, str) or BOOLEAN_VALUE.match(value):
        # Pulumi writes the config as strings, booleans and numbers aren't credentials.
        # numbers also have no line numbers, which are needed to mask them
        return False
    return key.split(":", 1)[-1] not in NON_SENSITIVE_CONFIG


def _sensitive_config_nodes(config: Any) -> list[Any]:
    if not isinstance(config, dict):
        return []
    return [
        value for key, value in config.items()
        if isinstance(key, str) and key not in LINE_FIELD_NAMES and _is_sensitive_config(key, value)
    ]


def _is_provider_state(value: dict[str, Any]) -> bool:
    resource_type = value.get("type")
    return isinstance(resource_type, str) and resource_type.startswith(PROVIDER_TYPE_PREFIX) and "urn" in value


def _secret_nodes(data: Any) -> list[Any]:
    """Secret values and credentials in the provider config, which is set without '--secret'

    The provider config is part of the stack config ('config' of a preview or the prelude event of an event log)
    and of the inputs and outputs of the provider resources.
    """

    nodes = []
    if isinstance(data, dict):
        nodes.extend(_sensitive_config_nodes(data.get("config")))
        prelude = data.get("preludeEvent")
        if isinstance(prelude, dict):
            nodes.extend(_sensitive_config_nodes(prelude.get("config")))
    stack = [data]
    while stack:
        current = stack.pop()
        if _is_secret(current):
            nodes.append(current)
        elif isinstance(current, dict):
            if _is_provider_state(current):
                nodes.extend(_sensitive_config_nodes(current.get("inputs")))
                nodes.extend(_sensitive_config_nodes(current.get("outputs")))
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return nodes


def _mask_spans(file_lines: list[tuple[int, str]], nodes: list[Any]) -> list[tuple[int, str]]:
    """Replaces the text of the nodes, the line numbers stay the same"""

    lines = [line for _, line in file_lines]
    spans = sorted(
        (node.start_mark.line, node.start_mark.column, node.end_mark.line, node.end_mark.column) for node in nodes
    )
    # reversed, so the columns of earlier spans in the same line stay valid
    for start_line, start_col, end_line, end_col in reversed(_without_nested(spans)):
        if start_line == end_line:
            line = lines[start_line]
            lines[start_line] = f'{line[:start_col]}"{MASK}"{line[end_col:]}'
        else:
            first, last = lines[start_line], lines[end_line]
            lines[start_line] = f'{first[:start_col]}"{MASK}"\n'
            for idx in range(start_line + 1, end_line):
                lines[idx] = "\n"
            lines[end_line] = last[end_col:]
    return [(idx, line) for (idx, _), line in zip(file_lines, lines)]  # noqa: B905  # same length


def _without_nested(spans: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    result: list[tuple[int, int, int, int]] = []
    for span in spans:
        if result and (span[0], span[1]) < (result[-1][2], result[-1][3]):
            # inside of the previous span
            continue
        result.append(span)
    return result


def _mask_secrets(file_lines: list[tuple[int, str]], data: Any) -> list[tuple[int, str]]:
    nodes = _secret_nodes(data)
    if nodes:
        if not all(hasattr(node, "start_mark") and hasattr(node, "end_mark") for node in nodes):
            # no line numbers, ex. large files, which have no code blocks anyway, everything is masked to be safe
            return [(idx, f"{MASK}\n") for idx, _ in file_lines]
        # before any other replacement, the columns of the nodes refer to the original lines
        file_lines = _mask_spans(file_lines, nodes)
    # with '--show-secrets' secrets are written in plaintext, always as JSON encoded string
    return [(idx, SECRET_PLAINTEXT.sub(f'"plaintext": "{MASK}"', line)) for idx, line in file_lines]


def _mask_event_secrets(file_lines: list[tuple[int, str]], content: str) -> list[tuple[int, str]]:
    """Events have no line numbers per value, events with secrets are masked completely"""

    events = content.splitlines()
    masked = []
    for (idx, line), event in zip(file_lines, events):  # noqa: B905  # same length
        if event.strip() and _secret_nodes(json.loads(event)):
            line = f"{MASK}\n"
        masked.append((idx, line))
    return masked


def parse_pulumi_file(
    file_path: str, out_parsing_errors: dict[str, str]
) -> tuple[list[PulumiResource], list[tuple[int, str]]] | tuple[None, None]:
    try:
        content = read_file_with_any_encoding(file_path=file_path)
    except Exception as e:
        logging.debug(f"[pulumi] failed to read file {file_path}", exc_info=True)
        out_parsing_errors[file_path] = str(e)
        return None, None
    if PULUMI_URN_PREFIX not in content:
        return None, None
    content = content.lstrip("﻿")
    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    try:
        if _is_event_log(content):
            resources = _parse_events(content)
            masked_lines = _mask_event_secrets(file_lines, content)
            if resources:
                logging.warning(
                    f"[pulumi] {file_path} is a streamed event log, which has no resource dependencies. "
                    "Graph checks, which need connected resources, can fail. Use 'pulumi preview --json' "
                    "without PULUMI_ENABLE_STREAMING_JSON_PREVIEW for complete results."
                )
        else:
            # strict JSON first, the YAML features of the line number parser, ex. aliases, are not allowed
            data = json.loads(content)
            if not isinstance(data, dict):
                return None, None
            if len(content) <= MAX_IAC_FILE_SIZE:
                # same as for Terraform plans, large files are loaded without line numbers.
                # the TF plan content type allows null values
                try:
                    data = cfn_yaml.loads(content, file_path, ContentType.TFPLAN)
                except Exception:
                    # valid JSON, which isn't supported by the YAML parser, ex. escaped surrogate pairs
                    logging.debug(f"[pulumi] failed to get line numbers for file {file_path}", exc_info=True)
            resources = _parse_document(data)
            masked_lines = _mask_secrets(file_lines, data)
    except Exception as e:
        logging.debug(f"[pulumi] failed to parse file {file_path}", exc_info=True)
        out_parsing_errors[file_path] = str(e)
        return None, None

    if resources is None:
        logging.debug(f"[pulumi] file {file_path} is not a Pulumi preview or stack export")
        return None, None
    return _deduplicate(resources), masked_lines
