from __future__ import annotations

from checkov.common.graph.graph_builder import EncryptionTypes
from checkov.common.graph.graph_builder.graph_components.generic_resource_encryption_base import GenericResourceEncryptionBase
from checkov.common.util.data_structures_utils import get_empty_list_str


class GenericResourceEncryption(GenericResourceEncryptionBase):
    def __init__(
        self,
        resource_type: str,
        attribute_values_map: dict[str, list[bool] | list[str]],
        enabled_by_default: bool = False,
    ) -> None:
        super().__init__(resource_type,
                         attribute_values_map,
                         enabled_by_default,
                         node_to_node_encryption="NodeToNodeEncryptionOptions")
        if self.resource_type.startswith("AWS::"):
            self.default_description = EncryptionTypes.DEFAULT_KMS.value


# This map allows dynamically creating the check for each resource type based on GenericResourceEncryption.
# Please check out the constructor to understand all the edge cases.
ENCRYPTION_BY_RESOURCE_TYPE: dict[str, GenericResourceEncryption] = {
    "AWS::ECR::Repository": GenericResourceEncryption(
        "AWS::ECR::Repository",
        {
            "EncryptionConfiguration.EncryptionType": [EncryptionTypes.AES256.value, EncryptionTypes.KMS_VALUE.value],
            "EncryptionConfiguration.KmsKey": get_empty_list_str(),
        },
    ),
    "AWS::Neptune::DBCluster": GenericResourceEncryption(
        "AWS::Neptune::DBCluster", {"StorageEncrypted": [True], "KmsKeyId": get_empty_list_str()}
    ),
    "AWS::EFS::FileSystem": GenericResourceEncryption("AWS::EFS::FileSystem", {"Encrypted": [True], "KmsKeyId": get_empty_list_str()}),
    "AWS::EC2::Volume": GenericResourceEncryption("AWS::EC2::Volume", {"Encrypted": [True], "KmsKeyId": get_empty_list_str()}),
    "AWS::ElastiCache::ReplicationGroup": GenericResourceEncryption(
        "AWS::ElastiCache::ReplicationGroup", {"AtRestEncryptionEnabled": [True], "KmsKeyId": ["arn"]}
    ),
    "AWS::Elasticsearch::Domain": GenericResourceEncryption(
        "AWS::Elasticsearch::Domain",
        {"EncryptionAtRestOptions.Enabled": [True], "EncryptionAtRestOptions.KmsKeyId": get_empty_list_str(), "NodeToNodeEncryptionOptions.Enabled": [True]},
    ),
    "AWS::MSK::Cluster": GenericResourceEncryption(
        "AWS::MSK::Cluster", {"EncryptionInfo.EncryptionAtRest.DataVolumeKMSKeyId": get_empty_list_str()}
    ),
    "AWS::DocDB::DBCluster": GenericResourceEncryption(
        "AWS::DocDB::DBCluster", {"StorageEncrypted": [True], "KmsKeyId": get_empty_list_str()}
    ),
    "AWS::CodeBuild::Project": GenericResourceEncryption("AWS::CodeBuild::Project", {"EncryptionKey": get_empty_list_str()}),
    "AWS::CodeBuild::ReportGroup": GenericResourceEncryption(
        "AWS::CodeBuild::ReportGroup",
        {
            "ExportConfig.S3Destination.EncryptionDisabled": [False],
            "ExportConfig.S3Destination.EncryptionKey": get_empty_list_str(),
        },
    ),
    "AWS::Athena::WorkGroup": GenericResourceEncryption(
        "AWS::Athena::WorkGroup",
        {
            "WorkGroupConfiguration.ResultConfiguration.EncryptionConfiguration.EncryptionOption": [
                "SSE_S3",
                "SSE_KMS",
                "CSE_KMS",
            ],
            "WorkGroupConfiguration.ResultConfiguration.EncryptionConfiguration.KmsKey": get_empty_list_str(),
        },
    ),
    "AWS::Kinesis::Stream": GenericResourceEncryption(
        "AWS::Kinesis::Stream", {"StreamEncryption.EncryptionType": [EncryptionTypes.KMS_VALUE.value], "StreamEncryption.KeyId": get_empty_list_str()}
    ),
    "AWS::EKS::Cluster": GenericResourceEncryption("AWS::EKS::Cluster", {"EncryptionConfig.Provider.KeyArn": get_empty_list_str()}),
    "AWS::DynamoDB::Table": GenericResourceEncryption(
        "AWS::DynamoDB::Table",
        {"SSESpecification.SSEEnabled": [True], "SSESpecification.KMSMasterKeyId": get_empty_list_str(), "SSESpecification.SSEType": get_empty_list_str()},
        enabled_by_default=True,
    ),
    "AWS::RDS::DBCluster": GenericResourceEncryption("AWS::RDS::DBCluster", {"StorageEncrypted": [True], "KmsKeyId": get_empty_list_str()}),
    "AWS::RDS::GlobalCluster": GenericResourceEncryption("AWS::RDS::GlobalCluster", {"StorageEncrypted": [True]}),
    "AWS::S3::Bucket": GenericResourceEncryption(
        "AWS::S3::Bucket",
        {
            "BucketEncryption.ServerSideEncryptionConfiguration.ServerSideEncryptionByDefault.SSEAlgorithm": [
                EncryptionTypes.AWS_KMS_VALUE.value,
                EncryptionTypes.AES256.value,
            ],
            "server_side_encryption_configuration.rule.apply_server_side_encryption_by_default.KMSMasterKeyID": get_empty_list_str(),
        },
    ),
    "AWS::Logs::LogGroup": GenericResourceEncryption(
        "AWS::Logs::LogGroup", {"KmsKeyId": get_empty_list_str()}, enabled_by_default=True
    ),
    "AWS::CloudTrail::Trail": GenericResourceEncryption("AWS::CloudTrail::Trail", {"KMSKeyId": get_empty_list_str()}),
    "AWS::DAX::Cluster": GenericResourceEncryption("AWS::DAX::Cluster", {"SSESpecification.SSEEnabled": [True]}),
    "AWS::Redshift::Cluster": GenericResourceEncryption("AWS::Redshift::Cluster", {"Encrypted": [True], "KmsKeyId": get_empty_list_str()}),
    "AWS::SNS::Topic": GenericResourceEncryption("AWS::SNS::Topic", {"KmsMasterKeyId": get_empty_list_str()}),
    "AWS::SQS::Queue": GenericResourceEncryption("AWS::SQS::Queue", {"KmsMasterKeyId": get_empty_list_str()}),
    "AWS::RDS::DBInstance": GenericResourceEncryption("AWS::RDS::DBInstance", {"StorageEncrypted": [True]})
}
