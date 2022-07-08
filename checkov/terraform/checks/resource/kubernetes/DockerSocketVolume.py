from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DockerSocketVolume(BaseResourceCheck):
    def __init__(self) -> None:
        # Exposing the socket gives container information and increases risk of exploit
        # read-only is not a solution but only makes it harder to exploit.
        # Location: Pod.spec.volumes[].hostPath.path
        # Location: CronJob.spec.jobTemplate.spec.template.spec.volumes[].hostPath.path
        # Location: *.spec.template.spec.volumes[].hostPath.path
        id = "CKV_K8S_27"
        name = "Do not expose the docker daemon socket to containers"
        supported_resources = ["kubernetes_pod", "kubernetes_deployment", "kubernetes_daemonset"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]):
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED

        spec = conf['spec'][0]
        if "volume" in spec and spec.get("volume"):
            volumes = spec.get("volume")
            for idx, v in enumerate(volumes):
                if v.get("host_path"):
                    if "path" in v["host_path"][0]:
                        if v["host_path"][0]["path"] == ["/var/run/docker.sock"]:
                            self.evaluated_keys = ["spec/volume/{idx}/host_path/[0]/path"]
                            return CheckResult.FAILED
        if "template" in spec and spec.get("template"):
            template = spec.get("template")[0]
            if "spec" in template:
                temp_spec = template.get("spec")[0]
                if "volume" in temp_spec and temp_spec.get("volume"):
                    volumes = temp_spec.get("volume")
                    for idx, v in enumerate(volumes):
                        if v.get("host_path"):
                            if "path" in v["host_path"][0]:
                                path = v["host_path"][0]["path"]
                                if path == ["/var/run/docker.sock"]:
                                    return CheckResult.FAILED

        return CheckResult.PASSED


check = DockerSocketVolume()
