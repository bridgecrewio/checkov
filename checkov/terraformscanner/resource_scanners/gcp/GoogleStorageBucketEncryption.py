from checkov.terraformscanner.models.enums import ScanResult, ScanCategories
from checkov.terraformscanner.resource_scanner import ResourceScanner


class GoogleStorageBucketEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure Google storage bucket have encryption enabled"
        scan_id = "BC_GCP_BUCKET_1"
        supported_resources = ['google_storage_bucket']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/azure/r/instance.html
        :param conf: azure_instance configuration
        :return: <ScanResult>
        """
        if 'encryption' in conf.keys():
            if len(conf['encryption'])>0:
                encryption_conf = conf['encryption'][0]
                if 'default_kms_key_name'  in encryption_conf.keys():
                    if encryption_conf['default_kms_key_name']:
                        return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = GoogleStorageBucketEncryption()
