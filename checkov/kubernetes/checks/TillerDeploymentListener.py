from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check
from checkov.kubernetes.checks.Tiller import Tiller


class TillerDeploymentListener(BaseK8Check):

    def __init__(self):
        name = "Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster"
        id = "CKV_K8S_45"
        # Location: container .image
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):

        # reuse the existing logic in case it ever changes.
        is_tiller = Tiller().scan_spec_conf(conf) == CheckResult.FAILED

        if not is_tiller:
            return CheckResult.UNKNOWN

        args = conf.get('args')
        if args:
            for arg in args:
                if '--listen' in arg and ('localhost' in arg or '127.0.0.1' in arg):
                    return CheckResult.PASSED

        return CheckResult.FAILED

check = TillerDeploymentListener()
