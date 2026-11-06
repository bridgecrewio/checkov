from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.pulumi.parser import parse_pulumi_file
from checkov.pulumi.runner import Runner
from checkov.pulumi.translator import PulumiResource, translate_resources
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"
STACK = "urn:pulumi:dev::project::"
UNKNOWN = "04da6b54-80e4-46f7-96ec-b56ff0331ba9"
SECRET_SIG = {"4dabf18193072939515e22adb298388d": "1b47061264138c4ac30d75fd1eb44270"}


def preview(*states: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "config": config or {},
        "steps": [{"op": "create", "urn": state["urn"], "newState": state} for state in states],
    }


def state(resource_type: str, name: str, inputs: Any, **kwargs: Any) -> dict[str, Any]:
    return {"urn": f"{STACK}{resource_type}::{name}", "custom": True, "type": resource_type, "inputs": inputs, **kwargs}


def run(path: Path, checks: list[str] | None = None) -> Report:
    report = Runner().run(root_folder=str(path) if path.is_dir() else None, files=None if path.is_dir() else [str(path)],
                          runner_filter=RunnerFilter(framework=["pulumi"], checks=checks or []))
    assert isinstance(report, Report)
    return report


def test_malformed_files_dont_stop_the_scan(tmp_path: Path) -> None:
    """One broken file must not hide the results of the other files"""

    bad_inputs = preview(state("aws:s3/bucket:Bucket", "bad", "not-a-dict"))
    bad_dependencies = preview(state("aws:s3/bucket:Bucket", "bad", {}, propertyDependencies={"bucket": [{"x": 1}]}))
    (tmp_path / "bad_inputs.json").write_text(json.dumps(bad_inputs))
    (tmp_path / "bad_dependencies.json").write_text(json.dumps(bad_dependencies))
    (tmp_path / "preview.json").write_text((EXAMPLES_DIR / "aws" / "preview.json").read_text())

    report = run(tmp_path, checks=["CKV_AWS_24"])

    assert [r.file_path for r in report.failed_checks] == ["/preview.json"]


def test_yaml_aliases_are_rejected(tmp_path: Path) -> None:
    """The line number parser understands YAML, only strict JSON is allowed to prevent alias expansion attacks"""

    file_path = tmp_path / "preview.json"
    levels = ['a0: &a0 ["x","x","x","x","x","x","x","x","x"]']
    levels += [f"a{i}: &a{i} [{','.join([f'*a{i - 1}'] * 9)}]" for i in range(1, 9)]
    file_path.write_text(
        "{" + ", ".join(levels) + ', "steps": [{"op": "create", "newState": {"urn": "urn:pulumi:dev::p::aws:s3/bucket:Bucket::b",'
        ' "custom": true, "type": "aws:s3/bucket:Bucket", "inputs": {"tags": *a8}}}]}'
    )
    errors: dict[str, str] = {}

    start = time.monotonic()
    assert parse_pulumi_file(str(file_path), errors) == (None, None)

    assert str(file_path) in errors
    assert time.monotonic() - start < 5


def test_many_duplicate_names_are_fast() -> None:
    resources = [
        PulumiResource(urn=f"urn:pulumi:stack{i}::project::aws:s3/bucket:Bucket::bucket", type="aws:s3/bucket:Bucket", inputs={})
        for i in range(20_000)
    ]

    start = time.monotonic()
    definition = translate_resources(resources)

    assert len(definition["resource"]) == 20_000
    assert time.monotonic() - start < 10


def test_deep_nesting(tmp_path: Path) -> None:
    nested: dict[str, Any] = {}
    current = nested
    for _ in range(300):
        current["a"] = {}
        current = current["a"]
    file_path = tmp_path / "preview.json"
    file_path.write_text(json.dumps(preview(state("aws:s3/bucket:Bucket", "bucket", {"tags": nested}))))

    report = run(file_path, checks=["CKV_AWS_18"])

    assert not report.parsing_errors
    assert len(report.failed_checks) == 1


def test_secrets_are_not_part_of_the_results(tmp_path: Path) -> None:
    password = "plaintext-db-password"
    token = 'p<a>ss&"word'
    file_path = tmp_path / "preview.json"
    # with '--show-secrets' the plaintext is a JSON encoded value, Pulumi uses the Go encoder, which escapes <, > and &
    file_path.write_text(
        json.dumps(
            preview(
                state("aws:rds/instance:Instance", "db", {"password": {**SECRET_SIG, "plaintext": json.dumps(password)}}),
                state(
                    "aws:lambda/function:Function",
                    "fn",
                    {"environment": {**SECRET_SIG, "plaintext": json.dumps({"variables": {"TOKEN": token}})}},
                ),
            ),
            indent=4,
        ).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )

    report = run(file_path)

    assert report.failed_checks
    output = json.dumps(report.get_dict())
    for secret in (password, "p\\u003ca", "p<a>"):
        assert secret not in output
    assert "**********" in output


