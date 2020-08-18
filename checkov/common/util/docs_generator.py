#!/usr/bin/env python

import re

from tabulate import tabulate

from checkov.arm.registry import arm_registry
from checkov.cloudformation.checks.resource.registry import cfn_registry as cfn_registry
from checkov.kubernetes.registry import registry as k8_registry
from checkov.serverless.registry import sls_registry
from checkov.terraform.checks.data.registry import data_registry
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
    return sorted(printable_checks_list, key=get_compare_key)


if __name__ == '__main__':
    print_checks()
