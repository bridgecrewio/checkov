from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.common.util.consts import START_LINE
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.github_actions.common.artifact_build import buildcmds as buildcmds
from checkov.github_actions.common.build_actions import buildactions as buildactions
from checkov.yaml_doc.enums import BlockType


class CosignSignSBOM(BaseGithubActionsCheck):
    def __init__(self) -> None:
        name = "Found artifact build without evidence of cosign sbom attestation in pipeline"
        id = "CKV_GHA_6"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.OBJECT,
            supported_entities=['jobs']
        )

    def scan_entity_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        build_found = False
        for jobname, jobdetail in conf.items():
            if jobname == START_LINE:
                return CheckResult.PASSED, conf
            steps = jobdetail.get("steps")
            if steps:
                for step in steps:
                    if build_found:
                        run = step.get("run", "")
                        if all(word in run for word in ("cosign", "sbom")):
                            return CheckResult.PASSED, step
                    else:
                        uses = step.get("uses")
                        if uses is not None and any(action in uses for action in buildactions):
                            build_found = True
                        run = step.get("run")
                        if run is not None and any(build in run for build in buildcmds):
                            build_found = True

        if build_found:
            return CheckResult.FAILED, conf            
        return CheckResult.PASSED, conf


check = CosignSignSBOM()
