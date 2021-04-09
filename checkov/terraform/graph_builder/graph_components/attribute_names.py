from dataclasses import dataclass

from checkov.common.graph.graph_builder import CustomAttributes, props


@dataclass
class CustomAttributes(CustomAttributes):
    SOURCE_MODULE = "source_module_"
    ENCRYPTION = "encryption_"
    ENCRYPTION_DETAILS = "encryption_details_"


reserved_attribute_names = props(CustomAttributes)
