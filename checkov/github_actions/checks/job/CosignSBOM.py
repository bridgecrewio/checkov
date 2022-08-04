from checkov.common.models.enums import CheckResult
from checkov.common.util.consts import START_LINE
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.github_actions.common.artifact_build import buildcmds as buildcmds
from checkov.github_actions.common.build_actions import buildactions as buildactions
from checkov.yaml_doc.enums import BlockType


class CosignSignSBOM(BaseGithubActionsCheck):
    def __init__(self):
        name = "Found artifact build without evidence of cosign sbom attestation in pipeline"
        id = "CKV_GHA_6"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.OBJECT,
            supported_entities=['jobs']
        )

    def scan_entity_conf(self, conf):
        buildfound = False
        for jobname, jobdetail in conf.items():
            if jobname == START_LINE:
                return CheckResult.PASSED, conf
            steps = jobdetail.get("steps")
            if steps:
                for step in steps:
                    if buildfound is False:
                        uses = step.get("uses")
                        if uses is not None:
                            for action in buildactions:
                                if action in uses:
                                    buildfound = True                    
                        run = step.get("run")
                        if run is not None:
                            for build in buildcmds:
                                if build in run:
                                    buildfound = True
                    else:                     
                        run = step.get("run","none")
                        if all(word in run for word in ("cosign", "sbom")):
                            return CheckResult.PASSED, step
        if buildfound:
            return CheckResult.FAILED, conf            
        return CheckResult.PASSED, conf


check = CosignSignSBOM()
