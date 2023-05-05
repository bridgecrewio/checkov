from __future__ import annotations

import pytest

from checkov.cdk.runner import CdkRunner

CHECK_ID_MAP: dict[str, str] = {}  # will be filled via setup()


@pytest.fixture(scope="module", autouse=True)
def setup() -> None:
    global CHECK_ID_MAP

    registry = CdkRunner().registry
    registry.load_rules(frameworks=[], sast_languages={})  # framework doesn't matter currently

    for check in registry.rules:
        for lang in check['languages']:
            CHECK_ID_MAP[f"{lang}_{check['metadata']['check_file'].split('.')[0]}"] = check['id']
