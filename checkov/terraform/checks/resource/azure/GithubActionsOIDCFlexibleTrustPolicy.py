from __future__ import annotations

import re
from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

GITHUB_ISSUER = "https://token.actions.githubusercontent.com"
# One clause of the flexible FIC expression language: claims['<name>'] <operator> '<comparand>'
CLAIM_CLAUSE = re.compile(r"claims\['([^']+)'\]\s+(eq|matches)\s+'[^']*'")
IMMUTABLE_CLAIMS = ("repository_id", "repository_owner_id")


class GithubActionsOIDCFlexibleTrustPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        """
        Microsoft Entra requires a GitHub flexible federated identity credential to match the `sub` claim
        and at least one immutable claim, `repository_id` or `repository_owner_id`, which only support `eq`.
        Entra rejects other expressions when the credential is created.
        https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-flexible-federated-identity-credentials
        """
        name = "Ensure Azure GitHub Actions OIDC flexible federated identity credential matches sub and an immutable repository claim"
        id = "CKV_AZURE_252"
        supported_resources = ("azuread_application_flexible_federated_identity_credential",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        issuer = conf.get("issuer", [""])[0]
        expression = conf.get("claims_matching_expression", [""])[0]
        if not isinstance(issuer, str) or not isinstance(expression, str) or "${" in issuer + expression:
            # unresolved variables, nothing reliable to evaluate
            return CheckResult.UNKNOWN
        if issuer.rstrip("/") != GITHUB_ISSUER:
            return CheckResult.PASSED

        operators: dict[str, set[str]] = {}
        for claim, operator in CLAIM_CLAUSE.findall(expression):
            operators.setdefault(claim, set()).add(operator)

        has_sub = "sub" in operators
        has_immutable_claim = any("eq" in operators.get(claim, ()) for claim in IMMUTABLE_CLAIMS)
        uses_unsupported_operator = any(operators.get(claim, set()) - {"eq"} for claim in IMMUTABLE_CLAIMS)
        if has_sub and has_immutable_claim and not uses_unsupported_operator:
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["issuer", "claims_matching_expression"]


check = GithubActionsOIDCFlexibleTrustPolicy()
