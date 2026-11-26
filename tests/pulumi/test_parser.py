from __future__ import annotations

from pathlib import Path

import pytest

from checkov.pulumi.parser import parse_pulumi_file

EXAMPLES_DIR = Path(__file__).parent / "examples"
RESOURCES_DIR = Path(__file__).parent / "resources"


@pytest.mark.parametrize("file_name", ["preview.json", "preview_events.jsonl", "stack_export.json"])
def test_parse_formats(file_name: str) -> None:
    errors: dict[str, str] = {}

    resources, file_lines = parse_pulumi_file(str(EXAMPLES_DIR / "aws" / file_name), errors)

    assert not errors
    assert resources and file_lines
    types = {r.type for r in resources}
    assert "aws:s3/bucket:Bucket" in types
    assert "aws:lambda/function:Function" in types
    # the stack resource is not a custom resource
    assert "pulumi:pulumi:Stack" not in types
    assert "pulumi:providers:aws" in types
    assert len({r.urn for r in resources}) == len(resources)


def test_parse_preview_details() -> None:
    errors: dict[str, str] = {}

    resources, file_lines = parse_pulumi_file(str(EXAMPLES_DIR / "aws" / "preview.json"), errors)

    assert resources and file_lines
    pab = next(r for r in resources if r.name == "securePab")
    assert pab.type == "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock"
    assert pab.inputs["blockPublicAcls"] is True
    assert pab.property_dependencies["bucket"] == ["urn:pulumi:dev::checkov-aws::aws:s3/bucket:Bucket::secureBucket"]

    # the line range covers the resource inputs
    first_line = file_lines[pab.start_line][1]
    last_line = file_lines[pab.end_line][1]
    assert first_line.rstrip().endswith('"inputs": {')
    assert last_line.strip().startswith("}")

    provider = next(r for r in resources if r.type == "pulumi:providers:aws")
    assert provider.inputs["region"] == "us-east-1"


def test_parse_event_line_ranges() -> None:
    errors: dict[str, str] = {}

    resources, file_lines = parse_pulumi_file(str(EXAMPLES_DIR / "aws" / "preview_events.jsonl"), errors)

    assert resources and file_lines
    bucket = next(r for r in resources if r.name == "secureBucket")
    assert bucket.end_line == bucket.start_line + 1
    assert "secureBucket" in file_lines[bucket.start_line][1]


def test_parse_operations() -> None:
    errors: dict[str, str] = {}

    resources, _ = parse_pulumi_file(str(RESOURCES_DIR / "operations.json"), errors)

    assert not errors
    assert resources is not None
    buckets = {r.name: r for r in resources if r.type == "aws:s3/bucket:Bucket"}
    # deleted and read only resources are not part of the stack, component resources are skipped
    assert set(buckets) == {"unchanged", "replaced"}
    assert buckets["replaced"].inputs["bucket"] == "replaced-new"
    assert buckets["unchanged"].inputs["acl"] is None


@pytest.mark.parametrize("file_name", ["not_pulumi.json", "mentions_urn.json", "array_with_urn.json"])
def test_other_files_are_ignored(file_name: str) -> None:
    errors: dict[str, str] = {}

    assert parse_pulumi_file(str(RESOURCES_DIR / file_name), errors) == (None, None)
    assert not errors


def test_malformed_file() -> None:
    errors: dict[str, str] = {}
    file_path = str(RESOURCES_DIR / "malformed_events.jsonl")

    assert parse_pulumi_file(file_path, errors) == (None, None)
    assert file_path in errors
