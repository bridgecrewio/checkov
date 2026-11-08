from pathlib import Path

import pytest

from checkov.arm.runner import Runner as ArmRunner
from checkov.bicep.graph_builder.local_graph import BicepLocalGraph
from checkov.bicep.parser import Parser
from checkov.bicep.runner import Runner
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples" / "same_name_in_multiple_files"
EVENT_HUB_FILE = EXAMPLES_DIR / "event_hub" / "main.bicep"
STORAGE_FILE = EXAMPLES_DIR / "storage" / "main.bicep"


def _build_rendered_graph(file_order: list[Path]) -> BicepLocalGraph:
    definitions = {}
    for file_path in file_order:
        template, _ = Parser().parse(file_path)
        definitions[file_path] = template

    local_graph = BicepLocalGraph(definitions=definitions)
    local_graph.build_graph(render_variables=True)
    return local_graph


def _resource_config(local_graph: BicepLocalGraph, file_path: Path, name: str) -> dict:
    vertex = local_graph.vertices[local_graph.vertices_by_path_and_name[(str(file_path), name)]]
    return vertex.config["config"]


@pytest.mark.parametrize(
    "file_order",
    [
        pytest.param([EVENT_HUB_FILE, STORAGE_FILE], id="event_hub_first"),
        pytest.param([STORAGE_FILE, EVENT_HUB_FILE], id="storage_first"),
    ],
)
def test_same_name_in_multiple_files_resolves_within_own_file(file_order: list[Path]) -> None:
    # when
    local_graph = _build_rendered_graph(file_order)

    # then
    event_hub_config = _resource_config(local_graph, EVENT_HUB_FILE, "eventHubNamespace")
    storage_config = _resource_config(local_graph, STORAGE_FILE, "storageAccount")

    assert event_hub_config["properties"]["minimumTlsVersion"] == "1.2"
    assert storage_config["properties"]["minimumTlsVersion"] == "TLS1_2"


@pytest.mark.parametrize(
    "file_order",
    [
        pytest.param([EVENT_HUB_FILE, STORAGE_FILE], id="event_hub_first"),
        pytest.param([STORAGE_FILE, EVENT_HUB_FILE], id="storage_first"),
    ],
)
def test_edges_do_not_cross_files(file_order: list[Path]) -> None:
    # when
    local_graph = _build_rendered_graph(file_order)

    # then
    for edge in local_graph.edges:
        assert local_graph.vertices[edge.origin].path == local_graph.vertices[edge.dest].path


def test_runner_check_uses_value_from_own_file() -> None:
    # given: initialize the ARM runner to add the ARM checks to the Bicep registry
    ArmRunner()

    # when
    report = Runner().run(
        root_folder=str(EXAMPLES_DIR),
        runner_filter=RunnerFilter(framework=["bicep"], checks=["CKV_AZURE_223"]),
    )

    # then
    event_hub_results = [
        record.check_result["result"]
        for record in report.passed_checks + report.failed_checks
        if record.resource == "Microsoft.EventHub/namespaces.eventHubNamespace"
    ]
    assert event_hub_results == [CheckResult.PASSED]
