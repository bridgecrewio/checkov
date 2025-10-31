from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3GlobalViewACL(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AWS S3 bucket does not have global view ACL permissions enabled"
        id = "CKV_AWS_375"
        supported_resource = ("aws_s3_bucket_acl",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if 'access_control_policy' in conf:
            for policy_idx, policy in enumerate(conf["access_control_policy"]):
                if 'grant' in policy:
                    for grant_idx, grant in enumerate(policy["grant"]):
                        self.evaluated_keys = [f"access_control_policy/[{policy_idx}]/grant/[{grant_idx}]/permission"]
                        if (isinstance(grant, dict) and 'permission' in grant and
                                ('FULL_CONTROL' in grant.get('permission') or 'READ_ACP' in grant.get('permission'))):
                            if 'grantee' in grant:
                                for grantee in grant.get('grantee'):
                                    if 'uri' in grantee and 'http://acs.amazonaws.com/groups/global/AllUsers' in grantee.get('uri'):
                                        return CheckResult.FAILED

        return CheckResult.PASSED


check = S3GlobalViewACL()
