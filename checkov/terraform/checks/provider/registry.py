from checkov.common.bridgecrew.check_type import CheckType
from checkov.terraform.checks.provider.base_registry import Registry
from checkov.terraform.checks.provider.plan_registry import Registry as PlanRegistry

provider_registry = Registry(CheckType.TERRAFORM)
plan_provider_registry = PlanRegistry(CheckType.TERRAFORM_PLAN)
