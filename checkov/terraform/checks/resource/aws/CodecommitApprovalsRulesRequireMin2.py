from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CodecommitApprovalsRulesRequireMin2(BaseResourceCheck):

    def __init__(self):
        """
        See https://docs.aws.amazon.com/codecommit/latest/userguide/approval-rule-templates.html
        """
        name = "Ensure CodeCommit branch changes have at least 2 approvals"
        id = "CKV_AWS_257"
        supported_resources = ['aws_codecommit_approval_rule_template']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("content") and isinstance(conf.get("content"), list):
            content = conf.get("content")[0]
            if not isinstance(content, dict):
                return CheckResult.UNKNOWN
            if content.get("Statements") and isinstance(content.get("Statements"), list):
                statement = content.get("Statements")[0]
                if isinstance(statement.get('NumberOfApprovalsNeeded'), int) and statement.get('NumberOfApprovalsNeeded') >= 2:
                    return CheckResult.PASSED
                self.evaluated_keys = ["content/Statements/NumberOfApprovalsNeeded"]
        return CheckResult.FAILED


check = CodecommitApprovalsRulesRequireMin2()
