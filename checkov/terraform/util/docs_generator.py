#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.checks.data.registry import data_registry


def print_checks():
    printable_checks_list = get_checks()
    print(
        tabulate(printable_checks_list, headers=["Id", "Type", "Entity", "Policy"], tablefmt="github", showindex=True))
    print("\n\n---\n\n")


def get_checks():
    printable_checks_list = []
    for key in resource_registry.checks.keys():
        for check in resource_registry.checks[key]:
            printable_checks_list.append([check.id, "resource", key, check.name])
    for key in data_registry.checks.keys():
        for check in data_registry.checks[key]:
            printable_checks_list.append([check.id, "data", key, check.name])
    return printable_checks_list


print_checks()
