from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeShieldedVM(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Compute instances are launched with Shielded VM enabled"
        id = "CKV_GCP_39"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Shielded VM can only be used with boot images with shielded VM support.
        See the complete list of supporting images here: https://cloud.google.com/compute/docs/images#shielded-images
        :param conf:
        :return: <checkResult>
        """

        if 'shielded_instance_config' in conf.keys():
            self.evaluated_keys = ['shielded_instance_config', 'shielded_instance_config/[0]/enable_vtpm',
                                   'shielded_instance_config/[0]/enable_integrity_monitoring']
            if 'enable_vtpm' in conf['shielded_instance_config'][0] and \
                    not conf['shielded_instance_config'][0]['enable_vtpm'][0]:
                self.evaluated_keys = ['shielded_instance_config/[0]/enable_vtpm']
                return CheckResult.FAILED
            if 'enable_integrity_monitoring' in conf['shielded_instance_config'][0] and \
                    not conf['shielded_instance_config'][0]['enable_integrity_monitoring'][0]:
                self.evaluated_keys = ['shielded_instance_config/[0]/enable_integrity_monitoring']
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleComputeShieldedVM()
