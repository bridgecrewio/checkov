from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class AzureManagedDiscEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure Azure managed disk have encryption enabled"
        scan_id = "BC_AZURE_DISC_1"
        supported_resources = ['azurerm_managed_disk']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/azure/r/instance.html
        :param conf: azure_instance configuration
        :return: <ScanResult>
        """
        if 'encryption_settings' in conf.keys():
            config = conf['encryption_settings'][0]
            if config['enabled'] ==[False]:
                return ScanResult.FAILURE
        return ScanResult.SUCCESS


scanner = AzureManagedDiscEncryption()
