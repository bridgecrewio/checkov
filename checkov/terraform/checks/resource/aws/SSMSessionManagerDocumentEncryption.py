import json

import yaml

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import is_json, is_yaml
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class SSMSessionManagerDocumentEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Session Manager data is encrypted in transit"
        id = "CKV_AWS_112"
        supported_resources = ["aws_ssm_document"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("document_type") != ["Session"] or "content" not in conf.keys():
            return CheckResult.UNKNOWN

        doc_format = conf.get("document_format", ["JSON"])
        content = conf["content"][0]
        inputs = None

        if doc_format == ["JSON"] and is_json(content):
            inputs = json.loads(content).get("inputs", {})
        elif doc_format == ["YAML"] and is_yaml(content):
            inputs = yaml.safe_load(content).get("inputs", {})
        elif isinstance(content, dict):
            inputs = content.get("inputs", None)

        if inputs and not inputs.get("kmsKeyId"):
            return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['document_type', 'document_format', 'content']


check = SSMSessionManagerDocumentEncryption()
