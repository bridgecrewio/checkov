import json
import os
from pathlib import Path

from pytest_mock import MockerFixture

from checkov.azure_devops.dal import AzureDevOps

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_persist_policies(mocker: MockerFixture, tmp_path: Path):
    #  given
    test_file = EXAMPLES_DIR / "minimum_number_of_reviewers.json"

    mocker.patch("checkov.azure_devops.dal.AzureDevOps._request", return_value=json.loads(test_file.read_text()))
    mocker.patch("checkov.azure_devops.dal.Path.cwd", return_value=tmp_path)

    mocker.patch.dict(
        os.environ,
        {
            "BUILD_REPOSITORY_ID": "12345678-abcd-1234-abcd-1234567890",
            "SYSTEM_PULLREQUEST_TARGETBRANCH": "refs/heads/main",
        },
    )
    azure_devops = AzureDevOps()
    azure_devops.conf_dir_path = tmp_path

    #  when
    azure_devops.persist_policies()

    # then
    policies_path = azure_devops.conf_file_paths["policies"][0]
    policies = json.loads(policies_path.read_text())

    assert len(policies) == 1
    assert policies[0]["settings"] == {
        "minimumApproverCount": 1,
        "creatorVoteCounts": False,
        "allowDownvotes": False,
        "resetOnSourcePush": False,
        "requireVoteOnLastIteration": False,
        "resetRejectionsOnSourcePush": False,
        "blockLastPusherVote": False,
        "scope": [
            {
                "refName": "refs/heads/main",
                "matchKind": "Exact",
                "repositoryId": "12345678-abcd-1234-abcd-1234567890",
            }
        ],
    }


def test_validate_github_conf_paths():
    # check that all the files in github_conf folder that should be updated with new data from GitHub api reply,
    # are empty. In case of no reply-no old data should be left causing confusion with new retrieved data.
    dal = AzureDevOps()

    all_files_are_empty = True
    for github_conf_type, files in dal.conf_file_paths.items():
        for file_path in files:
            all_files_are_empty &= not os.path.isfile(file_path) or os.path.getsize(file_path) == 0

    assert all_files_are_empty
