from __future__ import annotations

from pathlib import Path

import pytest

from checkov.common.output.report import CheckType
from checkov.helm.runner import Runner
from tests.helm.utils import helm_exists

RESOURCES_PATH = Path(__file__).parent / "runner" / "resources"


@pytest.mark.skipif(not helm_exists(), reason="helm not installed")
def test_multiple_resources():
    runner = Runner()
    report = runner.run(
        root_folder=str(RESOURCES_PATH / "multiple"),
    )

    # The helm chart contains one template with two resources.
    # Neither resource has a namespace.

    assert len(report.failed_checks) == 2
    assert report.check_type == CheckType.HELM

    assert len(report.resources) == 2
    for resource in report.resources:
        assert "templates/test.yaml" in resource
