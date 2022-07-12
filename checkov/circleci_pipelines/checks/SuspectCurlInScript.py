from __future__ import annotations
from typing import Any

from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType

class SuspectCurlInScript(BaseCircleCIPipelinesCheck):
    def __init__(self) -> None:
        name = "Suspicious use of curl in run task"
        id = "CKV_CIRCLECIPIPELINES_7"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['jobs.*.steps[]']
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if "run" not in conf:
            return CheckResult.PASSED, conf
        run = conf.get("run", "")
        if type(run) == dict:
            run = run.get("command", "")
        if "curl" in run:
            badstuff = ['curl', 'POST']
            lines = run.split("\n")
            for line in lines:
                if all(x in line for x in badstuff):
                    return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf

check = SuspectCurlInScript()
