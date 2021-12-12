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
        if 'data_catalog_encryption_settings' not in conf:
            return CheckResult.FAILED

        data_conf = conf['data_catalog_encryption_settings'][0]
        connection_encrypted = False
        encrypted_at_rest = False
        if 'encryption_at_rest' in data_conf:
            enc_res = data_conf['encryption_at_rest'][0]
            if 'catalog_encryption_mode' in enc_res and 'sse_aws_kms_key_id' in enc_res \
                    and enc_res['catalog_encryption_mode'][0] == "SSE-KMS":
                encrypted_at_rest = True
                self.evaluated_keys = [
                    'data_catalog_encryption_settings/[0]/encryption_at_rest/[0]/catalog_encryption_mode',
                    'data_catalog_encryption_settings/[0]/encryption_at_rest/[0]/sse_aws_kms_key_id']
            else:
                self.evaluated_keys = ['data_catalog_encryption_settings/[0]/encryption_at_rest']

        if 'connection_password_encryption' in data_conf:
            con_res = data_conf['connection_password_encryption'][0]
            if 'return_connection_password_encrypted' in con_res and 'aws_kms_key_id' in con_res \
                    and con_res['return_connection_password_encrypted'][0] is True:
                connection_encrypted = True
                self.evaluated_keys.append('data_catalog_encryption_settings/[0]/connection_password_encryption/[0]/'
                                           'return_connection_password_encrypted')
                self.evaluated_keys.append('data_catalog_encryption_settings/[0]/connection_password_encryption/[0]/'
                                           'aws_kms_key_id')
            elif 'return_connection_password_encrypted' in con_res and 'aws_kms_key_id' in con_res \
                    and con_res['return_connection_password_encrypted'][0] is False:
                # handle the case when the attribute is explicitly set to false
                self.evaluated_keys.append('data_catalog_encryption_settings/[0]/connection_password_encryption/[0]/'
                                           'return_connection_password_encrypted')
            else:
                self.evaluated_keys.append('data_catalog_encryption_settings/[0]/connection_password_encryption')

        if encrypted_at_rest and connection_encrypted:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GlueDataCatalogEncryption()
