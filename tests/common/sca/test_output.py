import responses

from checkov.common.sca.output import get_license_statuses


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
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
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
