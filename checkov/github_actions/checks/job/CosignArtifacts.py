from checkov.common.models.enums import CheckResult
from checkov.common.util.consts import START_LINE
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.github_actions.common.artifact_build import buildcmds as buildcmds
from checkov.github_actions.common.build_actions import buildactions as buildactions
from checkov.yaml_doc.enums import BlockType


class CosignSignPresent(BaseGithubActionsCheck):
    def __init__(self):
        name = "Found artifact build without evidence of cosign sign execution in pipeline"
        id = "CKV_GHA_5"
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
                        run = step.get("run","")            
                        if "cosign sign" in run:
                            return CheckResult.PASSED, step
        if buildfound:
            return CheckResult.FAILED, conf            
        return CheckResult.PASSED, conf


check = CosignSignPresent()
