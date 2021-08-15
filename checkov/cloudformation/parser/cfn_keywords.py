from enum import Enum


class IntrinsicFunctions(str, Enum):
    BASE64 = "Fn::Base64"
    CIDR = "Fn::Cidr"
    FIND_IN_MAP = "Fn::FindInMap"
    GET_ATT = "Fn::GetAtt"
    GET_AZS = "Fn::GetAZs"
    IMPORT_VALUE = "Fn::ImportValue"
    JOIN = "Fn::Join"
    SELECT = "Fn::Select"
    SPLIT = "Fn::Split"
    SUB = "Fn::Sub"
    TRANSFORM = "Fn::Transform"
    REF = "Ref"
    CONDITION = "Condition"


class ConditionFunctions(str, Enum):
    AND = "Fn::And"
    EQUALS = "Fn::Equals"
    IF = "Fn::If"
    NOT = "Fn::Not"
    OR = "Fn::Or"


class ResourceAttributes(str, Enum):
    CREATION_POLICY = "CreationPolicy"
    DELETION_POLICY = "DeletionPolicy"
    DEPENDS_ON = "DependsOn"
    METADATA = "Metadata"
    UPDATE_POLICY = "UpdatePolicy"
    UPDATE_REPLACE_POLICY = "UpdateReplacePolicy"
