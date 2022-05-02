import asyncio
import os
from pathlib import Path
import responses
import requests
from unittest import mock

from checkov.sca_package.scanner import Scanner

EXAMPLES_DIR = Path(__file__).parent / "examples"


@responses.activate
def test_run_scan(mock_bc_integration, scan_result2, scan_result_success_response):
    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan",
        json={'id': '2e97f5afea42664309f492a1e2083b43479c2935', 'status': 'running'},
        status=202,
    )

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/"
                                             "2e97f5afea42664309f492a1e2083b43479c2935",
        json=scan_result_success_response,
        status=200
    )

    # when
    scanner = Scanner()
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
    responses.assert_call_count(mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan", 1)
    assert len(responses.calls) >= 2


@responses.activate
def test_run_scan_fail_on_scan(mock_bc_integration):
    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan",
        json={'id': '2e97f5afea42664309f492a1e2083b43479c2936', 'status': 'running'},
        status=202,
    )

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/"
                                             "2e97f5afea42664309f492a1e2083b43479c2936",
        json={
            "outputType": "Error",
            "outputData": "error_message"
            },
        status=400,
    )

    # when
    result = asyncio.run(Scanner().run_scan(input_path=Path(EXAMPLES_DIR / "requirements.txt")))

    # then
    assert result == {}
    responses.assert_call_count(mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan", 1)
    assert len(responses.calls) >= 2


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "5", "REQUEST_SLEEP_BETWEEN_TRIES": "0"})
def test_request_wrapper_all_fail(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/2e97f5afea42664309f492a1e2083b43479c2936"
    responses.add(
        method=responses.GET,
        url=mock_url,
        body=requests.exceptions.ConnectionError()
    )
    try:
        Scanner().request_wrapper("GET", mock_url, {})
        assert False, "\'request_wrapper\' expected to ve failed in this scenario"
    except requests.exceptions.ConnectionError:
        responses.assert_call_count(mock_url, 5)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "3", "REQUEST_SLEEP_BETWEEN_TRIES": "0"})
def test_request_wrapper_with_success(mock_bc_integration, scan_result_success_response):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/2e97f5afea42664309f492a1e2083b43479c2936"
    responses.add(
        method=responses.GET,
        url=mock_url,
        json=scan_result_success_response,
        status=200
    )
    Scanner().request_wrapper("GET", mock_url, {})
    responses.assert_call_count(mock_url, 1)

