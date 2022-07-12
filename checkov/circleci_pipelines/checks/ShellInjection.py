from __future__ import annotations
from typing import Any

from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.circleci_pipelines.common.shell_injection_list import terms as bad_inputs
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType
import re


class DontAllowShellInjection(BaseCircleCIPipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure run commands are not vulnerable to shell injection"
        id = "CKV_CIRCLECIPIPELINES_6"
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
        if isinstance(run, dict):
            command = run.get("command", "")
            for term in bad_inputs:
                if re.search(term, command):
                    return CheckResult.FAILED, conf

        else:
            for term in bad_inputs:
                if re.search(term, run):
                    return CheckResult.FAILED, conf

        return CheckResult.PASSED, conf


check = DontAllowShellInjection()
