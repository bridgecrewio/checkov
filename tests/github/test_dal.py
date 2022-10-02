import os
from unittest import mock

from pytest_mock import MockerFixture

from checkov.github.dal import Github


@mock.patch.dict(os.environ, {"GITHUB_ORG": "simpleOrg"}, clear=True)
def test_org_security_null_description(mocker: MockerFixture):
    dal = Github()
    mock_data = {
        "data": {
            "organization": {
                "name": "Bridgecrew",
                "login": "Bridgecrew-dev",
                "description": None,
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

@mock.patch.dict(os.environ, {"GITHUB_ORG": "simpleOrg"}, clear=True)
def test_org_security_str_description(mocker: MockerFixture):
    dal = Github()
    mock_data2 = {
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
    mocker.patch("checkov.common.vcs.base_vcs_dal.BaseVCSDAL._request_graphql", return_value=mock_data2)
    result = dal.get_organization_security()
    assert result


def test_validate_github_conf_paths():
    dal = Github()
    all_github_conf_files_conf_declared = dal.github_conf_dir_path \
        and dal.github_org_security_file_path and dal.github_branch_protection_rules_file_path \
        and dal.github_org_webhooks_file_path and dal.github_repository_webhooks_file_path \
        and dal.github_repository_collaborators_file_path
    assert all_github_conf_files_conf_declared
