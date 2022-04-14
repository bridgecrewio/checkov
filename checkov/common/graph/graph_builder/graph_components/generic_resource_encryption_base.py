from typing import Dict, List, Union, Tuple, Any

from checkov.common.graph.graph_builder import EncryptionTypes


class GenericResourceEncryptionBase:
    def __init__(
        self,
        resource_type: str,
        attribute_values_map: Dict[str, Union[List[bool], List[str]]],
        enabled_by_default: bool = False,
        node_to_node_encryption: str = ""
    ) -> None:
        """
        :param resource_type:           The resource type this checks. Only helps with debugging.
        :param attribute_values_map:    A dict that maps each attribute to its expected values. An attribute which
                                        points to an empty array can hold any value, except None, and identify the
                                        resource as an encrypted resource.
        :param enabled_by_default:      Some resources are encrypted by default, even if no configuration is present.
                                        Some are not. This helps implement that logic
        """
        self.enabled_by_default = enabled_by_default
        self.attribute_values_map = attribute_values_map
        self.resource_type = resource_type
        self.node_to_node_encryption = node_to_node_encryption
        self.default_description = ""

    def is_encrypted(self, atts_dict: Dict[str, Any]) -> Tuple[bool, str]:
        result = True
        result_description = ""
        for att, expected_vals in self.attribute_values_map.items():
            att_value = atts_dict.get(att)
            if att_value:
                result &= (len(expected_vals) == 0 and att_value is not None) or att_value in expected_vals
                if result:
                    if att_value == EncryptionTypes.AES256.value:
                        result_description = att_value
                    elif self.node_to_node_encryption in att:
                        result_description = EncryptionTypes.NODE_TO_NODE.value
                    elif result_description == "":
                        result_description = EncryptionTypes.KMS_VALUE.value

        if result_description == "" and result:
            # No encryption config was found. Drop back to defaults:
            result = self.enabled_by_default
            result_description = self.default_description if self.enabled_by_default else ""

        return result, result_description

    def __str__(self) -> str:
        return f"GenericResourceEncryption[{self.resource_type}]"
