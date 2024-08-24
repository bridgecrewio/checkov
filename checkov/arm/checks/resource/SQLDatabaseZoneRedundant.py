from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class SQLDatabaseZoneRedundant(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        This is a best practise which helps to:
        - Improved High Availability: Zone redundancy ensures that your database is replicated
          across Availability Zones within an Azure region. If one Availability Zone experiences an outage,
          your database continues to operate from the other zones, minimizing downtime.
        - Reduced Maintenance Downtime: Zone-redundant configurations often require
          less planned maintenance downtime because updates and patches can be applied to
          one zone at a time while the other zones continue to serve traffic.
        - Improved Scalability: Zone-redundant configurations are designed to scale with your workload.
          You can take advantage of features like Hyperscale to dynamically adjust resources based on
          your database's performance needs.
        - Improved SLA: Azure SQL Database zone-redundant configurations typically offer
          a higher service-level agreement (SLA) for availability compared to non-zone-redundant configurations.

        However, it's critical to note that:
        Note that:
        - Zone-redundant availability is available to databases in the
          General Purpose, Premium, Business Critical and Hyperscale service tiers of the vCore purchasing model,
          and not the Basic and Standard service tiers of the DTU-based purchasing model.
        - This may not be required for:
           - Databases that supports applications which doesn't a high maturity in terms of "High Availability"
           - Databases that are very sensitive to network latency that may increase the transaction commit time,
             and thus impact the performance of some OLTP workloads.
        """
        name = "Ensure the Azure SQL Database Namespace is zone redundant"
        id = "CKV_AZURE_229"
        supported_resources = ["Microsoft.Sql/servers/databases",]
        categories = [CheckCategories.BACKUP_AND_RECOVERY,]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/zoneRedundant"


check = SQLDatabaseZoneRedundant()
