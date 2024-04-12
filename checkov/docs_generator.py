#!/usr/bin/env python

from __future__ import annotations

import os
import re
import inspect
from typing import List, Optional, Tuple, Union

from tabulate import tabulate

from checkov.ansible.checks.registry import registry as ansible_registry
from checkov.argo_workflows.checks.registry import registry as argo_workflows_registry
from checkov.arm.registry import arm_resource_registry, arm_parameter_registry
from checkov.azure_pipelines.checks.registry import registry as azure_pipelines_registry
from checkov.bicep.checks.param.registry import registry as bicep_param_registry
from checkov.bicep.checks.resource.registry import registry as bicep_resource_registry
from checkov.bitbucket.registry import registry as bitbucket_configuration_registry
from checkov.bitbucket_pipelines.registry import registry as bitbucket_pipelines_registry
from checkov.circleci_pipelines.registry import registry as circleci_pipelines_registry
from checkov.cloudformation.checks.resource.registry import cfn_registry as cfn_registry
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.checks_infra.registry import BaseRegistry as BaseGraphRegistry, get_graph_checks_registry
from checkov.common.runners.base_runner import strtobool
from checkov.dockerfile.registry import registry as dockerfile_registry
from checkov.github.registry import registry as github_configuration_registry
from checkov.github_actions.checks.registry import registry as github_actions_jobs_registry
from checkov.gitlab.registry import registry as gitlab_configuration_registry
from checkov.gitlab_ci.checks.registry import registry as gitlab_ci_jobs_registry
from checkov.kubernetes.checks.resource.registry import registry as k8_registry
from checkov.secrets.runner import CHECK_ID_TO_SECRET_TYPE
from checkov.serverless.registry import sls_registry
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.openapi.checks.registry import openapi_registry
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.runner_filter import RunnerFilter

ID_PARTS_PATTERN = re.compile(r'([^_]*)_([^_]*)_(\d+)')
CODE_LINK_BASE = 'https://github.com/bridgecrewio/checkov/blob/main/checkov'
CREATE_MARKDOWN_HYPERLINKS = strtobool(os.getenv("CHECKOV_CREATE_MARKDOWN_HYPERLINKS", "FALSE"))
SKIP_CHECK_IDS = {
    "CKV_SECRET_10",  # this is an intermediate step, which is needed for another check
}


def get_compare_key(c: list[str] | tuple[str, ...]) -> list[tuple[str, str, int, int, str]]:
    res = []
    for match in ID_PARTS_PATTERN.finditer(c[0]):
        ckv, framework, number = match.groups()
        numeric_value = int(number) if number else 0
        # count number of leading zeros
        same_number_ordering = len(number) - len(number.lstrip('0'))
        res.append((framework, ckv, numeric_value, same_number_ordering, c[2]))
    return res


def print_checks(frameworks: Optional[List[str]] = None, use_bc_ids: bool = False,
                 include_all_checkov_policies: bool = True, filtered_policy_ids: Optional[List[str]] = None,
                 filtered_exception_policy_ids: Optional[List[str]] = None) -> None:
    framework_list = frameworks if frameworks else ["all"]
    printable_checks_list = get_checks(framework_list, use_bc_ids=use_bc_ids,
                                       include_all_checkov_policies=include_all_checkov_policies,
                                       filtered_policy_ids=filtered_policy_ids or [],
                                       filtered_exception_policy_ids=filtered_exception_policy_ids or [])
    print(
        tabulate(printable_checks_list, headers=["Id", "Type", "Entity", "Policy", "IaC", "Resource Link"], tablefmt="github",
                 showindex=True))
    print("\n\n---\n\n")


def get_check_link(absolute_path: str) -> str:
    # this will do nothing unless it's a windows path
    absolute_path = absolute_path.replace('\\', '/')
    temp = absolute_path.split("checkov")
    # this will even work in the likely event that you're running checkov from a folder called checkov
    link = f'{CODE_LINK_BASE}{temp[len(temp)-1]}'

    if CREATE_MARKDOWN_HYPERLINKS:
        return f"[{absolute_path.rsplit('/', maxsplit=1)[1]}]({link})"

    return link