def test_provider_code_block_only_contains_provider_config(tmp_path: Path) -> None:
    file_path = tmp_path / "preview.json"
    config = {"aws:region": "us-east-1", "aws:secretKey": "notasecret", "myapp:apiToken": "tok_plain_123456"}
    file_path.write_text(json.dumps(preview(state("aws:s3/bucket:Bucket", "b", {}), config=config), indent=4))

    report = run(file_path, checks=["CKV_AWS_41"])

    record = next(r for r in report.passed_checks if r.resource == "aws.default")
    code = "".join(line for _, line in record.code_block)
    assert "aws:region" in code
    assert "myapp:apiToken" not in code


def test_external_and_refreshed_resources(tmp_path: Path) -> None:
    export = {
        "version": 3,
        "deployment": {
            "resources": [
                state("aws:s3/bucket:Bucket", "external", {}, external=True),
                state("aws:s3/bucket:Bucket", "managed", {}),
            ]
        },
    }
    refresh = {
        "steps": [
            {"op": "refresh", "newState": state("aws:s3/bucket:Bucket", "b", {"acl": "public-read"})},
            {"op": "update", "newState": state("aws:s3/bucket:Bucket", "b", {"acl": "private"})},
        ]
    }
    (tmp_path / "export.json").write_text(json.dumps(export))
    (tmp_path / "refresh.json").write_text(json.dumps(refresh))
    errors: dict[str, str] = {}

    export_resources, _ = parse_pulumi_file(str(tmp_path / "export.json"), errors)
    refresh_resources, _ = parse_pulumi_file(str(tmp_path / "refresh.json"), errors)

    assert export_resources and [r.name for r in export_resources] == ["managed"]
    # the planned state wins over the refreshed state
    assert refresh_resources and [r.inputs["acl"] for r in refresh_resources] == ["private"]


@pytest.mark.parametrize("prefix,newline", [("﻿", "\n"), ("", "\r\n")])
def test_event_log_encodings(tmp_path: Path, prefix: str, newline: str) -> None:
    lines = (EXAMPLES_DIR / "aws" / "preview_events.jsonl").read_text().splitlines()
    lines.insert(1, json.dumps({"sequence": 99, "preludeEvent": None, "resourcePreEvent": None}))
    file_path = tmp_path / "preview_events.jsonl"
    file_path.write_bytes((prefix + newline.join(lines) + newline).encode("utf-8"))
    errors: dict[str, str] = {}

    resources, _ = parse_pulumi_file(str(file_path), errors)

    assert not errors
    assert resources and any(r.name == "secureBucket" for r in resources)


def test_large_files_have_no_line_numbers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("checkov.pulumi.parser.MAX_IAC_FILE_SIZE", 10)
    errors: dict[str, str] = {}

    resources, _ = parse_pulumi_file(str(EXAMPLES_DIR / "aws" / "preview.json"), errors)

    assert not errors
    assert resources and all(r.start_line == r.end_line == 0 for r in resources)


@pytest.mark.skipif(os.name == "nt", reason="symlinks need special permissions on Windows")
def test_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "state.json").write_text((EXAMPLES_DIR / "aws" / "preview.json").read_text())
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "preview.json").write_text((EXAMPLES_DIR / "aws" / "preview.json").read_text())
    (repo / "evil.json").symlink_to(outside / "state.json")
    linked_repo = tmp_path / "linked_repo"
    linked_repo.symlink_to(repo, target_is_directory=True)

    report = run(linked_repo, checks=["CKV_AWS_24"])

    # files outside of the scanned directory are ignored and the paths are relative to the scanned directory
    assert [r.file_path for r in report.failed_checks] == ["/preview.json"]


def test_excluded_paths(tmp_path: Path) -> None:
    # the name of the tmp_path contains the test name
    for directory in ("included", "skipme"):
        (tmp_path / directory).mkdir()
        (tmp_path / directory / "preview.json").write_text((EXAMPLES_DIR / "aws" / "preview.json").read_text())

    report = Runner().run(
        root_folder=str(tmp_path),
        runner_filter=RunnerFilter(framework=["pulumi"], checks=["CKV_AWS_24"], excluded_paths=["skipme"]),
    )

    assert isinstance(report, Report)
    assert [r.file_path for r in report.failed_checks] == ["/included/preview.json"]


