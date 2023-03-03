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


@mock.patch.dict(os.environ, {"GITHUB_REPO_OWNER": "bridgecrew", "GITHUB_REPOSITORY": "main"}, clear=True)
def test_org_webhooks(mocker: MockerFixture):
    dal = Github()
    mock_data = [
        {
            "type": "Organization",
            "id": 0,
            "name": "web",
            "active": True,
            "events": [
                "*"
            ],
            "config": {
                "content_type": "form",
                "insecure_ssl": "0",
                "url": "http://test-repo-webhook.com"
            },
            "updated_at": "2022-10-02T12:39:12Z",
            "created_at": "2022-09-29T09:01:36Z",
            "url": "",
            "test_url": "",
            "ping_url": "",
            "deliveries_url": ""
        }
    ]
    mocker.patch("checkov.common.vcs.base_vcs_dal.BaseVCSDAL._request", return_value=mock_data)
    result = dal.get_repository_webhooks()
    assert result


@mock.patch.dict(os.environ, {"GITHUB_REPO_OWNER": "bridgecrew", "GITHUB_REPOSITORY": "main"}, clear=True)
def test_repository_webhooks(mocker: MockerFixture):
    dal = Github()
    mock_data = [
        {
            "type": "Repository",
            "id": 0,
            "name": "web",
            "active": True,
            "events": [
                "*"
            ],
            "config": {
                "content_type": "form",
                "insecure_ssl": "0",
                "url": "http://test-repo-webhook.com"
            },
            "updated_at": "2022-10-02T12:39:12Z",
            "created_at": "2022-09-29T09:01:36Z",
            "url": "",
            "test_url": "",
            "ping_url": "",
            "deliveries_url": ""
        }
    ]
    mocker.patch("checkov.common.vcs.base_vcs_dal.BaseVCSDAL._request", return_value=mock_data)
    result = dal.get_repository_webhooks()
    assert result


def test_validate_github_conf_paths():
    # check that all the files in github_conf folder that should be updated with new data from GitHub api reply,
    # are empty.In case of no reply-no old data should be left causing confusion with new retrieved data.
    dal = Github()

    all_files_are_empty = True
    for github_conf_type, files in dal.github_conf_file_paths.items():
        for file_path in files:
            all_files_are_empty &= not os.path.isfile(file_path) or os.path.getsize(file_path) == 0

    assert all_files_are_empty
