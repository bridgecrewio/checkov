from dataclasses import dataclass
from enum import Enum
from typing import List, Any


@dataclass
class CustomAttributes:
    BLOCK_NAME = "block_name_"
    BLOCK_TYPE = "block_type_"
    FILE_PATH = "file_path_"
    CONFIG = "config_"
    ATTRIBUTES = "attributes_"
    LABEL = "label_"
    ID = "id_"
    HASH = "hash"
    RENDERING_BREADCRUMBS = "rendering_breadcrumbs_"
    SOURCE = "source_"
    RESOURCE_TYPE = "resource_type"
    RESOURCE_ID = "resource_id"
    SOURCE_MODULE = "source_module_"
    MODULE_DEPENDENCY = "module_dependency_"
    MODULE_DEPENDENCY_NUM = "module_dependency_num_"
    ENCRYPTION = "encryption_"
    ENCRYPTION_DETAILS = "encryption_details_"


def props(cls: Any) -> List[str]:
    return [i for i in cls.__dict__.keys() if i[:1] != "_"]


reserved_attribute_names = props(CustomAttributes)


class EncryptionValues(Enum):
    ENCRYPTED = "ENCRYPTED"
    UNENCRYPTED = "UNENCRYPTED"


class EncryptionTypes(Enum):
    KMS_VALUE = "KMS"
    NODE_TO_NODE = "node-to-node"
    DEFAULT_KMS = "Default KMS"
    AES256 = "AES256"
    AWS_KMS_VALUE = "aws:kms"
