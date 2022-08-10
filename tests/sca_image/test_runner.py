from pathlib import Path
from urllib.parse import quote_plus

import responses

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.sca_image.runner import Runner
from checkov.github_actions.runner import Runner as GHA_Runner

EXAMPLES_DIR = Path(__file__).parent / "examples/.github/workflows"


@responses.activate
def test_image_referencer_trigger_image_flow_calls(mock_bc_integration, image_name, cached_scan_result):
    # given
    image_id_encoded = quote_plus(f"image:{image_name}")

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
        json=cached_scan_result,
        status=200,
    )

    # when
    image_runner = Runner()
    image_runner.image_referencers = [GHA_Runner()]
    report = image_runner.run(root_folder=EXAMPLES_DIR)

    # then
    assert len(responses.calls) == 1
    responses.assert_call_count(
        mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", 1
    )

    assert len(report.failed_checks) == 3


@responses.activate
def test_runner_honors_enforcement_rules(mock_bc_integration, image_name, cached_scan_result):
    # given
    image_id_encoded = quote_plus(f"image:{image_name}")

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
        json=cached_scan_result,
        status=200,
    )

    # when
    image_runner = Runner()
    filter = RunnerFilter(framework=['sca_image'], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.SCA_IMAGE: Severities[BcSeverities.OFF]}
    image_runner.image_referencers = [GHA_Runner()]
    report = image_runner.run(root_folder=EXAMPLES_DIR, runner_filter=filter)

    summary = report.get_summary()
    # then
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 3
    assert summary["parsing_errors"] == 0
