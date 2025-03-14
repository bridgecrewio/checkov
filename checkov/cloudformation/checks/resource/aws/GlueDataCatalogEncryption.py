from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class GlueDataCatalogEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Glue Data Catalog Encryption is enabled"
        id = "CKV_AWS_94"
        supported_resources = ['AWS::Glue::DataCatalogEncryptionSettings']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        connection_encrypted = False
        encrypted_at_rest = False
        if 'Properties' in conf.keys():
            self.evaluated_keys = ['Properties']
            if 'DataCatalogEncryptionSettings' in conf['Properties'].keys():
                self.evaluated_keys = ['Properties/DataCatalogEncryptionSettings']
                dc_enc_settings = conf['Properties']['DataCatalogEncryptionSettings']
                if 'ConnectionPasswordEncryption' in dc_enc_settings.keys():
                    con_pass_enc = dc_enc_settings['ConnectionPasswordEncryption']
                    if 'ReturnConnectionPasswordEncrypted' in con_pass_enc.keys():
                        if con_pass_enc['ReturnConnectionPasswordEncrypted'] is True:
                            connection_encrypted = True

                if 'EncryptionAtRest' in dc_enc_settings.keys():
                    enc_at_rest = dc_enc_settings['EncryptionAtRest']
                    if 'CatalogEncryptionMode' in enc_at_rest.keys():
                        if enc_at_rest['CatalogEncryptionMode'] == "SSE-KMS":
                            encrypted_at_rest = True

        if connection_encrypted and encrypted_at_rest:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = GlueDataCatalogEncryption()
