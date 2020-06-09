#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.cloudformation.checks.resource.registry import resource_registry as cfn_registry
from checkov.kubernetes.registry import registry as k8_registry


def print_checks(framework="all"):
    printable_checks_list = get_checks(framework)
    print(
        tabulate(printable_checks_list, headers=["Id", "Type", "Entity", "Policy", "IaC"], tablefmt="github",
                 showindex=True))
    print("\n\n---\n\n")


def get_checks(framework="all"):
    printable_checks_list = []
    if framework == "terraform" or framework == "all":
        for key in resource_registry.checks.keys():
            for check in resource_registry.checks[key]:
                printable_checks_list.append([check.id, "resource", key, check.name, "Terraform"])
        for key in data_registry.checks.keys():
            for check in data_registry.checks[key]:
                printable_checks_list.append([check.id, "data", key, check.name, "Terraform"])
        for key in provider_registry.checks.keys():
            for check in provider_registry.checks[key]:
                printable_checks_list.append([check.id, "provider", key, check.name, "Terraform"])
    if framework == "cloudformation" or framework == "all":
        for key in cfn_registry.checks.keys():
            for check in cfn_registry.checks[key]:
                printable_checks_list.append([check.id, "resource", key, check.name, "Cloudformation"])
    if framework == "kubernetes" or framework == "all":
        for key in k8_registry.checks.keys():
            for check in k8_registry.checks[key]:
                printable_checks_list.append([check.id, "PodSecurityPolicy", key, check.name, "Kubernetes"])
    return sorted(printable_checks_list, key=lambda x: x[0])

if __name__ == '__main__':
    print_checks()
