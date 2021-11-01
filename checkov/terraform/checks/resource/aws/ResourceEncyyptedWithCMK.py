from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class ResourceEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure resource is encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_175"
        supported_resources = ['aws_cloudtrail',
                               'aws_fsx_lustre_file_system','aws_fsx_ontap_file_system',
                               'aws_fsx_windows_file_system','aws_imagebuilder_component','aws_s3_object_copy',
                               'aws_docdb_cluster','aws_ebs_snapshot_copy','aws_ebs_volume','aws_efs_file_system',
                               'aws_elasticache_replication_group','aws_kinesis_stream','aws_kinesis_video_stream',
                               'aws_redshift_cluster','aws_s3_bucket_object','aws_sagemaker_domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = ResourceEncryptedWithCMK()
