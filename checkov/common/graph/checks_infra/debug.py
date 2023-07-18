from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from typing import Any, TYPE_CHECKING

import yaml
from termcolor import colored

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.env_vars_config import env_vars_config

if TYPE_CHECKING:
    from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def graph_check(check_id: str, check_name: str) -> None:
    if not env_vars_config.EXPERIMENTAL_GRAPH_DEBUG:
        return

    print(f'\nEvaluating graph policy: "{check_id}" - "{check_name}"')


def resource_types(resource_types: Iterable[str], resource_count: int, operator: str) -> None:
    if not env_vars_config.EXPERIMENTAL_GRAPH_DEBUG:
        return

    resource_types_str = '", "'.join(resource_types)
    print(
        f'\nFound {resource_count} resources with resource types: "{resource_types_str}" to check against operator: "{operator}"'
    )


def attribute_block(
    resource_types: Iterable[str],
    attribute: str | None,
    operator: str,
    value: str | list[str] | None,
    resource: dict[str, Any],
    status: str,
) -> None:
    if not env_vars_config.EXPERIMENTAL_GRAPH_DEBUG:
        return

    attribute_block_conf = _create_attribute_block(
        resource_types=resource_types, attribute=attribute, operator=operator, value=value
    )
    color = "green" if status == "passed" else "red"

    print("\nEvaluated block:\n")
    print(colored(yaml.dump([attribute_block_conf], sort_keys=False), "blue"))
    print("and got:")
    print(colored(f'\nResource "{resource[CustomAttributes.ID]}" {status}:', color))
    print(colored(json.dumps(resource[CustomAttributes.CONFIG], indent=2), "yellow"))


def connection_block(
    resource_types: Iterable[str],
    connected_resource_types: Iterable[str],
    operator: str,
    passed_resources: list[dict[str, Any]],
    failed_resources: list[dict[str, Any]],
) -> None:
    if not env_vars_config.EXPERIMENTAL_GRAPH_DEBUG:
        return

    connection_block_conf = _create_connection_block(
        resource_types=resource_types,
        connected_resource_types=connected_resource_types,
        operator=operator,
    )

    passed_resources_str = '", "'.join(resource[CustomAttributes.ID] for resource in passed_resources)
    failed_resources_str = '", "'.join(resource[CustomAttributes.ID] for resource in failed_resources)

    print("\nEvaluated blocks:\n")
    print(colored(yaml.dump([connection_block_conf], sort_keys=False), "blue"))
    print("and got:\n")
    print(colored(f'Passed resources: "{passed_resources_str}"', "green"))
    print(colored(f'Failed resources: "{failed_resources_str}"', "red"))


def complex_connection_block(
    solvers: list[BaseSolver],
    operator: str,
    passed_resources: list[dict[str, Any]],
    failed_resources: list[dict[str, Any]],
) -> None:
    if not env_vars_config.EXPERIMENTAL_GRAPH_DEBUG:
        return

    # to prevent circular dependencies
    from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
    from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
    from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
    from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import (
        ComplexConnectionSolver,
    )
    from checkov.common.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver

    complex_connection_block = []

    for solver in solvers:
        if isinstance(solver, BaseAttributeSolver):
            block = _create_attribute_block(
                resource_types=solver.resource_types,
                attribute=solver.attribute,
                operator=solver.operator,
                value=solver.value,
            )
        elif isinstance(solver, BaseFilterSolver):
            block = _create_filter_block(attribute=solver.attribute, operator=solver.operator, value=solver.value)
        elif isinstance(solver, (ComplexConnectionSolver, BaseComplexSolver)):
            # ComplexConnectionSolver check needs to be before BaseConnectionSolver, because it is a subclass
            block = {solver.operator: ["..." for _ in solver.solvers]}
        elif isinstance(solver, BaseConnectionSolver):
            block = _create_connection_block(
                resource_types=solver.resource_types,
                connected_resource_types=solver.connected_resources_types,
                operator=solver.operator,
            )
        else:
            logger.info(f"Unsupported solver type {type(solver)} found")
            continue

        complex_connection_block.append(block)

    passed_resources_str = '", "'.join(resource[CustomAttributes.ID] for resource in passed_resources)
    failed_resources_str = '", "'.join(resource[CustomAttributes.ID] for resource in failed_resources)

    print("\nEvaluated blocks:\n")
    print(colored(yaml.dump([{operator: complex_connection_block}], sort_keys=False), "blue"))
    print("and got:\n")
    print(colored(f'Passed resources: "{passed_resources_str}"', "green"))
    print(colored(f'Failed resources: "{failed_resources_str}"', "red"))


def _create_attribute_block(
    resource_types: Iterable[str], attribute: str | None, operator: str, value: str | list[str] | None
) -> dict[str, Any]:
    attribute_block_conf = {
        "cond_type": "attribute",
        "resource_types": resource_types,
        "attribute": attribute,
        "operator": operator,
    }
    if value is not None:
        attribute_block_conf["value"] = value

    return attribute_block_conf


def _create_connection_block(
    resource_types: Iterable[str], connected_resource_types: Iterable[str], operator: str
) -> dict[str, Any]:
    attribute_block_conf = {
        "cond_type": "connection",
        "resource_types": resource_types,
        "connected_resource_types": connected_resource_types,
        "operator": operator,
    }
    return attribute_block_conf


def _create_filter_block(attribute: str | None, operator: str, value: str | list[str]) -> dict[str, Any]:
    attribute_block_conf = {
        "cond_type": "filter",
        "attribute": attribute,
        "operator": operator,
        "value": value,
    }
    return attribute_block_conf
