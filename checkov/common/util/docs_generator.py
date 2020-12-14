#!/usr/bin/env python

import re

from tabulate import tabulate

from checkov.arm.registry import arm_registry
from checkov.cloudformation.checks.resource.registry import cfn_registry as cfn_registry
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.kubernetes.registry import registry as k8_registry
from checkov.serverless.registry import sls_registry
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry

ID_PARTS_PATTERN = re.compile(r'(\D*)(\d*)')


def get_compare_key(c):
    res = []
    for match in ID_PARTS_PATTERN.finditer(c[0]):
        text, number = match.groups()
        numeric_value = int(number) if number else 0
        # count number of leading zeros
        same_number_ordering = len(number) - len(number.lstrip('0'))
        res.append((text, numeric_value, same_number_ordering))
    return res


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
        add_from_repository(module_registry, "module", "Terraform")
    if framework == "cloudformation" or framework == "all":
        add_from_repository(cfn_registry, "resource", "Cloudformation")
    if framework == "kubernetes" or framework == "all":
        add_from_repository(k8_registry, "PodSecurityPolicy", "Kubernetes")
    if framework == "serverless" or framework == "all":
        add_from_repository(sls_registry, "resource", "serverless")
    if framework == "arm" or framework == "all":
        add_from_repository(arm_registry, "resource", "arm")
    return sorted(printable_checks_list, key=get_compare_key)


if __name__ == '__main__':
    print_checks()
