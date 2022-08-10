import os
from unittest import mock

from pytest_mock import MockerFixture

from checkov.github.dal import Github


@mock.patch.dict(os.environ, {"GITHUB_ORG": "simpleOrg"}, clear=True)
def test_org_security(mocker: MockerFixture):
    dal = Github()
    mock_data = {
        "data": {
            "organization": {
                "name": "Bridgecrew",
                "login": "Bridgecrew-dev",
                "description": "",
                "ipAllowListEnabledSetting": "DISABLED",
                "ipAllowListForInstalledAppsEnabledSetting": "DISABLED",
                "requiresTwoFactorAuthentication": False,
                "samlIdentityProvider": None
            }
        }
    }
    mocker.patch("checkov.common.vcs.base_vcs_dal.BaseVCSDAL._request_graphql", return_value=mock_data)
    result = dal.get_organization_security()
    assert result
