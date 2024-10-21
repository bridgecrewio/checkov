from __future__ import annotations
import json
from typing import Any, Dict

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.graph.graph_builder import CustomAttributes


class S3SecureDataTransport(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AWS S3 bucket is configured with secure data transport policy"
        id = "CKV_AWS_379"
        supported_resources = ('aws_s3_bucket_acl',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def _is_policy_secure(self, policy: Dict[str, Any]) -> CheckResult:
        # Explicitly deny aws:SecureTransport = false or allow aws:SecureTransport = true
        if policy.get("Statement"):
            for p in policy.get("Statement"):
                if p.get("Effect") == "Allow":
                    condition = p.get("Condition")
                    if (condition and condition.get("Bool") and
                            'aws:SecureTransport' in condition.get("Bool") and
                            condition.get("Bool").get("aws:SecureTransport").lower() == "true"):
                        return CheckResult.PASSED
                elif p.get("Effect") == "Deny":
                    condition = p.get("Condition")
                    if (condition and condition.get("Bool") and
                            'aws:SecureTransport' in condition.get("Bool") and
                            (not condition.get("Bool").get("aws:SecureTransport") or
                             condition.get("Bool").get("aws:SecureTransport").lower() == "false")):
                        return CheckResult.PASSED
        elif policy.get("statement"):
            policy_statement = policy.get("statement")
            if isinstance(policy_statement, dict):
                policy_statement = [policy_statement]
            for p in policy_statement:
                # Pass if aws:SecureTransport exists
                if ((not p.get("effect") or p.get("effect") == "Allow") and p.get("condition") and
                        p.get("condition").get("test") and p.get("condition").get("test") == "Bool" and
                        p.get("condition").get("variable") and
                        p.get("condition").get("variable") == "aws:SecureTransport" and
                        p.get("condition").get("values") and p.get("condition").get("values")[0]):
                    return CheckResult.PASSED
                elif ((not p.get("effect") or p.get("effect") == "Deny") and p.get("condition") and
                        p.get("condition").get("test") and p.get("condition").get("test") == "Bool" and
                        p.get("condition").get("variable") and
                        p.get("condition").get("variable") == "aws:SecureTransport" and
                        p.get("condition").get("values") and not p.get("condition").get("values")[0]):
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def scan_resource_conf(self, conf) -> CheckResult:
        acl = conf.get('acl')
        is_public = False
        connected_public_access_block = []
        if acl and acl[0] in ('public-read', 'public-read-write'):
            # Search for a connected aws_s3_bucket then a connected aws_s3_bucket_public_access_block then check if
            # restrict_public_buckets is true and pass or else fail
            bucket_id = conf.get("bucket")[0].rsplit('.', 1)[0]
            connected_public_access_block = [
                g for g in self.graph.nodes()
                if g[1].get(CustomAttributes.RESOURCE_TYPE) == "aws_s3_bucket_public_access_block"
                and isinstance(g[1].get("bucket"), str)
                and g[1].get("bucket").rsplit('.', 1)[0] == bucket_id
            ]
            if connected_public_access_block:
                if (not connected_public_access_block[0][1].get('restrict_public_buckets') and
                        not connected_public_access_block[0][1].get('block_public_acls')):
                    is_public = True
            else:
                is_public = True

        access_control_policy = conf.get('access_control_policy')
        if not is_public and access_control_policy:
            grants = access_control_policy[0].get('grant', [])
            for grant in grants:
                grantee = grant.get('grantee', [])
                if grantee and grantee[0].get('uri', [None])[0] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    # Search for a connected aws_s3_bucket then a connected aws_s3_bucket_public_access_block then
                    # check if block_public_acls is true and pass or else fail
                    bucket_id = conf.get("bucket")[0].rsplit('.', 1)[0]
                    # Don't look again if already collected
                    if not connected_public_access_block:
                        connected_public_access_block = [
                            g for g in self.graph.nodes()
                            if g[1].get(CustomAttributes.RESOURCE_TYPE) == "aws_s3_bucket_public_access_block"
                            and isinstance(g[1].get("bucket"), str)
                            and g[1].get("bucket").rsplit('.', 1)[0] == bucket_id
                        ]
                    if connected_public_access_block:
                        if not connected_public_access_block[0][1].get('block_public_acls'):
                            is_public = True
                    else:
                        is_public = True

        if not is_public:
            return CheckResult.PASSED

        # if connected to aws_s3_bucket_website_configuration then pass
        bucket_id = conf.get("bucket")[0].rsplit('.', 1)[0]
        connected_website = [
            g for g in self.graph.nodes()
            if g[1].get(CustomAttributes.RESOURCE_TYPE) == "aws_s3_bucket_website_configuration"
            and isinstance(g[1].get("bucket"), str)
            and g[1].get("bucket").rsplit('.', 1)[0] == bucket_id
        ]
        if connected_website:
            return CheckResult.PASSED

        # Ensures the aws:SecureTransport condition does not exist in any policy statement.
        connected_s3_bucket_policy = [
            g for g in self.graph.nodes()
            if g[1].get(CustomAttributes.RESOURCE_TYPE) == "aws_s3_bucket_policy"
            and isinstance(g[1].get("bucket"), str)
            and g[1].get("bucket").rsplit('.', 1)[0] == bucket_id
        ]

        if connected_s3_bucket_policy:
            policy_statement = connected_s3_bucket_policy[0][1].get("policy")
            if isinstance(policy_statement, dict):
                return self._is_policy_secure(policy_statement)
            elif isinstance(policy_statement, str) and policy_statement.strip().startswith('jsonencode'):
                json_content = policy_statement.replace("jsonencode(", "").replace(")", "")
                json_content = json_content.replace("'", '"')
                json_content = json_content.replace('""', '"')
                try:
                    policy_statement = json.loads(json_content)
                except json.JSONDecodeError:
                    # Error decoding JSON
                    return CheckResult.UNKNOWN
                return self._is_policy_secure(policy_statement)
            elif (isinstance(policy_statement, str) and policy_statement.split('.')[0] == 'data' and
                  policy_statement.split('.')[-1] == 'json'):
                target_id = '.'.join(policy_statement.split('.')[1:-1])
                connected_iam_policy_doc = [
                    g2 for g2 in self.graph.nodes()
                    if g2[1].get(CustomAttributes.BLOCK_TYPE) == "data"
                    and g2[1].get(CustomAttributes.ID) == target_id
                ]

                if connected_iam_policy_doc[0][1].get("statement"):
                    return self._is_policy_secure(connected_iam_policy_doc[0][1])

        return CheckResult.UNKNOWN


check = S3SecureDataTransport()
