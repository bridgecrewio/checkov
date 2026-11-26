from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.output.report import Report
from checkov.main import Checkov
from checkov.pulumi.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.plan_runner import Runner as TerraformPlanRunner
from checkov.terraform.runner import Runner as TerraformRunner

EXAMPLES_DIR = Path(__file__).parent / "examples"
GRAPH_CONNECTORS = [NetworkxConnector, RustworkxConnector]

# checks, which have a different result for the Terraform plan, because the plan explicitly contains
# empty values of unset attributes. Pulumi omits them, which is the same as in a Terraform configuration.
TF_PLAN_DIFFERENCES = {
    ("CKV_AWS_173", "aws_lambda_function.fn"),  # kms_key_arn: null
    ("CKV_GCP_39", "google_compute_instance.vm"),  # shielded_instance_config: []
    ("CKV_GCP_63", "google_storage_bucket.insecureBucket"),  # logging: []
}

Results = "dict[tuple[str, str], str]"


def get_results(report: Report | list[Report]) -> dict[tuple[str, str], str]:
    report = report[0] if isinstance(report, list) else report
    assert not report.parsing_errors
    results = {(r.check_id, r.resource): "FAILED" for r in report.failed_checks}
    results.update({(r.check_id, r.resource): "PASSED" for r in report.passed_checks})
    return results


def run_pulumi(file_path: Path, graph_connector: type = NetworkxConnector) -> dict[tuple[str, str], str]:
    report = Runner(db_connector=graph_connector()).run(
        root_folder=None, files=[str(file_path)], runner_filter=RunnerFilter(framework=["pulumi"])
    )
    return get_results(report)


@pytest.mark.parametrize("graph_connector", GRAPH_CONNECTORS)
@pytest.mark.parametrize(
    "provider,file_name",
    [
        ("aws", "preview.json"),
        ("aws", "stack_export.json"),
        ("gcp", "preview.json"),
        ("azure", "preview.json"),
    ],
)
def test_parity_with_terraform(provider: str, file_name: str, graph_connector: type) -> None:
    """The Pulumi preview of a program has the same results as the Terraform plan of the same infrastructure"""

    example_dir = EXAMPLES_DIR / provider

    pulumi_results = run_pulumi(example_dir / file_name, graph_connector)
    plan_results = get_results(
        TerraformPlanRunner(db_connector=graph_connector()).run(
            root_folder=None, files=[str(example_dir / "tfplan.json")], runner_filter=RunnerFilter(framework=["all"])
        )
    )

    assert len(pulumi_results) > 30
    assert "FAILED" in pulumi_results.values() and "PASSED" in pulumi_results.values()
    differences = {key for key in pulumi_results.keys() | plan_results.keys() if pulumi_results.get(key) != plan_results.get(key)}
    assert differences <= TF_PLAN_DIFFERENCES

    # the differences match the result of the Terraform configuration
    if differences:
        config_results = get_results(
            TerraformRunner(db_connector=graph_connector()).run(
                root_folder=str(example_dir),
                runner_filter=RunnerFilter(framework=["terraform"], checks=sorted({check for check, _ in differences})),
            )
        )
        for key in differences:
            assert pulumi_results.get(key) == config_results.get(key), key


@pytest.mark.parametrize("extension", [".jsonl", ".json"])
def test_event_log(tmp_path: Path, extension: str) -> None:
    """Event logs don't contain dependencies, therefore only graph checks with connections can differ"""

    file_path = tmp_path / f"preview_events{extension}"
    shutil.copy(EXAMPLES_DIR / "aws" / "preview_events.jsonl", file_path)

    preview_results = run_pulumi(EXAMPLES_DIR / "aws" / "preview.json")
    event_results = run_pulumi(file_path)

    graph_registry = get_graph_checks_registry(CheckType.TERRAFORM)
    graph_registry.load_checks()
    graph_check_ids = {check.id for check in graph_registry.checks}
    assert preview_results.keys() == event_results.keys()
    for key, result in preview_results.items():
        if key[0] not in graph_check_ids:
            assert event_results[key] == result, key


@pytest.mark.parametrize("graph_connector", GRAPH_CONNECTORS)
def test_runner(graph_connector: type) -> None:
    file_path = EXAMPLES_DIR / "aws" / "preview.json"

    report = Runner(db_connector=graph_connector()).run(
        root_folder=None,
        files=[str(file_path)],
        runner_filter=RunnerFilter(framework=["pulumi"], checks=["CKV_AWS_24", "CKV_AWS_41", "CKV2_AWS_6"]),
    )

    assert isinstance(report, Report)
    assert report.check_type == CheckType.PULUMI
    summary = report.get_summary()
    assert summary["parsing_errors"] == 0
    assert summary["resource_count"] == 16

    failed = {(r.check_id, r.resource) for r in report.failed_checks}
    passed = {(r.check_id, r.resource) for r in report.passed_checks}
    assert failed == {
        ("CKV_AWS_24", "aws_security_group.openSg"),
        ("CKV2_AWS_6", "aws_s3_bucket.insecureBucket"),
    }
    assert passed == {
        ("CKV2_AWS_6", "aws_s3_bucket.secureBucket"),
        ("CKV_AWS_41", "aws.default"),
    }

    record = next(r for r in report.failed_checks if r.check_id == "CKV_AWS_24")
    assert record.file_path == f"/{file_path.name}"
    code = "".join(line for _, line in record.code_block)
    assert code.lstrip().startswith('"inputs": {')
    assert '"cidrBlocks"' in code


def test_runner_directory() -> None:
    report = Runner().run(
        root_folder=str(EXAMPLES_DIR / "aws"), runner_filter=RunnerFilter(framework=["pulumi"], checks=["CKV_AWS_24"])
    )

    assert isinstance(report, Report)
    # Terraform plan and configuration files are ignored
    assert {r.file_path for r in report.failed_checks} == {"/preview.json", "/preview_events.jsonl", "/stack_export.json"}
    assert not report.parsing_errors


def test_hardcoded_provider_credentials(tmp_path: Path) -> None:
    preview = json.loads((EXAMPLES_DIR / "aws" / "preview.json").read_text())
    # AWS documentation example keys, built at runtime to not trigger secret scanners
    preview["config"]["aws:accessKey"] = "AKIA" + "IOSFODNN7EXAMPLE"
    preview["config"]["aws:secretKey"] = "wJalrXUtnFEMI/K7MDENG/" + "bPxRfiCYEXAMPLEKEY"
    file_path = tmp_path / "preview.json"
    file_path.write_text(json.dumps(preview, indent=4))

    results = run_pulumi(file_path)

    assert results[("CKV_AWS_41", "aws.default")] == "FAILED"


def test_cli(tmp_path: Path) -> None:
    output_file = tmp_path / "results_json.json"
    ckv = Checkov(
        argv=[
            "-f", str(EXAMPLES_DIR / "aws" / "preview.json"),
            "--framework", "pulumi",
            "--check", "CKV_AWS_24,CKV2_AWS_6",
            "-o", "json",
            "--output-file-path", str(tmp_path),
            "--skip-download",
        ]
    )

    exit_code = ckv.run()

    assert exit_code == 1
    output = json.loads(output_file.read_text())
    assert output["check_type"] == "pulumi"
    assert output["summary"]["failed"] == 2
    assert output["summary"]["passed"] == 1
