import json
import logging

import yaml

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SSMSessionManagerDocumentLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Session Manager logs are enabled and encrypted"
        id = "CKV_AWS_113"
        supported_resources = ["aws_ssm_document"]
        categories = [CheckCategories.ENCRYPTION, CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("document_type") == ["Session"]:
            doc_format = conf.get("document_format", ["JSON"])

            if "content" in conf.keys():
                content = conf["content"][0]
                inputs = None

                if doc_format == ["JSON"] and is_json(content):
                    inputs = json.loads(content).get("inputs", {})
                elif doc_format == ["YAML"] and is_yaml(content):
                    inputs = yaml.safe_load(content).get("inputs", {})

                if inputs:
                    if inputs.get("s3BucketName") and inputs.get("s3EncryptionEnabled"):
                        return CheckResult.PASSED
                    elif inputs.get("cloudWatchLogGroupName") and inputs.get("cloudWatchEncryptionEnabled"):
                        return CheckResult.PASSED

                    return CheckResult.FAILED

                return CheckResult.UNKNOWN

        return CheckResult.UNKNOWN


def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        logging.debug(f"could not parse json data: {data}")
        return False
    return True


def is_yaml(data):
    try:
        yaml.safe_load(data)
    except yaml.YAMLError:
        logging.debug(f"could not parse yaml data: {data}")
        return False
    return True


check = SSMSessionManagerDocumentLogging()
