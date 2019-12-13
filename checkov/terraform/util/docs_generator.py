#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraform.checks.resource.registry import resource_registry


def print_checks():
    printable_checks_list = get_checks()
    print(tabulate(printable_checks_list, headers=["id", "Resource", "Policy"], tablefmt="github", showindex=True))
    print("\n\n---\n\n")


def get_checks():
    printable_checks_list = []
    for key in resource_registry.checks.keys():
        for check in resource_registry.checks[key]:
            printable_checks_list.append([check.id, key, check.name])
    return printable_checks_list


print_checks()
