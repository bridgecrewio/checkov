from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class HostPort(BaseK8Check):

    def __init__(self):
        """
        https://kubernetes.io/docs/concepts/configuration/overview/

        Don’t specify a hostPort for a Pod unless it is absolutely necessary.
        When you bind a Pod to a hostPort, it limits the number of places the
        Pod can be scheduled, because each <hostIP, hostPort, protocol> combination
        must be unique.
        """
        name = "Do not specify hostPort unless absolutely necessary"
        id = "CKV_K8S_26"
        # Location: container .ports[].hostPort
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "ports" in conf:
            for port in conf["ports"]:
                if "hostPort" in port:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = HostPort()
