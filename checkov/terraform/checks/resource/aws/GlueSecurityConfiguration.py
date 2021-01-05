from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class GlueSecurityConfiguration(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Glue Security Configuration Encryption is enabled"
        id = "CKV_AWS_99"
        supported_resources = ['aws_glue_security_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'encryption_configuration' in conf:
            data_conf = conf['encryption_configuration'][0]
            cloudwatch_encrypted = False
            job_bookmarks_encrypted = False
            s3_encrypted = False
            if 'cloudwatch_encryption' in data_conf:
                enc_res = data_conf['cloudwatch_encryption'][0]
                if 'cloudwatch_encryption_mode' in enc_res and 'kms_key_arn' in enc_res:
                    if enc_res['cloudwatch_encryption_mode'][0] == "SSE-KMS":
                        cloudwatch_encrypted = True

            if 'job_bookmarks_encryption' in data_conf:
                enc_res = data_conf['job_bookmarks_encryption'][0]
                if 'job_bookmarks_encryption_mode' in enc_res and 'kms_key_arn' in enc_res:
                    if enc_res['job_bookmarks_encryption_mode'][0] == "CSE-KMS":
                        job_bookmarks_encrypted = True

            if 's3_encryption' in data_conf:
                enc_res = data_conf['s3_encryption'][0]
                if 's3_encryption_mode' in enc_res:
                    if enc_res['s3_encryption_mode'][0] != "DISABLED":
                        s3_encrypted = True                        

            if cloudwatch_encrypted and job_bookmarks_encrypted and s3_encrypted:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GlueSecurityConfiguration()