def get_checks(frameworks: Optional[List[str]] = None, use_bc_ids: bool = False,
               include_all_checkov_policies: bool = True, filtered_policy_ids: Optional[List[str]] = None,
               filtered_exception_policy_ids: Optional[List[str]] = None) -> List[Tuple[str, str, int, int, str, str]]:
    framework_list = frameworks if frameworks else ["all"]
    printable_checks_list: list[tuple[str, str, str, str, str, str]] = []
    filtered_policy_ids = filtered_policy_ids or []
    filtered_exception_policy_ids = filtered_exception_policy_ids or []
    runner_filter = RunnerFilter(include_all_checkov_policies=include_all_checkov_policies,
                                 filtered_policy_ids=filtered_policy_ids,
                                 filtered_exception_policy_ids=filtered_exception_policy_ids)

    def add_from_repository(registry: Union[BaseCheckRegistry, BaseGraphRegistry], checked_type: str, iac: str,
                            runner_filter: RunnerFilter = runner_filter) -> None:
        nonlocal printable_checks_list
        if isinstance(registry, BaseCheckRegistry):
            for entity, check in registry.all_checks():
                if runner_filter.should_run_check(check, check.id, check.bc_id, check.severity):
                    check_link = get_check_link(inspect.getfile(check.__class__))
                    printable_checks_list.append(
                        (check.get_output_id(use_bc_ids), checked_type, entity, check.name, iac, check_link))
        elif isinstance(registry, BaseGraphRegistry):
            for graph_check in registry.checks:
                if runner_filter.should_run_check(graph_check, graph_check.id, graph_check.bc_id, graph_check.severity):
                    if not graph_check.resource_types:
                        # only for platform custom polices with resource_types == all
                        graph_check.resource_types = ['all']
                    for rt in graph_check.resource_types:
                        if graph_check.check_path:
                            base_path = graph_check.check_path
                        else:
                            base_path = inspect.getfile(graph_check.__class__)
                        check_link = get_check_link(base_path)
                        printable_checks_list.append(
                            (graph_check.get_output_id(use_bc_ids), checked_type, rt, graph_check.name, iac, check_link))

    if any(x in framework_list for x in ("all", "terraform")):
        add_from_repository(resource_registry, "resource", "Terraform")
        add_from_repository(data_registry, "data", "Terraform")
        add_from_repository(provider_registry, "provider", "Terraform")
        add_from_repository(module_registry, "module", "Terraform")

        graph_registry = get_graph_checks_registry("terraform")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "Terraform")
    if any(x in framework_list for x in ("all", "cloudformation")):
        graph_registry = get_graph_checks_registry("cloudformation")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "Cloudformation")
        add_from_repository(cfn_registry, "resource", "Cloudformation")
    if any(x in framework_list for x in ("all", "kubernetes")):
        graph_registry = get_graph_checks_registry("kubernetes")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "Kubernetes")
        add_from_repository(k8_registry, "resource", "Kubernetes")
    if any(x in framework_list for x in ("all", "serverless")):
        add_from_repository(sls_registry, "resource", "serverless")
    if any(x in framework_list for x in ("all", "dockerfile")):
        graph_registry = get_graph_checks_registry("dockerfile")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "dockerfile")
        add_from_repository(dockerfile_registry, "dockerfile", "dockerfile")
    if any(x in framework_list for x in ("all", "github_configuration")):
        add_from_repository(github_configuration_registry, "github_configuration", "github_configuration")
    if any(x in framework_list for x in ("all", "github_actions")):
        graph_registry = get_graph_checks_registry("github_actions")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "github_actions")
        add_from_repository(github_actions_jobs_registry, "jobs", "github_actions")
    if any(x in framework_list for x in ("all", "gitlab_ci")):
        add_from_repository(gitlab_ci_jobs_registry, "jobs", "gitlab_ci")
    if any(x in framework_list for x in ("all", "gitlab_configuration")):
        add_from_repository(gitlab_configuration_registry, "gitlab_configuration", "gitlab_configuration")
    if any(x in framework_list for x in ("all", "bitbucket_configuration")):
        add_from_repository(bitbucket_configuration_registry, "bitbucket_configuration", "bitbucket_configuration")
    if any(x in framework_list for x in ("all", "bitbucket_pipelines")):
        add_from_repository(bitbucket_pipelines_registry, "bitbucket_pipelines", "bitbucket_pipelines")
    if any(x in framework_list for x in ("all", "circleci_pipelines")):
        add_from_repository(circleci_pipelines_registry, "circleci_pipelines", "circleci_pipelines")
    if any(x in framework_list for x in ("all", "argo_workflows")):
        add_from_repository(argo_workflows_registry, "argo_workflows", "Argo Workflows")
    if any(x in framework_list for x in ("all", "azure_pipelines")):
        add_from_repository(azure_pipelines_registry, "azure_pipelines", "Azure Pipelines")
    if any(x in framework_list for x in ("all", "arm")):
        graph_registry = get_graph_checks_registry("arm")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "arm")
        add_from_repository(arm_resource_registry, "resource", "arm")
        add_from_repository(arm_parameter_registry, "parameter", "arm")
    if any(x in framework_list for x in ("all", "bicep")):
        graph_registry = get_graph_checks_registry("bicep")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "Bicep")
        add_from_repository(bicep_param_registry, "parameter", "Bicep")
        add_from_repository(bicep_resource_registry, "resource", "Bicep")
    if any(x in framework_list for x in ("all", "openapi")):
        add_from_repository(openapi_registry, "resource", "OpenAPI")
    if any(x in framework_list for x in ("all", "ansible")):
        graph_registry = get_graph_checks_registry("ansible")
        graph_registry.load_checks()
        add_from_repository(graph_registry, "resource", "Ansible")
        add_from_repository(ansible_registry, "resource", "Ansible")
    if any(x in framework_list for x in ("all", "secrets")):
        for check_id, check_type in CHECK_ID_TO_SECRET_TYPE.items():
            if check_id in SKIP_CHECK_IDS:
                continue

            if not filtered_policy_ids or check_id in filtered_policy_ids:
                if use_bc_ids:
                    check_id = metadata_integration.get_bc_id(check_id)
                check_link = get_check_link(inspect.getfile(metadata_integration.__class__))
                printable_checks_list.append((check_id, check_type, "secrets", check_type, "secrets", check_link))
    return sorted(printable_checks_list, key=get_compare_key)  # type:ignore[arg-type]


if __name__ == '__main__':
    print_checks()
