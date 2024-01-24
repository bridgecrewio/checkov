import os
import responses
import requests
from unittest import mock
import pytest
from pytest_mock import MockerFixture
from aioresponses import aioresponses
import aiohttp

from checkov.common.util.http_utils import request_wrapper, aiohttp_client_session_wrapper, valid_url


def get_report_url() -> str:
    base_url = "https://www.bridgecrew.cloud/api/v1/vulnerabilities"
    return f"{base_url}/results"


@responses.activate
@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "5", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
def test_request_wrapper_all_fail_with_connection_error_for_get_scan_result(mock_bc_integration):
    # given
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan-results/2e97f5afea42664309f492a1e2083b43479c2936"
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
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan"
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
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/twistcli?os=linux"
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
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/twistcli?os=linux"
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
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan-results/2e97f5afea42664309f492a1e2083b43479c2936"
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
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/twistcli?os=linux"
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
    mock_url = mock_bc_integration.api_url + "/api/v1/vulnerabilities/scan"
    responses.add(
        method=responses.POST,
        url=mock_url,
        json=scan_result_success_response,
        status=200
    )
    request_wrapper("POST", mock_url, {}, data={'mocked_key': 'mocked_value'})
    responses.assert_call_count(mock_url, 1)


@pytest.mark.asyncio
async def test_aiohttp_client_session_wrapper_with_one_handled_exception(mocker: MockerFixture, mock_bc_integration):
    # given
    bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    report_url = get_report_url()

    mocker.patch.dict(os.environ, {"BC_ROOT_DIR": "app", "REQUEST_MAX_TRIES": "3", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})

    # when
    with aioresponses() as m:
        m.post(report_url, exception=aiohttp.ClientOSError())
        m.post(report_url, status=200, repeat=True)

        result = await aiohttp_client_session_wrapper(get_report_url(), {}, {})

    # then
    assert result == 0


@pytest.mark.asyncio
async def test_aiohttp_client_session_wrapper_with_several_handled_exceptions(mocker: MockerFixture, mock_bc_integration):
    # given
    bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    report_url = get_report_url()

    mocker.patch.dict(os.environ, {"BC_ROOT_DIR": "app", "REQUEST_MAX_TRIES": "3", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})

    # when
    with aioresponses() as m:
        m.post(report_url, exception=aiohttp.ClientOSError(), repeat=True)
        try:
            await aiohttp_client_session_wrapper(get_report_url(), {}, {})

            # case the specific error wasn't raised
            assert False

        except aiohttp.ClientOSError:
            # case the specific error was raised
            assert True


@pytest.mark.asyncio
async def test_raiohttp_client_session_wrapper_with_one_not_handled_exception(mocker: MockerFixture, mock_bc_integration):
    # given
    bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    report_url = get_report_url()

    mocker.patch.dict(os.environ, {"BC_ROOT_DIR": "app", "REQUEST_MAX_TRIES": "3", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})

    # when
    with aioresponses() as m:
        m.post(report_url, exception=aiohttp.ServerTimeoutError())
        try:
            await aiohttp_client_session_wrapper(get_report_url(), {}, {})
            # case that specific error wasn't raised
            assert False

        except aiohttp.ServerTimeoutError:
            # case the specific error was raised
            assert True


@pytest.mark.parametrize(
    "input,expected",
    [
        (None, False),
        ("", False),
        ("/path/to", False),
        ("some random text", False),
        ("https://www.checkov.io", True),
        ("https://docs.bridgecrew.io/docs/bc_aws_iam_45", True),
    ],
    ids=["None", "empty", "local path", "text", "url", "url with subdirectory"],
)
def test_valid_url(input, expected):
    assert valid_url(input) == expected