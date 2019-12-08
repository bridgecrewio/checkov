#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraform.checks.resource.registry import resource_registry


def print_checks():
    printable_checks_list = []
    for key in resource_registry.scanners.keys():
        for check in resource_registry.checks[key]:
            printable_checks_list.append([key, check.name])
    print(tabulate(printable_checks_list, headers=["Resource", "Policy"], tablefmt="github", showindex=True))


print_checks()
