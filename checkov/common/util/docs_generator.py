#!/usr/bin/env python

from tabulate import tabulate

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.cloudformation.checks.resource.registry import cfn_registry as cfn_registry
from checkov.kubernetes.registry import registry as k8_registry
from checkov.serverless.registry import sls_registry
from checkov.arm.registry import arm_registry


def print_checks(framework="all"):
    printable_checks_list = get_checks(framework)
    print(
        tabulate(printable_checks_list, headers=["Id", "Type", "Entity", "Policy", "IaC"], tablefmt="github",
                 showindex=True))
    print("\n\n---\n\n")


def get_checks(framework="all"):
    printable_checks_list = []

    def add_from_repository(registry: BaseCheckRegistry, checked_type: str, iac: str):
        nonlocal printable_checks_list
        for entity, check in registry.all_checks():
            printable_checks_list.append([check.id, checked_type, entity, check.name, iac])

    if framework == "terraform" or framework == "all":
        add_from_repository(resource_registry, "resource", "Terraform")
        add_from_repository(data_registry, "data", "Terraform")
        add_from_repository(provider_registry, "provider", "Terraform")
        # TODO add also module_registry
    if framework == "cloudformation" or framework == "all":
        add_from_repository(cfn_registry, "resource", "Cloudformation")
    if framework == "kubernetes" or framework == "all":
        add_from_repository(k8_registry, "PodSecurityPolicy", "Kubernetes")
    if framework == "serverless" or framework == "all":
        add_from_repository(sls_registry, "resource", "serverless")
    if framework == "arm" or framework == "all":
        add_from_repository(arm_registry, "resource", "arm")
    return sorted(printable_checks_list, key=lambda x: x[0])


if __name__ == '__main__':
    print_checks()
