import pytest
from unittest.mock import Mock
import json
from checkov.common.output.in_toto_output import InTotoOutput
import tempfile
import os
import hashlib


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@pytest.fixture
def mock_report():
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, "main.tf")
    with open(temp_file_path, "w") as f:
        f.write("dummy content")

    report = Mock()
    report.failed_checks = [

        Mock(
            file_path=temp_file_path,
            check_id="CKV_AWS_18",
            check_name="Ensure the S3 bucket has access logging enabled",
            severity="MEDIUM",
        ),
    ]
    return report, temp_file_path


def test_generate_output(mock_report):
    report, temp_file_path = mock_report
    in_toto_output = InTotoOutput(repo_id="my_repo", reports=[report])
    result = in_toto_output.generate_output()
    expected_sha256 = calculate_sha256(temp_file_path)

    assert result["_type"] == "https://in-toto.io/Statement/v1"
    assert result["predicateType"] == "https://in-toto.io/attestation/vulns/v0.1"
    assert result["subject"][0]["digest"]["sha256"] == expected_sha256
    assert result["predicate"]["invocation"]["uri"] == ""
    assert result["predicate"]["invocation"]["event_id"] == "1071875574"
    assert result["predicate"]["invocation"]["builder.id"] == ""
    assert result["predicate"]["scanner"]["uri"] == ""
    assert result["predicate"]["scanner"]["version"] == "0.19.2"
    assert result["predicate"]["scanner"]["db"]["uri"] == "pkg:github/aquasecurity/trivy-db/commit/4c76bb580b2736d67751410fa4ab66d2b6b9b27d"
    assert result["predicate"]["scanner"]["db"]["version"] == "v1-2021080612"
    assert result["predicate"]["scanner"]["db"]["lastUpdate"] == "2021-08-06T17:45:50.52Z"
    assert result["predicate"]["scanner"]["result"][0]["id"] == "CKV_AWS_18"
    assert result["predicate"]["scanner"]["result"][0]["severity"][0]["score"] == "MEDIUM"


def test_write_output(mock_report, tmpdir):
    report, temp_file_path = mock_report
    in_toto_output = InTotoOutput(repo_id="my_repo", reports=[report])
    output_path = tmpdir.join("test_output.json")
    result = in_toto_output.generate_output()
    in_toto_output.write_output(str(output_path), result)
    expected_sha256 = calculate_sha256(temp_file_path)

    with open(output_path, "r") as f:
        data = json.load(f)

    assert data["_type"] == "https://in-toto.io/Statement/v1"
    assert data["predicateType"] == "https://in-toto.io/attestation/vulns/v0.1"
    assert data["subject"][0]["digest"]["sha256"] == expected_sha256
    assert data["predicate"]["invocation"]["uri"] == ""
    assert data["predicate"]["invocation"]["event_id"] == "1071875574"
    assert data["predicate"]["invocation"]["builder.id"] == ""
    assert data["predicate"]["scanner"]["uri"] == ""
    assert data["predicate"]["scanner"]["version"] == "0.19.2"
    assert data["predicate"]["scanner"]["db"]["uri"] == "pkg:github/aquasecurity/trivy-db/commit/4c76bb580b2736d67751410fa4ab66d2b6b9b27d"
    assert data["predicate"]["scanner"]["db"]["version"] == "v1-2021080612"
    assert data["predicate"]["scanner"]["db"]["lastUpdate"] == "2021-08-06T17:45:50.52Z"
    assert data["predicate"]["scanner"]["result"][0]["id"] == "CKV_AWS_18"
    assert data["predicate"]["scanner"]["result"][0]["severity"][0]["score"] == "MEDIUM"
