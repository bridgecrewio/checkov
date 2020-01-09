import json
import re

from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories

import parliament

# credit: https://github.com/rdkls/tf-parliament

field_mappings = [
    {'tf_key': 'effect', 'iam_key': 'Effect', 'mock_var': 'Allow'},
    {'tf_key': 'actions', 'iam_key': 'Action', 'mock_var': '*'},
    {'tf_key': 'not_actions', 'iam_key': 'NotAction', 'mock_var': '*'},
    {'tf_key': 'resources', 'iam_key': 'Resource', 'mock_var': '*'},
    {'tf_key': 'not_resources', 'iam_key': 'NotResource', 'mock_var': '*'},
]

policy_template = """{{
    "Version": "2012-10-17",
    "Id": "123",
    "Statement": {statements}
}}"""


class IAMParliamentFinding(BaseDataCheck):
    def __init__(self, finding):
        id = "CKV_AWS_28"
        categories = [CheckCategories.IAM]

        name = "Parliament:{}".format(str(finding))
        super().__init__(name=name, id=id, categories=categories, supported_data=[])

    def scan_data_conf(self, conf):
        pass


class IAMParliament(BaseDataCheck):
    def __init__(self):
        name = "Ensure AWS IAM policy is valid as defined at: https://github.com/duo-labs/parliament"
        id = "CKV_AWS_28"
        supported_data = ['aws_iam_policy_document']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf):
        statements = []
        for statement_data in conf['statement']:

            actions = statement_data.get('actions')[0]
            if actions == ['sts:AssumeRole'] or actions == ['sts:AssumeRoleWithSAML']:
                continue

            statement = {}

            for field in field_mappings:
                if statement_data.get(field['tf_key'], None):
                    field_values = statement_data.get(field['tf_key'])[0]

                    # If there are TF vars in the string e.g. "${var.xxx}"
                    # we replace these with "mock" vars for the field to pass validation
                    if list == type(field_values):
                        field_values = list(map(lambda x: re.sub('\${.*?}', field['mock_var'], x), field_values))
                    else:
                        field_values = re.sub('\${.*?}', field['mock_var'], field_values)

                    statement[field['iam_key']] = field_values

            statements.append(statement)

        policy_string = policy_template.format(statements=json.dumps(statements))
        analyzed_policy = parliament.analyze_policy_string(policy_string)

        if analyzed_policy.findings:
            results = []
            for finding in analyzed_policy.findings:
                # terraform statement element is optional - The default is "Allow".
                if finding.detail != "Statement does not contain an Effect element":
                    results.append(
                        IAMParliamentFinding(finding))
            if results:
                return CheckResult.FAILED, results
        return CheckResult.PASSED


check = IAMParliament()
