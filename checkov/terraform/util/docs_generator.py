#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraform.checks.resource.registry import resource_registry


def print_scanners():
    printable_scanner_list = []
    for key in resource_registry.scanners.keys():
        for scanner in resource_registry.scanners[key]:
            printable_scanner_list.append([key, scanner.name])
    print(tabulate(printable_scanner_list, headers=["Resource", "Policy"], tablefmt="github", showindex=True))


print_scanners()
