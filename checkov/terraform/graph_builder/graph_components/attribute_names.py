from dataclasses import dataclass

from checkov.common.graph.graph_builder import CustomAttributes as CommonCustomAttributes, props


@dataclass
class CustomAttributes(CommonCustomAttributes):
    ENCRYPTION = "encryption_"
    ENCRYPTION_DETAILS = "encryption_details_"


reserved_attribute_names = props(CustomAttributes)
