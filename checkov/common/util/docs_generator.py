#!/usr/bin/env python

import re
from typing import List, Optional, Tuple, Union

from tabulate import tabulate

from checkov.arm.registry import arm_resource_registry, arm_parameter_registry
from checkov.cloudformation.checks.resource.registry import cfn_registry as cfn_registry
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.checks_infra.registry import BaseRegistry as BaseGraphRegistry, get_graph_checks_registry
from checkov.dockerfile.registry import registry as dockerfile_registry
from checkov.github.registry import registry as github_configuration_registry
from checkov.kubernetes.checks.resource.registry import registry as k8_registry
from checkov.secrets.runner import CHECK_ID_TO_SECRET_TYPE
from checkov.serverless.registry import sls_registry
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry

ID_PARTS_PATTERN = re.compile(r'([^_]*)_([^_]*)_(\d+)')


def get_compare_key(c):
    res = []
    for match in ID_PARTS_PATTERN.finditer(c[0]):
        ckv, framework, number = match.groups()
        numeric_value = int(number) if number else 0
        # count number of leading zeros
        same_number_ordering = len(number) - len(number.lstrip('0'))
        res.append((framework, ckv, numeric_value, same_number_ordering, c[2]))
    return res


def print_checks(frameworks: Optional[List[str]] = None, use_bc_ids: bool = False) -> None:
    framework_list = frameworks if frameworks else ["all"]
    printable_checks_list = get_checks(framework_list, use_bc_ids=use_bc_ids)
    print(
        tabulate(printable_checks_list, headers=["Id", "Type", "Entity", "Policy", "IaC"], tablefmt="github",
                 showindex=True))
    print("\n\n---\n\n")


def get_checks(frameworks: Optional[List[str]] = None, use_bc_ids: bool = False) -> List[Tuple[str, str, str, str, str]]:
    framework_list = frameworks if frameworks else ["all"]
    printable_checks_list = []

    def add_from_repository(registry: Union[BaseCheckRegistry, BaseGraphRegistry], checked_type: str, iac: str) -> None:
        nonlocal printable_checks_list
        if isinstance(registry, BaseCheckRegistry):
            for entity, check in registry.all_checks():
                printable_checks_list.append((check.get_output_id(use_bc_ids), checked_type, entity, check.name, iac))
        elif isinstance(registry, BaseGraphRegistry):
            for check in registry.checks:
                for rt in check.resource_types:
                    printable_checks_list.append((check.get_output_id(use_bc_ids), checked_type, rt, check.name, iac))

    if any(x in framework_list for x in ("all", "terraform")):
        add_from_repository(resource_registry, "resource", "Terraform")
        add_from_repository(data_registry, "data", "Terraform")
        add_from_repository(provider_registry, "provider", "Terraform")
        add_from_repository(module_registry, "module", "Terraform")

        graph_registry = get_graph_checks_registry("terraform")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "Terraform")
    if any(x in framework_list for x in ("all", "cloudformation")):
        add_from_repository(cfn_registry, "resource", "Cloudformation")
    if any(x in framework_list for x in ("all", "kubernetes")):
        add_from_repository(k8_registry, "resource", "Kubernetes")
    if any(x in framework_list for x in ("all", "serverless")):
        add_from_repository(sls_registry, "resource", "serverless")
    if any(x in framework_list for x in ("all", "dockerfile")):
        add_from_repository(dockerfile_registry, "dockerfile", "dockerfile")
    if any(x in framework_list for x in ("all", "github_configuration")):
        add_from_repository(github_configuration_registry, "github_configuration", "github_configuration")
    if any(x in framework_list for x in ("all", "arm")):
        add_from_repository(arm_resource_registry, "resource", "arm")
        add_from_repository(arm_parameter_registry, "parameter", "arm")
    if any(x in framework_list for x in ("all", "secrets")):
        for check_id, check_type in CHECK_ID_TO_SECRET_TYPE.items():
            printable_checks_list.append((check_id, check_type, "secrets", check_type, "secrets"))
    return sorted(printable_checks_list, key=get_compare_key)


if __name__ == '__main__':
    print_checks()
