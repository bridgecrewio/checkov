from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class CodeBuildProjectEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that CodeBuild Project encryption is not disabled"
        id = "CKV_AWS_78"
        supported_resources = ['AWS::CodeBuild::Project']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Only Fail if Artifact Type is S3 and EncryptionDisabled is True.
        artifact_type = ""
        encryption_disabled = False
        if 'Properties' in conf.keys():
            if 'Artifacts' in conf['Properties'].keys():
                if 'Type' in conf['Properties']['Artifacts'].keys():
                    artifact_type = conf['Properties']['Artifacts']['Type']
                if 'EncryptionDisabled' in conf['Properties']['Artifacts'].keys(): 
                    encryption_disabled = conf['Properties']['Artifacts']['EncryptionDisabled']
                if artifact_type == "S3" and encryption_disabled is True:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = CodeBuildProjectEncryption()
