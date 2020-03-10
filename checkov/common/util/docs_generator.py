#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.cloudformation.checks.resource.registry import resource_registry as cfn_registry

def print_checks():
    printable_checks_list = get_checks()
    print(
        tabulate(printable_checks_list, headers=["Id", "Type", "Entity", "Policy", "IaC"], tablefmt="github",
                 showindex=True))
    print("\n\n---\n\n")


def get_checks():
    printable_checks_list = []
    for key in resource_registry.checks.keys():
        for check in resource_registry.checks[key]:
            printable_checks_list.append([check.id, "resource", key, check.name, "Terraform"])
    for key in data_registry.checks.keys():
        for check in data_registry.checks[key]:
            printable_checks_list.append([check.id, "data", key, check.name, "Terraform"])
    for key in cfn_registry.checks.keys():
        for check in cfn_registry.checks[key]:
            printable_checks_list.append([check.id, "resource", key, check.name, "Cloudformation"])
    return printable_checks_list


if __name__ == '__main__':
    print_checks()
