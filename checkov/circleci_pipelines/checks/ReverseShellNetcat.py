from __future__ import annotations
from typing import Any

from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType
import re


class ReverseShellNetcat(BaseCircleCIPipelinesCheck):
    def __init__(self) -> None:
        name = "Suspicious use of netcat with IP address"
        id = "CKV_CIRCLECIPIPELINES_5"
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
            if re.search(r'(nc|netcat) (\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})', command):
                return CheckResult.FAILED, conf
        else:
            if re.search(r'(nc|netcat) (\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})', run):
                return CheckResult.FAILED, conf
                
        return CheckResult.PASSED, conf


check = ReverseShellNetcat()
