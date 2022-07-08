from dataclasses import dataclass
from typing import Any, Dict, Optional
from checkov.common.graph.graph_builder.graph_components.attribute_names import EncryptionValues
from checkov.common.graph.graph_builder.graph_components.blocks import Block


@dataclass
class EncryptionResult:
    encrypted: str
    reason: str


class GraphResourcesEncryptionManager():
    def __init__(self) -> None:
        self._encription_by_resource_type: Dict[str, Any] = {}

    def set_encription_by_resource_type(self, encription_by_resource_type: Dict[str, Any]) -> None:
        self._encription_by_resource_type = encription_by_resource_type

    def get_encryption_result(self, vertex: Block) -> Optional[EncryptionResult]:
        resource_type = vertex.id.split(".")[0]
        encryption_conf = self._encription_by_resource_type.get(resource_type)
        if not encryption_conf:
            return None
        attributes = vertex.get_attribute_dict()
        is_encrypted, reason = encryption_conf.is_encrypted(attributes)
        # TODO: Does not support possible dependency (i.e. S3 Object being encrypted due to S3 Bucket config)
        encrypted = (EncryptionValues.ENCRYPTED.value if is_encrypted else EncryptionValues.UNENCRYPTED.value)
        return EncryptionResult(encrypted, reason)
