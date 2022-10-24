from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class PeerClientCertAuthTrue(BaseK8Check):

    def __init__(self):
        name = "Ensure that the --peer-client-cert-auth argument is set to true"
        id = "CKV_K8S_121"
        supported_kind = ['Pod']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf, entity_type=None):
        if conf.get("metadata", {}).get('name') == 'etcd':
            containers = conf.get('spec')['containers']
            for container in containers:
                if container.get("args") is not None:
                    if '--peer-client-cert-auth=true' not in container['args']:
                        return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = PeerClientCertAuthTrue()
