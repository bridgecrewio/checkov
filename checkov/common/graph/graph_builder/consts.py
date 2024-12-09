from enum import Enum


SELF_REFERENCE = "__self__"


class GraphSource(str, Enum):
    ANSIBLE = "Ansible"
    ARM = "ARM"
    BICEP = "Bicep"
    CLOUDFORMATION = "CloudFormation"
    DOCKERFILE = "Dockerfile"
    GITHUB_ACTIONS = "GitHubActions"
    KUBERNETES = "Kubernetes"
    TERRAFORM = "Terraform"
    TERRAFORM_PLAN = "terraform_plan"
    KUSTOMIZE = "kustomize"
    GITHUB_ACTION = "github_actions"
    HELM = "helm"
    SERVERLESS = "serverless"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value
