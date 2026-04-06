from __future__ import annotations

import asyncio
from pathlib import Path
from unittest import mock

import pytest

from checkov.common.sca.commons import validate_image_id, IMAGE_ID_PATTERN, IMAGE_NAME_PATTERN
from checkov.sca_image.runner import Runner


class TestImageIdPattern:
    """Tests for IMAGE_ID_PATTERN — matches Docker image SHA IDs (3-64 hex chars, optionally prefixed with sha256:)."""

    @pytest.mark.parametrize("image_id", [
        "sha256:" + "a" * 64,
        "sha256:" + "0123456789abcdef" * 4,
        "a" * 64,
        "0" * 64,
        "sha256:abc",                # 3 hex chars with prefix
        "abc",                       # 3 hex chars raw
        "a" * 12,                    # shortened SHA (12 chars)
        "sha256:" + "a" * 12,       # shortened SHA with prefix
        "a" * 63,                    # 63 hex chars
    ])
    def test_valid_image_ids(self, image_id: str) -> None:
        assert IMAGE_ID_PATTERN.fullmatch(image_id), f"Expected match for: {image_id}"

    @pytest.mark.parametrize("image_id", [
        "sha256:" + "g" * 64,       # non-hex chars
        "a" * 65,                    # too long
        "",                          # empty
        "sha256:",                   # prefix only, no hex
        "ab",                        # too short (2 chars)
        "sha256:ab",                 # too short with prefix
    ])
    def test_invalid_image_ids(self, image_id: str) -> None:
        assert not IMAGE_ID_PATTERN.fullmatch(image_id), f"Expected no match for: {image_id}"


class TestImageNamePattern:
    """Tests for IMAGE_NAME_PATTERN — matches Docker image name references."""

    @pytest.mark.parametrize("image_name", [
        "nginx",
        "nginx:latest",
        "nginx:1.21.0",
        "myregistry.io/nginx",
        "myregistry.io:5000/nginx",
        "myregistry.io/myns/nginx:v1.0",
        "docker.io/library/nginx:latest",
        "gcr.io/my-project/my-image:v2.1",
        "nginx@sha256:" + "a" * 64,
        "myregistry.io/nginx:v1@sha256:" + "b" * 64,
        "ubuntu",
        "python:3.11-slim",
        "node:14.16",
        "public.ecr.aws/aws-containers/hello-app-runner:latest",
    ])
    def test_valid_image_names(self, image_name: str) -> None:
        assert IMAGE_NAME_PATTERN.fullmatch(image_name), f"Expected match for: {image_name}"

    @pytest.mark.parametrize("image_name", [
        "",
        "-nginx",
        ".nginx",
        "nginx; rm -rf /",
        "nginx$(whoami)",
        "nginx | cat /etc/passwd",
        "nginx`id`",
        "image name",
        "nginx&&echo pwned",
        "nginx>output",
        "nginx\nmalicious",
    ])
    def test_invalid_image_names(self, image_name: str) -> None:
        assert not IMAGE_NAME_PATTERN.fullmatch(image_name), f"Expected no match for: {image_name}"


class TestValidateImageId:
    """Tests for the combined validate_image_id function."""

    @pytest.mark.parametrize("image_id", [
        "sha256:" + "a" * 64,
        "nginx:latest",
        "gcr.io/my-project/my-image:v2.1",
        "a",
        "ubuntu",
    ])
    def test_valid_inputs(self, image_id: str) -> None:
        assert validate_image_id(image_id) is True

    @pytest.mark.parametrize("image_id", [
        "",
        "nginx; rm -rf /",
        "nginx$(whoami)",
        "nginx | cat /etc/passwd",
        "nginx`id`",
        "image name with spaces",
        "nginx&&echo pwned",
        "nginx>output",
        "-nginx",
    ])
    def test_injection_payloads_rejected(self, image_id: str) -> None:
        assert validate_image_id(image_id) is False


class TestExecuteScanRejectsInvalidImageId:
    """Tests that Runner.execute_scan rejects invalid image_id values."""

    def test_execute_scan_rejects_shell_injection(self) -> None:
        runner = Runner()
        malicious_id = "nginx; rm -rf /"
        result = asyncio.run(runner.execute_scan(malicious_id, Path("output.json")))
        assert result == {}

    def test_execute_scan_rejects_subshell_injection(self) -> None:
        runner = Runner()
        malicious_id = "nginx$(whoami)"
        result = asyncio.run(runner.execute_scan(malicious_id, Path("output.json")))
        assert result == {}

    def test_execute_scan_rejects_pipe_injection(self) -> None:
        runner = Runner()
        malicious_id = "nginx | cat /etc/passwd"
        result = asyncio.run(runner.execute_scan(malicious_id, Path("output.json")))
        assert result == {}

    def test_execute_scan_rejects_backtick_injection(self) -> None:
        runner = Runner()
        malicious_id = "nginx`id`"
        result = asyncio.run(runner.execute_scan(malicious_id, Path("output.json")))
        assert result == {}

    def test_execute_scan_rejects_ampersand_injection(self) -> None:
        runner = Runner()
        malicious_id = "nginx&&echo pwned"
        result = asyncio.run(runner.execute_scan(malicious_id, Path("output.json")))
        assert result == {}
