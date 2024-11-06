from pathlib import Path

from checkov.arm.graph_builder.local_graph import ArmLocalGraph
from checkov.arm.utils import get_files_definitions

EXAMPLES_DIR = Path(__file__).parent


def test_render_vars():
    # given
    test_file = EXAMPLES_DIR / "test_rendering.json"
    definitions, _, _ = get_files_definitions([str(test_file)])
    local_graph = ArmLocalGraph(definitions=definitions)
    # when
    local_graph.build_graph(render_variables=True)

    # then
    assert len(local_graph.vertices) == 5
    assert len(local_graph.edges) == 5
    assert local_graph.vertices[2].attributes['name'] == "[format('{0}/{1}', aci-vnet, aci-networkProfile)]"
    assert local_graph.vertices[2].attributes['id'] == "[resourceId('Microsoft.Network/networkProfiles', aci-networkProfile)]"
    assert local_graph.vertices[2].attributes['location'] == "eth0"
    assert local_graph.vertices[2].attributes['properties.addressSpace.addressPrefixes.0'] == "10.0.0.0/16"
    assert local_graph.vertices[2].attributes['properties']['addressSpace']['addressPrefixes'][0] == "10.0.0.0/16"

