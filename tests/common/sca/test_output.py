import os
from unittest import mock

import responses

from checkov.common.sca.output import get_license_statuses, _get_request_input


def test_get_request_input():
    packages_input = [
        {"name": "docutils", "version": "0.15.2", "type": "python"},
        {"name": "github.com/apparentlymart/go-textseg/v12", "version": "v12.0.0", "lang": "go"},
        {"name": "ruby_package", "version": "9.9.9", "type": "ruby"},
        {"name": "ruby_package2", "version": "8.8.8", "type": "gem"},
        {"name": "empty_type_package", "version": "8.8.8", "type": ""},
        {"name": "invalid_type_package", "version": "8.8.8", "type": "bbbbb"}
    ]
    request_input = _get_request_input(packages_input)

    assert request_input == [
        {'name': 'docutils', 'version': '0.15.2', 'lang': 'python'},
        {'name': 'github.com/apparentlymart/go-textseg/v12', 'version': 'v12.0.0', 'lang': ''},
        {'name': 'ruby_package', 'version': '9.9.9', 'lang': 'ruby'},
        {'name': 'ruby_package2', 'version': '8.8.8', 'lang': 'ruby'},
        {'name': 'empty_type_package', 'version': '8.8.8', 'lang': ''},
        {'name': 'invalid_type_package', 'version': '8.8.8', 'lang': 'bbbbb'}
    ]


@responses.activate
def test_licenses_status(mock_bc_integration):
    packages_input = [
        {"name": "docutils", "version": "0.15.2", "lang": "python"},
        {"name": "github.com/apparentlymart/go-textseg/v12", "version": "v12.0.0", "lang": "go"}
    ]

    response_json = {
        "violations": [
            {
                "name": "github.com/apparentlymart/go-textseg/v12",
                "version": "v12.0.0",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
            {
                "name": "docutils",
                "version": "0.15.2",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
        ]
    }

    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )

    license_statuses = get_license_statuses(packages_input)
    assert license_statuses == [
        {
            "package_name": "github.com/apparentlymart/go-textseg/v12",
            "package_version": "v12.0.0",
            "policy": "BC_LIC_1",
            "license": "Apache-2.0",
            "status": "COMPLIANT",
        },
        {
            "package_name": "docutils",
            "package_version": "0.15.2",
            "policy": "BC_LIC_1",
            "license": "Apache-2.0",
            "status": "COMPLIANT",
        },
    ]


@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "1", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
@responses.activate
def test_licenses_status_on_failure(mock_bc_integration):
    # given
    packages_input = [
        {"name": "docutils", "version": "0.15.2", "lang": "python"},
        {"name": "github.com/apparentlymart/go-textseg/v12", "version": "v12.0.0", "lang": "go"}
    ]

    responses.add(
        method=responses.POST,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        status=500
    )

    # when
    # we expect no failure here, in case of a http/connection error
    license_statuses = get_license_statuses(packages_input)

    # then
    assert len(license_statuses) == 0
