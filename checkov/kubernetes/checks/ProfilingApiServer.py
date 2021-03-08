from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ProfilingApiServer(BaseK8Check):
    def __init__(self):
        # CIS-1.6 1.2.21
        id = "CKV2_K8S_42"
        name = "Ensure that the --profiling argument is set to false (Scored)"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['pod']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def scan_spec_conf(self, conf):
        if "spec" in conf:
            if "command" in conf["spec"]:
                if "--profiling=false" in conf["spec"]["command"]:
                    return CheckResult.PASSED
           
        return CheckResult.FAILED

check = ProfilingApiServer()