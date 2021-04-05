import json
import logging
from abc import abstractmethod
from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.multi_signature import multi_signature
from checkov.terraform.checks.utils.iam_cloudformation_document_to_policy_converter import \
    convert_cloudformation_conf_to_iam_policy


class BaseCloudsplainingIAMCheck(BaseResourceCheck):
    def __init__(self, name, id):
        super().__init__(name=name, id=id, categories=CheckCategories.IAM, supported_resources=["AWS::IAM::Policy", "AWS::IAM::ManagedPolicy"])

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            props_conf = conf['Properties']
            key = 'PolicyDocument'
            if key in props_conf.keys():
                converted_conf = props_conf[key]
                try:
                    converted_conf = convert_cloudformation_conf_to_iam_policy(converted_conf)
                    key = 'Statement'
                    if key in converted_conf:
                        policy = PolicyDocument(converted_conf)
                        violations = self.cloudsplaining_analysis(policy)
                        if violations:
                            logging.debug("detailed cloudsplainging finding: {}",json.dumps(violations))
                            return CheckResult.FAILED
                except Exception as e:
                    # this might occur with templated iam policies where ARN is not in place or similar
                    logging.debug("could not run cloudsplaining analysis on policy {}", conf)
                    return CheckResult.UNKNOWN
        return CheckResult.PASSED

    @multi_signature()
    @abstractmethod
    def cloudsplaining_analysis(self, policy):
        raise NotImplementedError()
