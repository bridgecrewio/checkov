from __future__ import annotations
from typing import Any, Dict
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class APIGatewayMethodWOAuth(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure API gateway method has authorization or API key set"
        id = "CKV2_AWS_70"
        supported_resources = ('aws_api_gateway_method',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def _is_policy_secure(self, policy: Dict[str, Any]) -> CheckResult:
        # Check that the policy doesn't allow for all principals to us action execute-api:Invoke
        passed = True
        if policy.get("Statement"):
            for p in policy.get("Statement"):
                # Pass if there is any Deny for execute-api:Invoke
                if p.get("Effect") == "Deny" and p.get("Principal") == "*":
                    if (isinstance(p.get("Action"), str) and p.get("Action") in ["execute-api:Invoke", "execute-api:*",
                                                                                 "*"]) or \
                            (isinstance(p.get("Action"), list) and
                             any(action in ["execute-api:Invoke", "execute-api:*", "*"] for action in p.get("Action"))):
                        return CheckResult.PASSED
                # Fail if there is an Allow for execute-api:Invoke without a Deny or Conditions
                if p.get("Effect") == "Allow" and p.get("Principal") == "*" and "Condition" not in p:
                    if (isinstance(p.get("Action"), str) and p.get("Action") in ["execute-api:Invoke",
                                                                                 "execute-api:*", "*"]) or \
                            (isinstance(p.get("Action"), list) and
                             any(action in ["execute-api:Invoke", "execute-api:*", "*"] for action in p.get("Action"))):
                        passed = False
            if passed:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        elif policy.get("statement"):
            policy_statement = policy.get("statement")
            if isinstance(policy_statement, dict):
                policy_statement = [policy_statement]
            for p in policy_statement:
                # Pass if there is any Deny for execute-api:Invoke
                if p.get("effect") and p.get("effect") == "Deny" and p.get("principals").get("identifiers") and \
                        p.get("principals").get("identifiers") == ["*"]:
                    if (isinstance(p.get("actions"), str) and p.get("actions") in
                        ["execute-api:Invoke", "execute-api:*", "*"]) or \
                        (isinstance(p.get("actions"), list) and
                         any(action in ["execute-api:Invoke", "execute-api:*", "*"] for action in p.get("actions"))):
                        return CheckResult.PASSED
                # Fail if there is an Allow for execute-api:Invoke without a Deny or Conditions
                if p.get("effect") and p.get("effect") == "Allow" and p.get("principals").get("identifiers") and \
                        p.get("principals").get("identifiers") == ['*'] and "condition" not in p:
                    if (isinstance(p.get("actions"), str) and p.get("actions") in ["execute-api:Invoke",
                                                                                   "execute-api:*", "*"]) or \
                            (isinstance(p.get("actions"), list) and
                             any(action in ["execute-api:Invoke", "execute-api:*", "*"] for action in p.get("actions"))):
                        passed = False
            if passed:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        return CheckResult.UNKNOWN

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Pass if authorization is not NONE or if api_key_required = true (explicitly) or if http_method is anything
        # other than OPTIONS
        if conf.get("authorization", [None])[0] != 'NONE' or \
                conf.get("api_key_required", [False])[0] or \
                conf.get("http_method", [None])[0] != "OPTIONS":
            return CheckResult.PASSED

        # Find connected `aws_api_gateway_rest_api` resources
        rest_api_id = conf.get("rest_api_id")[0].rsplit('.', 1)[0]
        connected_rest_api_nodes = [g for g in self.graph.nodes() if g[1].get(CustomAttributes.ID) == rest_api_id]
        if connected_rest_api_nodes:
            connected_rest_api = connected_rest_api_nodes[0][1]
            # If only PRIVATE (only private not ["EDGE","PRIVATE"] as an example)
            if "endpoint_configuration" in connected_rest_api and \
                    "types" in connected_rest_api.get("endpoint_configuration") and \
                    connected_rest_api.get("endpoint_configuration").get("types") == ["PRIVATE"]:
                return CheckResult.PASSED
            elif "policy" in connected_rest_api:
                return self._is_policy_secure(connected_rest_api.get("policy"))
            else:
                # Check for connected `aws_api_gateway_rest_api_policy`
                # If so, check that it follows the rules above
                connected_rest_api_policy_nodes = [
                    g2 for g2 in self.graph.nodes()
                    if g2[1].get(CustomAttributes.RESOURCE_TYPE) == "aws_api_gateway_rest_api_policy" and
                    g2[1].get("rest_api_id").rsplit('.', 1)[0] == rest_api_id
                ]

                if connected_rest_api_policy_nodes:
                    policy_statement = connected_rest_api_policy_nodes[0][1].get("policy")
                    if isinstance(policy_statement, dict):
                        return self._is_policy_secure(policy_statement)
                    elif isinstance(policy_statement, str) and policy_statement.split('.')[0] == 'data' and \
                            policy_statement.split('.')[-1] == 'json':
                        target_id = '.'.join(policy_statement.split('.')[1:-1])
                        connected_iam_policy_doc = [
                            g3 for g3 in self.graph.nodes()
                            if g3[1].get(CustomAttributes.BLOCK_TYPE) == "data" and
                            g3[1].get(CustomAttributes.ID) == target_id
                        ]

                        if connected_iam_policy_doc[0][1].get("statement"):
                            return self._is_policy_secure(connected_iam_policy_doc[0][1])
                else:
                    return CheckResult.UNKNOWN
            return CheckResult.UNKNOWN

        # If there is no connected `aws_api_gateway_rest_api` then return UNKNOWN
        return CheckResult.UNKNOWN


check = APIGatewayMethodWOAuth()