def test_reports_are_not_enriched_with_terraform_configuration() -> None:
    report = Report(CheckType.PULUMI)
    report.add_record(
        Record(
            check_id="CKV_AWS_24",
            bc_check_id=None,
            check_name="test",
            check_result={"result": "FAILED"},
            code_block=[],
            file_path="/preview.json",
            file_line_range=[1, 2],
            resource="aws_security_group.openSg",
            evaluations=None,
            check_class="",
            file_abs_path=str(EXAMPLES_DIR / "aws" / "preview.json"),
            resource_address="aws_security_group.openSg",
        )
    )
    registry = RunnerRegistry("", RunnerFilter(framework=["pulumi"]), Runner())

    # the Terraform configuration contains a resource with the same address
    registry._handle_report(report, [str(EXAMPLES_DIR / "aws")])

    assert registry.scan_reports[0].failed_checks[0].file_path == "/preview.json"


def test_secret_masking_is_fast(tmp_path: Path) -> None:
    tags = {f"tag{i}": {**SECRET_SIG, "plaintext": json.dumps(f"secret{i:08}")} for i in range(20_000)}
    file_path = tmp_path / "preview.json"
    file_path.write_text(json.dumps(preview(state("aws:s3/bucket:Bucket", "bucket", {"tags": tags}))))
    errors: dict[str, str] = {}

    start = time.monotonic()
    resources, file_lines = parse_pulumi_file(str(file_path), errors)

    assert resources and file_lines
    assert "secret00000042" not in file_lines[0][1]
    assert time.monotonic() - start < 10


def test_partially_unknown_policies_are_unknown() -> None:
    policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": UNKNOWN}]}

    definition = translate_resources(
        [PulumiResource(urn=f"{STACK}aws:iam/policy:Policy::p", type="aws:iam/policy:Policy", inputs={"policy": policy})]
    )

    assert "policy" not in definition["resource"][0]["aws_iam_policy"]["p"]


def test_valid_json_without_line_numbers(tmp_path: Path) -> None:
    """Escaped surrogate pairs are valid JSON, but not supported by the YAML parser"""

    file_path = tmp_path / "preview.json"
    file_path.write_text(json.dumps(preview(state("aws:s3/bucket:Bucket", "bucket", {"tags": {"emoji": "\U0001F600"}}))))
    errors: dict[str, str] = {}

    resources, _ = parse_pulumi_file(str(file_path), errors)

    assert not errors
    assert resources and resources[0].inputs["tags"]["emoji"] == "\U0001F600"



@pytest.mark.parametrize("indent", [None, 4])
def test_secret_outputs_and_credentials_are_masked(tmp_path: Path, indent: int | None) -> None:
    output_sig = {"4dabf18193072939515e22adb298388d": "d0e6a833031e9bbcd3f4e8bde6ca49a4"}
    file_path = tmp_path / "preview.json"
    file_path.write_text(
        json.dumps(
            preview(
                state(
                    "aws:lambda/function:Function",
                    "fn",
                    {"environment": {**output_sig, "secret": True, "value": {"variables": {"TOKEN": "output-secret-value"}}}},
                ),
                config={
                    "azure:clientSecret": "plain-client-secret",
                    "azure:clientCertificate": "plain-certificate",
                    "kubernetes:kubeconfig": "plain-kubeconfig",
                    "aws:secretKey": "73914625",
                    "aws:skipMetadataApiCheck": "true",
                    "aws:region": "us-east-1",
                },
            ),
            indent=indent,
        )
    )
    errors: dict[str, str] = {}

    resources, file_lines = parse_pulumi_file(str(file_path), errors)

    assert resources
    text = "".join(line for _, line in file_lines or [])
    assert "output-secret-value" not in text
    for value in ("plain-client-secret", "plain-certificate", "plain-kubeconfig", "73914625"):
        assert value not in text
    assert '"aws:skipMetadataApiCheck": "true"' in text
    # the line numbers and other values stay the same
    assert len(file_lines or []) == len(file_path.read_text().splitlines())
    assert "us-east-1" in text
    json_lines = [line for _, line in file_lines or [] if line.strip()]
    if indent is None:
        json.loads(json_lines[0])


def test_event_log_secrets_are_masked(tmp_path: Path) -> None:
    secret = {**SECRET_SIG, "plaintext": json.dumps("event-secret-value")}
    events = [
        {"sequence": 0, "preludeEvent": {"config": {"aws:region": "us-east-1"}}},
        {"sequence": 1, "resourcePreEvent": {"metadata": {"op": "create", "new": state(
            "aws:rds/instance:Instance", "db", {"password": secret, "engine": "mysql"}
        )}}},
    ]
    file_path = tmp_path / "preview_events.jsonl"
    file_path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    errors: dict[str, str] = {}

    resources, file_lines = parse_pulumi_file(str(file_path), errors)

    assert resources and resources[-1].inputs["engine"] == "mysql"
    assert "event-secret-value" not in "".join(line for _, line in file_lines or [])


