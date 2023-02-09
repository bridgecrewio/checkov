from dataclasses import dataclass

from checkov.common.bridgecrew.severities import Severity, BcSeverities, Severities
from checkov.common.bridgecrew.check_type import CheckType


@dataclass
class CodeCategoryType:
    IAC = "IAC"
    OPEN_SOURCE = "OPEN_SOURCE"
    SECRETS = "SECRETS"
    IMAGES = "IMAGES"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"


CodeCategoryMapping = {
    CheckType.ANSIBLE: CodeCategoryType.IAC,
    CheckType.ARGO_WORKFLOWS: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.ARM: CodeCategoryType.IAC,
    CheckType.AZURE_PIPELINES: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.BICEP: CodeCategoryType.IAC,
    CheckType.BITBUCKET_PIPELINES: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.CIRCLECI_PIPELINES: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.CLOUDFORMATION: CodeCategoryType.IAC,
    CheckType.DOCKERFILE: CodeCategoryType.IAC,
    CheckType.GITHUB_CONFIGURATION: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.GITHUB_ACTIONS: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.GITLAB_CONFIGURATION: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.GITLAB_CI: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.BITBUCKET_CONFIGURATION: CodeCategoryType.SUPPLY_CHAIN,
    CheckType.HELM: CodeCategoryType.IAC,
    CheckType.JSON: CodeCategoryType.IAC,
    CheckType.YAML: CodeCategoryType.IAC,
    CheckType.KUBERNETES: CodeCategoryType.IAC,
    CheckType.KUSTOMIZE: CodeCategoryType.IAC,
    CheckType.OPENAPI: CodeCategoryType.IAC,
    CheckType.SCA_PACKAGE: CodeCategoryType.OPEN_SOURCE,
    CheckType.SCA_IMAGE: CodeCategoryType.IMAGES,
    CheckType.SECRETS: CodeCategoryType.SECRETS,
    CheckType.SERVERLESS: CodeCategoryType.IAC,
    CheckType.TERRAFORM: CodeCategoryType.IAC,
    CheckType.TERRAFORM_PLAN: CodeCategoryType.IAC,
    CheckType.POLICY_3D: CodeCategoryType.IAC
}


class CodeCategoryConfiguration:
    def __init__(self, category: str, soft_fail_threshold: Severity, hard_fail_threshold: Severity):
        self.category = category
        self.soft_fail_threshold = soft_fail_threshold
        self.hard_fail_threshold = hard_fail_threshold

    def is_global_soft_fail(self) -> bool:
        return self.hard_fail_threshold == Severities[BcSeverities.OFF]
