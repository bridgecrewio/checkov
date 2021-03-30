from dataclasses import dataclass
from enum import Enum


@dataclass
class CustomAttributes:
    BLOCK_NAME = "block_name_"
    BLOCK_TYPE = "block_type_"
    FILE_PATH = "file_path_"
    CONFIG = "config_"
    LABEL = "label_"
    ID = "id_"
    HASH = "hash"
    RENDERING_BREADCRUMBS = "rendering_breadcrumbs_"
    SOURCE = "source_"
    RESOURCE_TYPE = "resource_type"
    RESOURCE_ID = "resource_id"
    SOURCE_MODULE = "source_module_"


def props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']


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
