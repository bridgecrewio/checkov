import pytest
from unittest.mock import Mock
import json
from checkov.common.output.in_toto_output import InTotoOutput


@pytest.fixture
def mock_report():
    report = Mock()
    report.failed_checks = [
        Mock(
            file_path="/path/to/main.tf",
            check_id="CKV_AWS_6",
            check_name="Ensure that S3 bucket has a Public Access block",
            severity="HIGH",
        ),
        Mock(
            file_path="/path/to/main.tf",
            check_id="CKV_AWS_18",
            check_name="Ensure the S3 bucket has access logging enabled",
            severity="MEDIUM",
        ),
    ]
    return report


def test_generate_output(mock_report):
    in_toto_output = InTotoOutput(repo_id="my_repo", reports=[mock_report])
    result = in_toto_output.generate_output()

    assert result["_type"] == "https://in-toto.io/Statement/v1"
    assert result["predicateType"] == "https://in-toto.io/attestation/vulns/v0.1"
    assert result["subject"][0]["digest"][
               "sha256"] == "fe4fe40ac7250263c5dbe1cf3138912f3f416140aa248637a60d65fe22c47da4"
    assert result["predicate"]["invocation"]["uri"] == "https://github.com/developer-guy/alpine/actions/runs/1071875574"
    assert result["predicate"]["invocation"]["event_id"] == "1071875574"
    assert result["predicate"]["invocation"]["builder.id"] == "GitHub Actions"
    assert result["predicate"]["scanner"]["uri"] == "pkg:github/aquasecurity/trivy@244fd47e07d1004f0aed9"
    assert result["predicate"]["scanner"]["version"] == "0.19.2"
    assert result["predicate"]["scanner"]["db"][
               "uri"] == "pkg:github/aquasecurity/trivy-db/commit/4c76bb580b2736d67751410fa4ab66d2b6b9b27d"
    assert result["predicate"]["scanner"]["db"]["version"] == "v1-2021080612"
    assert result["predicate"]["scanner"]["db"]["lastUpdate"] == "2021-08-06T17:45:50.52Z"
    assert result["predicate"]["scanner"]["result"][0]["id"] == "CKV_AWS_6"
    assert result["predicate"]["scanner"]["result"][0]["severity"][0]["score"] == "HIGH"
    assert result["predicate"]["scanner"]["result"][1]["id"] == "CKV_AWS_18"
    assert result["predicate"]["scanner"]["result"][1]["severity"][0]["score"] == "MEDIUM"


def test_write_output(mock_report, tmpdir):
    in_toto_output = InTotoOutput(repo_id="my_repo", reports=[mock_report])
    output_path = tmpdir.join("test_output.json")
    result = in_toto_output.generate_output()
    in_toto_output.write_output(str(output_path), result)

    with open(output_path, "r") as f:
        data = json.load(f)

    assert data["_type"] == "https://in-toto.io/Statement/v1"
    assert data["predicateType"] == "https://in-toto.io/attestation/vulns/v0.1"
    assert data["subject"][0]["digest"]["sha256"] == "fe4fe40ac7250263c5dbe1cf3138912f3f416140aa248637a60d65fe22c47da4"
    assert data["predicate"]["invocation"]["uri"] == "https://github.com/developer-guy/alpine/actions/runs/1071875574"
    assert data["predicate"]["invocation"]["event_id"] == "1071875574"
    assert data["predicate"]["invocation"]["builder.id"] == "GitHub Actions"
    assert data["predicate"]["scanner"]["uri"] == "pkg:github/aquasecurity/trivy@244fd47e07d1004f0aed9"
    assert data["predicate"]["scanner"]["version"] == "0.19.2"
    assert data["predicate"]["scanner"]["db"][
               "uri"] == "pkg:github/aquasecurity/trivy-db/commit/4c76bb580b2736d67751410fa4ab66d2b6b9b27d"
    assert data["predicate"]["scanner"]["db"]["version"] == "v1-2021080612"
    assert data["predicate"]["scanner"]["db"]["lastUpdate"] == "2021-08-06T17:45:50.52Z"
    assert data["predicate"]["scanner"]["result"][0]["id"] == "CKV_AWS_6"
    assert data["predicate"]["scanner"]["result"][0]["severity"][0]["score"] == "HIGH"
    assert data["predicate"]["scanner"]["result"][1]["id"] == "CKV_AWS_18"
    assert data["predicate"]["scanner"]["result"][1]["severity"][0]["score"] == "MEDIUM"
