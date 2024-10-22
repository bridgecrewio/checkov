from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list


class GlueSecurityConfiguration(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Glue Security Configuration Encryption is enabled"
        id = "CKV_AWS_99"
        supported_resources = ('AWS::Glue::SecurityConfiguration',)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        s3_enc = False
        cw_enc = False
        book_enc = False
        if 'Properties' in conf.keys():
            if 'EncryptionConfiguration' in conf['Properties'].keys():
                enc_conf = conf['Properties']['EncryptionConfiguration']

                if 'CloudWatchEncryption' in enc_conf.keys():
                    if 'CloudWatchEncryptionMode' in enc_conf['CloudWatchEncryption'].keys():
                        if enc_conf['CloudWatchEncryption']['CloudWatchEncryptionMode'] != 'DISABLED':
                            cw_enc = True

                if 'JobBookmarksEncryption' in enc_conf.keys():
                    if 'JobBookmarksEncryptionMode' in enc_conf['JobBookmarksEncryption'].keys():
                        if enc_conf['JobBookmarksEncryption']['JobBookmarksEncryptionMode'] != 'DISABLED':
                            book_enc = True

                if 'S3Encryptions' in enc_conf.keys():
                    for s3_encryption in force_list(enc_conf['S3Encryptions']):
                        if 'S3EncryptionMode' in s3_encryption.keys():
                            if s3_encryption['S3EncryptionMode'] != 'DISABLED':
                                s3_enc = True
                                break

        if s3_enc and cw_enc and book_enc:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = GlueSecurityConfiguration()
