import os
import platform
from pathlib import Path
from urllib.parse import quote_plus

import responses
from pytest_mock import MockerFixture

from checkov.sca_image.runner import Runner
from checkov.github_actions.runner import Runner as GHA_Runner

EXAMPLES_DIR = Path(__file__).parent / "examples/.github/workflows"


@responses.activate
def test_image_referencer_trigger_image_flow_calls(mocker: MockerFixture, image_id, mock_bc_integration, empty_report):
    # can be removed after feature flag is removed
    os.environ["CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING"] = "TRUE"

    image_id_encoded = quote_plus(image_id)

    mocker.patch('checkov.common.images.image_referencer.ImageReferencer.pull_image', return_value=image_id)
    # async_mocker.patch('checkov.sca_image.runner.Runner.execute_scan', return_value=empty_report)

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
        json={'outputType': 'Empty'},
        status=202,
    )
    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/twistcli?os={platform.system().lower()}",
        json={},
        status=200
    )
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results",
        json={},
        status=202
    )

    image_runner = Runner()
    image_runner.image_referencers = [GHA_Runner()]
    image_runner.run(root_folder=EXAMPLES_DIR)

    responses.assert_call_count(
        mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", 1)
    responses.assert_call_count(mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results", 1)

    assert len(responses.calls) >= 2
