from __future__ import annotations

import pytest

from checkov.pulumi.mappings import PROVIDERS, _load, get_resource_mapping
from checkov.pulumi.mappings.generate import checked_tf_types

# resource types used by checks, which don't exist (anymore) in the Terraform providers bridged by Pulumi
NOT_BRIDGED = {
    "aws_db_security_group",
    "aws_ec2_spot_fleet_request",
    "aws_elasticache_security_group",
    "aws_redshift_security_group",
    "azurerm_data_lake_store",
    "azurerm_mariadb_firewall_rule",
    "azurerm_mariadb_server",
    "azurerm_monitor_log_profile",
    "azurerm_mysql_firewall_rule",
    "azurerm_mysql_server",
    "azurerm_mysql_server_key",
    "azurerm_sql_active_directory_administrator",
    "azurerm_sql_firewall_rule",
    "azurerm_sql_server",
    "google_notebooks_instance",
    "google_notebooks_runtime",
    "google_project_services",
}


def test_checked_resource_types_are_mapped() -> None:
    mapped = {entry["type"] for provider in PROVIDERS for entry in _load(provider)["resources"].values()}
    checked = {t for t in checked_tf_types() if t.startswith(("aws_", "google_", "azurerm_"))}

    assert len(checked) > 400
    unmapped = checked - mapped - NOT_BRIDGED
    # new checks for resource types, which are newer than the mappings, need a regeneration of the mappings
    assert len(unmapped) / len(checked) < 0.05, sorted(unmapped)
    assert not NOT_BRIDGED & mapped


@pytest.mark.parametrize("provider", PROVIDERS)
def test_mapping_files(provider: str) -> None:
    mapping = _load(provider)

    assert len(mapping["resources"]) > 1000
    for token, entry in mapping["resources"].items():
        assert token.startswith(f"{provider}:")
        assert entry["type"].startswith(("aws_", "google_", "azurerm_"))
    for alias, token in mapping["aliases"].items():
        assert alias not in mapping["resources"]
        assert get_resource_mapping(alias) == mapping["resources"][token]
