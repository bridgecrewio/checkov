import os
import responses
import requests
from unittest import mock

from checkov.common.util.http_utils import request_wrapper


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "5", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_all_fail_with_connection_error_for_get_scan_result(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/2e97f5afea42664309f492a1e2083b43479c2936"
    responses.add(
        method=responses.GET,
        url=mock_url,
        body=requests.exceptions.ConnectionError()
    )
    try:
        request_wrapper("GET", mock_url, {})
        assert False, "\'request_wrapper\' is expected to fail in this scenario"
    except requests.exceptions.ConnectionError:
        responses.assert_call_count(mock_url, 5)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "5", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_all_fail_with_connection_error_for_post_scan(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan"
    responses.add(
        method=responses.POST,
        url=mock_url,
        body=requests.exceptions.ConnectionError()
    )
    try:
        request_wrapper("POST", mock_url, {}, data={'mocked_key': 'mocked_value'})
        assert False, "\'request_wrapper\' is expected to fail in this scenario"
    except requests.exceptions.ConnectionError:
        responses.assert_call_count(mock_url, 5)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "5", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_all_fail_with_http_error(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/twistcli?os=linux"
    responses.add(
        method=responses.GET,
        url=mock_url,
        json={'error': "mocked client error"},
        status=403
    )
    request_wrapper("GET", mock_url, {})
    responses.assert_call_count(mock_url, 1)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "5", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_all_fail_with_http_error_should_call_raise_for_status(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/twistcli?os=linux"
    responses.add(
        method=responses.GET,
        url=mock_url,
        json={'error': "mocked client error"},
        status=403
    )
    try:
        request_wrapper("GET", mock_url, {}, should_call_raise_for_status=True)
        assert False, "\'request_wrapper\' is expected to fail in this scenario"
    except requests.exceptions.HTTPError:
        responses.assert_call_count(mock_url, 5)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "3", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_with_success_for_get_scan_result(mock_bc_integration, scan_result_success_response):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/2e97f5afea42664309f492a1e2083b43479c2936"
    responses.add(
        method=responses.GET,
        url=mock_url,
        json=scan_result_success_response,
        status=200
    )
    request_wrapper("GET", mock_url, {})
    responses.assert_call_count(mock_url, 1)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "3", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_with_success_for_download_twistcli(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/twistcli?os=linux"
    responses.add(
        method=responses.GET,
        url=mock_url,
        json={},
        status=200
    )
    request_wrapper("GET", mock_url, {})
    responses.assert_call_count(mock_url, 1)


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "3", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_with_success_for_post_scan(mock_bc_integration, scan_result_success_response):
    # given
    mock_url = mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan"
    responses.add(
        method=responses.POST,
        url=mock_url,
        json=scan_result_success_response,
        status=200
    )
    request_wrapper("POST", mock_url, {}, data={'mocked_key': 'mocked_value'})
    responses.assert_call_count(mock_url, 1)
