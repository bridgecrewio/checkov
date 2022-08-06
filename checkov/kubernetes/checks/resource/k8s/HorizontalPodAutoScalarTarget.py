from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class HorizontalPodAutoScalarTarget(BaseK8Check):

    def __init__(self):
        name = "Target for HorizontalPodAutoscaler does not exist."
        id = "CKV_K8S_900"
        # Location: PodSecurityPolicy.annotations.seccomp.security.alpha.kubernetes.io/defaultProfileName
        supported_kind = ['collection']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

   def scan_spec_conf(self, conf):
        entity_conf = conf[self.evaluated_keys[0]][0]
        entity_type = entity_conf.get("kind")
        if entity_type =="HorizontalPodAutoscaler":
             if self.find_target(entity_conf.get("spec"), conf):
                 return CheckResult.PASSED
             else:
                 return CheckResult.FAILED
        return CheckResult.UNKNOWN

    def find_target(self, spec, conf):
        if "scaleTargetRef" in spec:
            if "kind" in spec["scaleTargetRef"]:
                kind = spec["scaleTargetRef"]["kind"]
            if "name" in spec["scaleTargetRef"]:
                name = spec["scaleTargetRef"]["name"]
            if name and spec:
                for k8_file in conf.keys():
                    for entity_conf in conf[k8_file]:
                        entity_type = entity_conf.get("kind")
                        if kind == entity_type:
                            if "metadata" in entity_conf:
                                if "name" in entity_conf["metadata"]:
                                    if name == entity_conf["metadata"]["name"]:
                                        return True
            else:
                return False
        return False

check = HorizontalPodAutoScalarTarget()
