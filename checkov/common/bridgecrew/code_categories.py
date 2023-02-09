from enum import Enum
from typing import Dict, List, Union

from checkov.common.bridgecrew.severities import Severity, BcSeverities, Severities
from checkov.common.bridgecrew.check_type import CheckType


class CodeCategoryType(str, Enum):
    IAC = "IAC"
    VULNERABILITIES = "VULNERABILITIES"
    SECRETS = "SECRETS"
    LICENSES = "LICENSES"
    BUILD_INTEGRITY = "BUILD_INTEGRITY"


CodeCategoryMapping: Dict[str, Union[CodeCategoryType, List[CodeCategoryType]]] = {
    CheckType.ANSIBLE: CodeCategoryType.IAC,
    CheckType.ARGO_WORKFLOWS: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.ARM: CodeCategoryType.IAC,
    CheckType.AZURE_PIPELINES: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.BICEP: CodeCategoryType.IAC,
    CheckType.BITBUCKET_PIPELINES: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.CIRCLECI_PIPELINES: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.CLOUDFORMATION: CodeCategoryType.IAC,
    CheckType.DOCKERFILE: CodeCategoryType.IAC,
    CheckType.GITHUB_CONFIGURATION: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.GITHUB_ACTIONS: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.GITLAB_CONFIGURATION: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.GITLAB_CI: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.BITBUCKET_CONFIGURATION: CodeCategoryType.BUILD_INTEGRITY,
    CheckType.HELM: CodeCategoryType.IAC,
    CheckType.JSON: CodeCategoryType.IAC,
    CheckType.YAML: CodeCategoryType.IAC,
    CheckType.KUBERNETES: CodeCategoryType.IAC,
    CheckType.KUSTOMIZE: CodeCategoryType.IAC,
    CheckType.OPENAPI: CodeCategoryType.IAC,
    CheckType.SCA_PACKAGE: [CodeCategoryType.LICENSES, CodeCategoryType.VULNERABILITIES],
    CheckType.SCA_IMAGE: [CodeCategoryType.LICENSES, CodeCategoryType.VULNERABILITIES],
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
