from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleStorageBucketEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Google storage bucket have encryption enabled"
        id = "CKV_GCP_5"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/azure/r/instance.html
        :param conf: azure_instance configuration
        :return: <CheckResult>
        """
        if 'encryption' in conf.keys():
            if len(conf['encryption'])>0:
                encryption_conf = conf['encryption'][0]
                if 'default_kms_key_name'  in encryption_conf.keys():
                    if encryption_conf['default_kms_key_name']:
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleStorageBucketEncryption()
