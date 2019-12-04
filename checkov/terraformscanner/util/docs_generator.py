#!/usr/bin/env python

from tabulate import tabulate

from checkov.terraformscanner.resource_scanner_registry import resource_scanner_registry


def print_scanners():
    printable_scanner_list = []
    for key in resource_scanner_registry.scanners.keys():
        for scanner in resource_scanner_registry.scanners[key]:
            printable_scanner_list.append([key, scanner.name])
    print(tabulate(printable_scanner_list, headers=["Resource", "Policy"], tablefmt="github", showindex=True))


print_scanners()
