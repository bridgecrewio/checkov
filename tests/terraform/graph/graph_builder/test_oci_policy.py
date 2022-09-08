"""Test if OCI policy statements are evaluated correctly."""

import os
from pathlib import Path
from unittest import mock

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.terraform.graph_manager import TerraformGraphManager

@mock.patch.dict(os.environ, {"CKV_TERRAFORM_PROVIDER": "OCI"})
def test_oci_policy_statements_with_provider_env_var():
    # given
    resources_dir = Path(__file__).parent.parent / "resources/oci_policies"
    graph_manager = TerraformGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, _ = graph_manager.build_graph_from_source_directory(
        source_dir=str(resources_dir), render_variables=True
    )

    # then
    statements = local_graph.vertices[0].config["oci_identity_policy"]["example"]["statements"][0]
    assert statements == [
        "allow group group-admin-001 to use groups in tenancy where target.group.name != 'Administrators'"
    ]


def test_oci_policy_statements_without_provider_env_var():
    # given
    resources_dir = Path(__file__).parent.parent / "resources/oci_policies"
    graph_manager = TerraformGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, _ = graph_manager.build_graph_from_source_directory(str(resources_dir), render_variables=True)

    # then
    statements = local_graph.vertices[0].config["oci_identity_policy"]["example"]["statements"][0]
    # If CKV_TERRAFORM_PROVIDER is not set to "OCI", Checkov wrongly evaluates this policy statement.
    # Remove this assertion when Checkov can handle OCI policy statement evaluation.
    assert statements == ["True"]
