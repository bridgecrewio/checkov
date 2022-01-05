
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class RootContainers(BaseK8Check):

    def __init__(self):
        # CIS-1.3 1.7.6
        # CIS-1.5 5.2.6
        name = "Minimize the admission of root containers"
        # Check runAsNonRoot.  If false, then ensure runAsUser > 0
        # Location: Pod.spec.runAsUser / runAsNonRoot
        # Location: CronJob.spec.jobTemplate.spec.template.spec.securityContext.runAsUser / runAsNonRoot
        # Location: *.spec.template.spec.securityContext.runAsUser / runAsNonRoot
        id = "CKV_K8S_23"
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        spec = {}

        if conf['kind'] == 'Pod':
            if "spec" in conf:
                spec = conf["spec"]
        elif conf['kind'] == 'CronJob':
            if "spec" in conf:
                if "jobTemplate" in conf["spec"]:
                    if "spec" in conf["spec"]["jobTemplate"]:
                        if "template" in conf["spec"]["jobTemplate"]["spec"]:
                            if "spec" in conf["spec"]["jobTemplate"]["spec"]["template"]:
                                spec = conf["spec"]["jobTemplate"]["spec"]["template"]["spec"]
        else:
            inner_spec = self.get_inner_entry(conf, "spec")
            spec = inner_spec if inner_spec else spec

        # Collect results
        if spec:
            results = {}
            results["pod"] = {}
            results["container"] = []
            results["pod"]["runAsNonRoot"] = check_runAsNonRoot(spec)
            results["pod"]["runAsUser"] = check_runAsUser(spec)

            if spec.get("containers"):
                for c in spec["containers"]:
                    cresults = {}
                    cresults["runAsNonRoot"] = check_runAsNonRoot(c)
                    cresults["runAsUser"] = check_runAsUser(c)
                    results["container"].append(cresults)

            # Evaluate pass / fail
            # Container values override Pod values
            # Pod runAsNonRoot == True, plus no override at container spec   (PASSED)
            # Pod runAsNonRoot == True, but container runAsNonRoot == False
            #                     If runAsUser failed or absent (FAILED)
            #                     if runAsUser passed, the check will pass (but don't want to pass one container if another fails)
            if results["pod"]["runAsNonRoot"] == "PASSED":
                for cr in results["container"]:
                    if cr["runAsNonRoot"] == "FAILED":
                        if cr["runAsUser"] == "FAILED" or cr["runAsUser"] == "ABSENT":
                            return CheckResult.FAILED
                return CheckResult.PASSED
            elif results["pod"]["runAsUser"] == "PASSED":
                # Pod runAsNonRoot == False (or absent) ; Pod runAsUser > 0 (PASSED)
                # If container runAsUser FAILED, then overall fail as it overrides pod (FAILED)
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED":
                        return CheckResult.FAILED
                return CheckResult.PASSED
            else:
                # Pod runAsNonRoot and runAsUser failed or absent
                #   If container runAsNonRoot true (PASSED)
                #   If container runAsNonRoot failed or absent, but runAsUser passed (PASSED)
                #   If container runAsNonRoot failed or absent, but runAsUser failed/absent (FAILED)
                for cr in results["container"]:

                    if cr["runAsNonRoot"] == "PASSED":
                        continue
                    if cr["runAsNonRoot"] == "FAILED" or cr["runAsNonRoot"] == "ABSENT":
                        if cr["runAsUser"] == "PASSED":
                            continue
                        else:
                            return CheckResult.FAILED
                return CheckResult.PASSED

        return CheckResult.FAILED

check = RootContainers()

def check_runAsNonRoot(spec):
    if spec.get("securityContext"):
        if "runAsNonRoot" in spec["securityContext"]:
            if spec["securityContext"]["runAsNonRoot"]:
                return "PASSED"
            else:
                return "FAILED"
    return "ABSENT"

def check_runAsUser(spec):
    if spec.get("securityContext"):
        if "runAsUser" in spec["securityContext"]:
            if spec["securityContext"]["runAsUser"] > 0:
                return "PASSED"
            else:
                return "FAILED"
    return "ABSENT"


