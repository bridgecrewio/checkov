from typing import Dict, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class CleartextCredsOverUnencryptedChannel(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_3"
        name = "Ensure that security schemes don't allow cleartext credentials over unencrypted channel"
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_entities=["*"],
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        irrelevant_keys = ['__startline__', '__endline__']
        try:
            security_schemes = conf.get("components").get("securitySchemes")
            paths = conf.get('paths')
        except AttributeError:
            return CheckResult.SKIPPED

        for name, security_scheme in security_schemes.items():
            if name in irrelevant_keys:
                continue
            if security_scheme.get('type') == 'http':
                return CheckResult.FAILED
            elif security_scheme.get('scheme') == 'basic':
                return CheckResult.FAILED

        for key, path in paths.items():
            if key in irrelevant_keys:
                continue
            for operation in path:
                if not isinstance(operation, dict):
                    continue
                if operation.get('security'):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = CleartextCredsOverUnencryptedChannel()
