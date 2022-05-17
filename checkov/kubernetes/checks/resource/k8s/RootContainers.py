from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_root_container_check import BaseK8sRootContainerCheck


class RootContainers(BaseK8sRootContainerCheck):
    def __init__(self):
        # CIS-1.3 1.7.6
        # CIS-1.5 5.2.6
        name = "Minimize the admission of root containers"
        # Check runAsNonRoot.  If false, then ensure runAsUser > 0
        # Location: Pod.spec.runAsUser / runAsNonRoot
        # Location: CronJob.spec.jobTemplate.spec.template.spec.securityContext.runAsUser / runAsNonRoot
        # Location: *.spec.template.spec.securityContext.runAsUser / runAsNonRoot
        id = "CKV_K8S_23"
        super().__init__(name=name, id=id)

    def scan_spec_conf(self, conf):
        spec = self.extract_spec(conf)

        # Collect results
        if spec:
            results = {"pod": {}, "container": []}
            results["pod"]["runAsNonRoot"] = self.check_runAsNonRoot(spec)
            results["pod"]["runAsUser"] = self.check_runAsUser(spec, 1)

            if spec.get("containers"):
                for c in spec["containers"]:
                    cresults = {"runAsNonRoot": self.check_runAsNonRoot(c), "runAsUser": self.check_runAsUser(c, 1)}
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
