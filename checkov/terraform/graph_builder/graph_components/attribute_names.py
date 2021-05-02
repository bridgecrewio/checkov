from dataclasses import dataclass

from checkov.common.graph.graph_builder import CustomAttributes, props


@dataclass
class CustomTerraformAttributes(CustomAttributes):
    ENCRYPTION = "encryption_"
    ENCRYPTION_DETAILS = "encryption_details_"


reserved_attribute_names = props(CustomTerraformAttributes)
