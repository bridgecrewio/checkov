from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class GlueDataCatalogEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Glue Data Catalog Encryption is enabled"
        id = "CKV_AWS_94"
        supported_resources = ['aws_glue_data_catalog_encryption_settings']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'data_catalog_encryption_settings' in conf:
            data_conf = conf['data_catalog_encryption_settings'][0]
            connection_encrypted = False
            encrypted_at_rest = False
            if 'encryption_at_rest' in data_conf:
                enc_res = data_conf['encryption_at_rest'][0]
                if 'catalog_encryption_mode' in enc_res and 'sse_aws_kms_key_id' in enc_res:
                    if enc_res['catalog_encryption_mode'][0] == "SSE-KMS":
                        encrypted_at_rest = True

            if 'connection_password_encryption' in data_conf:
                con_res = data_conf['connection_password_encryption'][0]
                if 'return_connection_password_encrypted' in con_res and 'aws_kms_key_id' in con_res:
                    if con_res['return_connection_password_encrypted'][0] == True:
                        connection_encrypted = True

            if encrypted_at_rest and connection_encrypted:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GlueDataCatalogEncryption()
