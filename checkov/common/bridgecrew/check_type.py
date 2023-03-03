from dataclasses import dataclass


@dataclass
class CheckType:
    ANSIBLE = "ansible"
    ARGO_WORKFLOWS = "argo_workflows"
    ARM = "arm"
    AZURE_PIPELINES = "azure_pipelines"
    BICEP = "bicep"
    BITBUCKET_PIPELINES = "bitbucket_pipelines"
    CIRCLECI_PIPELINES = "circleci_pipelines"
    CLOUDFORMATION = "cloudformation"
    DOCKERFILE = "dockerfile"
    GITHUB_CONFIGURATION = "github_configuration"
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CONFIGURATION = "gitlab_configuration"
    GITLAB_CI = "gitlab_ci"
    BITBUCKET_CONFIGURATION = "bitbucket_configuration"
    HELM = "helm"
    JSON = "json"
    YAML = "yaml"
    KUBERNETES = "kubernetes"
    KUSTOMIZE = "kustomize"
    OPENAPI = "openapi"
    SCA_PACKAGE = "sca_package"
    SCA_IMAGE = "sca_image"
    SECRETS = "secrets"
    SERVERLESS = "serverless"
    TERRAFORM = "terraform"
    TERRAFORM_PLAN = "terraform_plan"
    POLICY_3D = "3d_policy"


# needs to be at the end
checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]
