import json
from pathlib import Path

import parliament
from checkov.common.models.enums import (
    CheckCategories,
    CheckResult,
)
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from parliament.cli import is_finding_filtered


class ParliamentProblem(BaseResourceCheck):

    def __init__(self):
        name = "duo-labs/parliament issue(s) found"
        self.base_name = "duo-labs/parliament issue(s) found"
        id = "CKV_AWS_96"
        categories = [CheckCategories.IAM]
        supported_resources = ['aws_iam_policy']
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        """
        TODO

        :param conf: dict of supported resource configuration
        :return: <CheckResult>
        """
        # We change the name only if we find issues
        self.name = self.base_name

        policy_string = conf['policy'][0].strip()

        try:
            json.loads(policy_string)
        except ValueError:
            return CheckResult.PASSED

        enhanced_filtered_findings = [
            enhanced_finding
            for enhanced_finding in map(
                parliament.enhance_finding,
                parliament.analyze_policy_string(
                    policy_string,
                    include_community_auditors=True,
                    config=parliament.config,
                ).findings,
            )
            if not is_finding_filtered(
                enhanced_finding,
                minimum_severity="MEDIUM",
            )
        ]
        if enhanced_filtered_findings:
            self.name = f"{self.name}\n" + "-\n".join(
                map(
                    str,
                    enhanced_filtered_findings,
                )
            )
            return CheckResult.FAILED
        return CheckResult.PASSED



def add_config_for_community_auditors():
    community_auditors_override_file = (
        Path(parliament.config_path).parent
        / "community_auditors"
        / "config_override.yaml"
    )
    # This adds to parliament.config
    parliament.override_config(community_auditors_override_file)


add_config_for_community_auditors()


check = ParliamentProblem()
