from dataclasses import dataclass

from checkov.graph.graph_builder.graph_components.attribute_names import CustomAttributes, props


@dataclass
class CustomAttributes(CustomAttributes):
    SOURCE_MODULE = "source_module_"
    ENCRYPTION = "encryption_"
    ENCRYPTION_DETAILS = "encryption_details_"


reserved_attribute_names = props(CustomAttributes)
