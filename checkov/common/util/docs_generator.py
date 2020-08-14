#!/usr/bin/env python
from functools import cmp_to_key

from tabulate import tabulate

from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.cloudformation.checks.resource.registry import cfn_registry as cfn_registry
from checkov.kubernetes.registry import registry as k8_registry
from checkov.serverless.registry import sls_registry
from checkov.arm.registry import arm_registry


def check_compare(c1, c2):
    c1: str = c1[0]
    c2: str = c2[0]

    c1_index = c1.rindex('_')
    c2_index = c2.rindex('_')

    c1_prefix = c1[0:c1_index]
    c1_number = int(c1[c1_index + 1:])

    c2_prefix = c2[0:c2_index]
    c2_number = int(c2[c2_index + 1:])

    if c1_prefix == c2_prefix:
        return c1_number - c2_number
    else:
        return -1 if c1 < c2 else 1


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
    if framework == "serverless" or framework == "all":
        for key in sls_registry.checks.keys():
            for check in sls_registry.checks[key]:
                printable_checks_list.append([check.id, "resource", key, check.name, "serverless"])
    if framework == "arm" or framework == "all":
        for key in arm_registry.checks.keys():
            for check in arm_registry.checks[key]:
                printable_checks_list.append([check.id, "resource", key, check.name, "arm"])
    return sorted(printable_checks_list, key=cmp_to_key(check_compare))

if __name__ == '__main__':
    print_checks()
