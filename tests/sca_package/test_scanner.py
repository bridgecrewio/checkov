import asyncio
from pathlib import Path
import responses
from checkov.common.util.tqdm_utils import ProgressBar

from checkov.sca_package.scanner import Scanner

EXAMPLES_DIR = Path(__file__).parent / "examples"


@responses.activate
def test_run_scan(mock_bc_integration, scan_result2, scan_result_success_response):
    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan",
        json={'id': '2e97f5afea42664309f492a1e2083b43479c2935', 'status': 'running'},
        status=202,
    )

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan-results/"
                                             "2e97f5afea42664309f492a1e2083b43479c2935",
        json=scan_result_success_response,
        status=200
    )

    # when
    pbar = ProgressBar('')
    pbar.turn_off_progress_bar()
    scanner = Scanner(pbar)
    result = asyncio.run(scanner.run_scan((Path(EXAMPLES_DIR / "requirements.txt"))))

    # then
    assert len(result) == len(scan_result2)
    assert result.keys() == scan_result2.keys()
    assert len(result.get("packages")) == len(scan_result2.get("packages"))
    result_vuln_len = len(result.get("vulnerabilities"))
    scan_result_vuln_len = len(scan_result2.get("vulnerabilities"))
    assert result_vuln_len == scan_result_vuln_len
    assert sorted([result.get("vulnerabilities")[i]["id"] for i in range(result_vuln_len)]) == \
        sorted([scan_result2.get("vulnerabilities")[i]["id"] for i in range(scan_result_vuln_len)])
    assert result.get("complianceDistribution") == scan_result2.get("complianceDistribution")
    assert result.get("vulnerabilityDistribution") == scan_result2.get("vulnerabilityDistribution")
    responses.assert_call_count(mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan", 1)
    assert len(responses.calls) >= 2


@responses.activate
def test_run_scan_fail_on_scan(mock_bc_integration):
    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan",
        json={'id': '2e97f5afea42664309f492a1e2083b43479c2936', 'status': 'running'},
        status=202,
    )

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan-results/"
                                             "2e97f5afea42664309f492a1e2083b43479c2936",
        json={
            "outputType": "Error",
            "outputData": "error_message"
        },
        status=400,
    )

    # when
    pbar = ProgressBar('')
    pbar.turn_off_progress_bar()
    result = asyncio.run(Scanner(pbar).run_scan(input_path=Path(EXAMPLES_DIR / "requirements.txt")))

    # then
    assert result == {}
    responses.assert_call_count(mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan", 1)
    assert len(responses.calls) >= 2
