
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class RootContainersHighUID(BaseK8Check):

    def __init__(self):
        name = "Containers should run as a high UID to avoid host conflict"
        # runAsUser should be >= 10000 at pod spec or container level
        # Location: Pod.spec.runAsUser
        # Location: CronJob.spec.jobTemplate.spec.template.spec.securityContext.runAsUser
        # Location: *.spec.template.spec.securityContext.runAsUser
        id = "CKV_K8S_40"
        supported_kind = ['Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController', 'Job', 'CronJob']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)



    def get_resource_id(self, conf):
        if "namespace" in conf["metadata"]:
            return "{}.{}.{}".format(conf["kind"], conf["metadata"]["name"], conf["metadata"]["namespace"])
        else:
            return "{}.{}.default".format(conf["kind"], conf["metadata"]["name"])

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
            results["pod"]["runAsUser"] = check_runAsUser(spec)

            if spec.get("containers"):
                for c in spec["containers"]:
                    cresults = {}
                    cresults["runAsUser"] = check_runAsUser(c)
                    results["container"].append(cresults)

            # Evaluate pass / fail - Container values override Pod values
                # Pod runAsUser >= 10000, no override at container (PASSED)
                # Pod runAsUser >= 10000, override at container < 10000 (FAILED)
                # Pod runAsUser < 10000, no override at container (FAILED)
                # Pod runAsUser < 10000, override at container >= 10000 (PASSED)
                # Pod runAsUser not set, container runAsUser not set or < 10000 (FAILED)
                # Pod runAsUser not set, container runAsUser set >= 10000 (PASSED)
            if results["pod"]["runAsUser"] == "PASSED":
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED":
                        return CheckResult.FAILED
                return CheckResult.PASSED
            elif results["pod"]["runAsUser"] == "FAILED":
                containeroverride = False
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED" or cr["runAsUser"] == "ABSENT":
                        return CheckResult.FAILED
                    elif cr["runAsUser"] == "PASSED":
                        containeroverride = True
                if containeroverride:
                    return CheckResult.PASSED
                return CheckResult.FAILED
            else:
                # Pod runAsUser ABSENT
                containeroverride = False
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED" or cr["runAsUser"] == "ABSENT":
                        return CheckResult.FAILED
                    elif cr["runAsUser"] == "PASSED":
                        containeroverride = True
                if containeroverride:
                    return CheckResult.PASSED
                return CheckResult.FAILED

        return CheckResult.FAILED

check = RootContainersHighUID()

def check_runAsUser(spec):
    if "securityContext" in spec:
        if "runAsUser" in spec["securityContext"]:
            if spec["securityContext"]["runAsUser"] >= 10000:
                return "PASSED"
            else:
                return "FAILED"
    return "ABSENT"