def test_secrets_without_line_numbers_are_masked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("checkov.pulumi.parser.MAX_IAC_FILE_SIZE", 10)
    # pretty printed over multiple lines, only the regex for plaintext secrets doesn't mask it
    secret = {"4dabf18193072939515e22adb298388d": "d0e6a833031e9bbcd3f4e8bde6ca49a4", "secret": True,
              "value": {"multi": "line-secret-value"}}
    file_path = tmp_path / "preview.json"
    file_path.write_text(
        json.dumps(preview(state("aws:s3/bucket:Bucket", "b", {"tags": secret}), config={"aws:skipMetadataApiCheck": True}), indent=4)
    )
    errors: dict[str, str] = {}

    resources, file_lines = parse_pulumi_file(str(file_path), errors)

    assert resources
    assert "line-secret-value" not in "".join(line for _, line in file_lines or [])


def _masked_text(file_path: Path) -> str:
    errors: dict[str, str] = {}
    resources, file_lines = parse_pulumi_file(str(file_path), errors)
    assert resources and not errors
    return "".join(line for _, line in file_lines or [])


def test_resource_inputs_named_config_are_not_masked(tmp_path: Path) -> None:
    """Only the stack config is provider config, a resource input called 'config' must not mask the file"""

    file_path = tmp_path / "preview.json"
    environment = state(
        "gcp:composer/environment:Environment", "env",
        {"name": "visible-name", "config": {"nodeCount": 3, "softwareConfig": {"imageVersion": "visible-version"}}},
    )
    file_path.write_text(json.dumps(preview(environment, config={"gcp:project": "p"}), indent=4))

    text = _masked_text(file_path)

    assert "visible-name" in text
    assert "visible-version" in text


@pytest.mark.parametrize("indent", [None, 4])
def test_provider_resource_credentials_are_masked(tmp_path: Path, indent: int | None) -> None:
    """Providers keep their config in their inputs and outputs, ex. in a stack export or for explicit providers"""

    provider_config = {"region": "us-east-1", "accessKey": "plain-access-key", "secretKey": "plain-secret-key",
                       "skipCredentialsValidation": "true", "version": "7.53.0"}
    provider = state("pulumi:providers:aws", "default_7_53_0", provider_config, outputs=provider_config)
    file_path = tmp_path / "stack_export.json"
    file_path.write_text(json.dumps({"deployment": {"resources": [provider]}}, indent=indent))

    text = _masked_text(file_path)

    assert "plain-access-key" not in text
    assert "plain-secret-key" not in text
    assert "us-east-1" in text
    assert "7.53.0" in text


def test_provider_resource_credentials_are_masked_in_events(tmp_path: Path) -> None:
    provider = state("pulumi:providers:aws", "prod", {"region": "us-east-1", "secretKey": "plain-secret-key"})
    bucket = state("aws:s3/bucket:Bucket", "b", {"bucket": "visible-bucket"})
    events = [
        {"sequence": 0, "resourcePreEvent": {"metadata": {"op": "create", "new": provider}}},
        {"sequence": 1, "resourcePreEvent": {"metadata": {"op": "create", "new": bucket}}},
    ]
    file_path = tmp_path / "preview_events.jsonl"
    file_path.write_text("\n".join(json.dumps(e) for e in events) + "\n")

    text = _masked_text(file_path)

    assert "plain-secret-key" not in text
    assert "visible-bucket" in text


def test_plaintext_secrets_on_one_line_keep_the_other_values(tmp_path: Path) -> None:
    """Masking the plaintext of a secret must not shift the columns of the other masked values in the same line"""

    def secret(value: str) -> dict[str, str]:
        return {**SECRET_SIG, "plaintext": json.dumps(value)}

    bucket = state("aws:s3/bucket:Bucket", "b", {
        "acl": secret("a-plaintext-value-which-is-longer-than-the-mask"),
        "tags": {"key": secret("v")},
        "bucket": "after-the-secrets",
    })
    file_path = tmp_path / "preview.json"
    file_path.write_text(json.dumps(preview(bucket)))

    text = _masked_text(file_path)

    assert "a-plaintext-value" not in text
    assert '"bucket": "after-the-secrets"' in text
    json.loads(text)
