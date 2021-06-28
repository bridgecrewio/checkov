from typing import Dict, List, Union, Tuple, Any

from checkov.common.graph.graph_builder import EncryptionTypes
from checkov.terraform.checks.utils.utils import decode_graph_property_value


class GenericResourceEncryption:
    def __init__(
        self,
        resource_type: str,
        attribute_values_map: Dict[str, Union[List[bool], List[str]]],
        enabled_by_default: bool = False,
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

        self.default_description = ""
        if self.resource_type.startswith("aws_"):
            self.default_description = EncryptionTypes.DEFAULT_KMS.value

    def is_encrypted(self, atts_dict: Dict[str, Any]) -> Tuple[bool, str]:
        result = True
        result_description = ""
        for att, expected_vals in self.attribute_values_map.items():
            att_conf = atts_dict.get(att)
            if att_conf:
                att_value = decode_graph_property_value(att_conf)
                result &= (len(expected_vals) == 0 and att_value is not None) or att_value in expected_vals
                if result:
                    if att_value == EncryptionTypes.AES256.value:
                        result_description = att_value
                    elif "node_to_node_encryption" in att:
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


# This map allows dynamically creating the check for each resource type based on GenericResourceEncryption.
# Please check out the constructor to understand all the edge cases.
ENCRYPTION_BY_RESOURCE_TYPE = {
    "aws_ecr_repository": GenericResourceEncryption(
        "aws_ecr_repository",
        {
            "encryption_configuration.encryption_type": [EncryptionTypes.AES256.value, EncryptionTypes.KMS_VALUE.value],
            "encryption_configuration.kms_key": [],
        },
    ),
    "aws_neptune_cluster": GenericResourceEncryption(
        "aws_neptune_cluster", {"storage_encrypted": [True], "kms_key_arn": []}
    ),
    "aws_efs_file_system": GenericResourceEncryption("aws_efs_file_system", {"encrypted": [True], "kms_key_id": []}),
    "aws_sagemaker_feature_group": GenericResourceEncryption(
        "aws_sagemaker_feature_group", {"security_config.kms_key_id": []}
    ),
    "aws_ebs_volume": GenericResourceEncryption("aws_ebs_volume", {"encrypted": [True], "kms_key_id": []}),
    "aws_elasticache_replication_group": GenericResourceEncryption(
        "aws_elasticache_replication_group", {"at_rest_encryption_enabled": [True], "kms_key_id": ["arn"],}
    ),
    "aws_elasticsearch_domain": GenericResourceEncryption(
        "aws_elasticsearch_domain",
        {"encrypt_at_rest.enabled": [True], "kms_key_id": [], "node_to_node_encryption.enabled": [True]},
    ),
    "aws_msk_cluster": GenericResourceEncryption(
        "aws_msk_cluster", {"encryption_info.encryption_at_rest_kms_key_arn": []}
    ),
    "aws_docdb_cluster": GenericResourceEncryption(
        "aws_docdb_cluster", {"storage_encrypted": [True], "kms_key_arn": []}
    ),
    "aws_codebuild_project": GenericResourceEncryption("aws_codebuild_project", {"encryption_key": []}),
    "aws_codebuild_report_group": GenericResourceEncryption(
        "aws_codebuild_report_group",
        {
            "export_config.s3_destination.encryption_disabled": [False],
            "export_config.s3_destination.encryption_key": [],
        },
    ),
    "aws_athena_database": GenericResourceEncryption(
        "aws_athena_database",
        {
            "encryption_configuration.encryption_option": ["SSE_S3", "SSE_KMS", "CSE_KMS"],
            "encryption_configuration.kms_key": [],
        },
    ),
    "aws_athena_workgroup": GenericResourceEncryption(
        "aws_athena_workgroup",
        {
            "configuration.result_configuration.encryption_configuration.encryption_option": [
                "SSE_S3",
                "SSE_KMS",
                "CSE_KMS",
            ],
            "configuration.result_configuration.encryption_configuration.kms_key_arn": [],
        },
    ),
    "aws_kinesis_stream": GenericResourceEncryption(
        "aws_kinesis_stream", {"encryption_type": [EncryptionTypes.KMS_VALUE.value], "kms_key_id": []}
    ),
    "aws_eks_cluster": GenericResourceEncryption("aws_eks_cluster", {"encryption_config.provider.key_arn": []}),
    "aws_dynamodb_table": GenericResourceEncryption(
        "aws_dynamodb_table",
        {"server_side_encryption.enabled": [True], "server_side_encryption.kms_key_arn": []},
        enabled_by_default=True,
    ),
    "aws_rds_cluster": GenericResourceEncryption("aws_rds_cluster", {"storage_encrypted": [True], "kms_key_id": []}),
    "aws_rds_global_cluster": GenericResourceEncryption("aws_rds_global_cluster", {"storage_encrypted": [True]}),
    "aws_s3_bucket": GenericResourceEncryption(
        "aws_s3_bucket",
        {
            "server_side_encryption_configuration.rule.apply_server_side_encryption_by_default.sse_algorithm": [
                EncryptionTypes.AWS_KMS_VALUE.value,
                EncryptionTypes.AES256.value,
            ],
            "server_side_encryption_configuration.rule.apply_server_side_encryption_by_default.kms_master_key_id": [],
        },
    ),
    "aws_s3_bucket_inventory": GenericResourceEncryption(
        "aws_s3_bucket_inventory", {"destination.bucket.encryption": []}
    ),
    "aws_s3_bucket_object": GenericResourceEncryption(
        "aws_s3_bucket_object",
        {
            "server_side_encryption": [EncryptionTypes.AWS_KMS_VALUE.value, EncryptionTypes.AES256.value],
            "kms_key_id": [],
        },
    ),
    "aws_cloudwatch_log_group": GenericResourceEncryption(
        "aws_cloudwatch_log_group", {"kms_key_id": []}, enabled_by_default=True
    ),
    "aws_cloudtrail": GenericResourceEncryption("aws_cloudtrail", {"kms_key_id": []}),
    "aws_dax_cluster": GenericResourceEncryption("aws_dax_cluster", {"server_side_encryption.enabled": [True]}),
    "aws_redshift_cluster": GenericResourceEncryption("aws_redshift_cluster", {"encrypted": [True], "kms_key_id": []}),
    "aws_sns_topic": GenericResourceEncryption("aws_sns_topic", {"kms_master_key_id": []}),
    "aws_sqs_queue": GenericResourceEncryption("aws_sqs_queue", {"kms_master_key_id": []}),
}
