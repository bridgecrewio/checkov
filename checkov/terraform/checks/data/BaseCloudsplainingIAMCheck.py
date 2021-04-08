import json
import logging
from abc import abstractmethod
from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.multi_signature import multi_signature
from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.terraform.checks.utils.iam_terraform_document_to_policy_converter import \
    convert_terraform_conf_to_iam_policy


class BaseCloudsplainingIAMCheck(BaseDataCheck):
    def __init__(self, name, id):
        super().__init__(name=name, id=id, categories=[CheckCategories.IAM], supported_data=['aws_iam_policy_document'])

    def scan_data_conf(self, conf):
        key = 'statement'
        if key in conf.keys():
            try:
                converted_conf = convert_terraform_conf_to_iam_policy(conf)
                policy = PolicyDocument(converted_conf)
                violations = self.cloudsplaining_analysis(policy)
            except Exception as e:
                # this might occur with templated iam policies where ARN is not in place or similar
                logging.debug("could not run cloudsplaining analysis on policy {}", conf)
                return CheckResult.UNKNOWN
            if violations:
                logging.debug("detailed cloudsplainging finding: {}", json.dumps(violations))
                return CheckResult.FAILED
        return CheckResult.PASSED

    @multi_signature()
    @abstractmethod
    def cloudsplaining_analysis(self, policy):
        raise NotImplementedError()
