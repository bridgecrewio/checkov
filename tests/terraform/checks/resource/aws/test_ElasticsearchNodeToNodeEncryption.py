import unittest

from checkov.terraform.checks.resource.aws.ElasticsearchNodeToNodeEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestElasticsearchNodeToNodeEncryption(unittest.TestCase):

    def test_unknown(self):
        resource_conf = {'count': ['${var.enabled ? 1 : 0}'], 'domain_name': ['${module.label.id}'],
                         'elasticsearch_version': ['${var.elasticsearch_version}'],
                         'advanced_options': ['${var.advanced_options}'], 'ebs_options': [
                {'ebs_enabled': ['${var.ebs_volume_size > 0 ? True : False}'],
                 'volume_size': ['${var.ebs_volume_size}'], 'volume_type': ['${var.ebs_volume_type}'],
                 'iops': ['${var.ebs_iops}']}],
                         'encrypt_at_rest': [{'enabled': [False], 'kms_key_id': ['${var.encrypt_at_rest_kms_key_id}']}],
                         'cluster_config': [{'instance_count': ['${var.foo}'], 'instance_type': ['${var.instance_type}'],
                                             'dedicated_master_enabled': ['${var.dedicated_master_enabled}'],
                                             'dedicated_master_count': ['${var.dedicated_master_count}'],
                                             'dedicated_master_type': ['${var.dedicated_master_type}'],
                                             'zone_awareness_enabled': ['${var.zone_awareness_enabled}'],
                                             'zone_awareness_config': [
                                                 {'availability_zone_count': ['${var.availability_zone_count}']}]}],
                         'vpc_options': [
                             {'security_group_ids': [['${join("",aws_security_group.default.*.id)}']],
                              'subnet_ids': ['${var.subnet_ids}']}], 'snapshot_options': [
                {'automated_snapshot_start_hour': ['${var.automated_snapshot_start_hour}']}],
                         'log_publishing_options': [
                             {'enabled': ['${var.log_publishing_index_enabled}'], 'log_type': ['INDEX_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_index_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_search_enabled}'], 'log_type': ['SEARCH_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_search_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_application_enabled}'],
                              'log_type': ['ES_APPLICATION_LOGS'], 'cloudwatch_log_group_arn': [
                                 '${var.log_publishing_application_cloudwatch_log_group_arn}']}],
                         'tags': ['${module.label.tags}'], 'depends_on': [['${aws_iam_service_linked_role.default}']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_failure(self):
        resource_conf = {'count': ['${var.enabled ? 1 : 0}'], 'domain_name': ['${module.label.id}'],
                         'elasticsearch_version': ['${var.elasticsearch_version}'],
                         'advanced_options': ['${var.advanced_options}'], 'ebs_options': [
                {'ebs_enabled': ['${var.ebs_volume_size > 0 ? True : False}'],
                 'volume_size': ['${var.ebs_volume_size}'], 'volume_type': ['${var.ebs_volume_type}'],
                 'iops': ['${var.ebs_iops}']}],
                         'encrypt_at_rest': [{'enabled': [False], 'kms_key_id': ['${var.encrypt_at_rest_kms_key_id}']}],
                         'cluster_config': [{'instance_count': [3], 'instance_type': ['${var.instance_type}'],
                                             'dedicated_master_enabled': ['${var.dedicated_master_enabled}'],
                                             'dedicated_master_count': ['${var.dedicated_master_count}'],
                                             'dedicated_master_type': ['${var.dedicated_master_type}'],
                                             'zone_awareness_enabled': ['${var.zone_awareness_enabled}'],
                                             'zone_awareness_config': [
                                                 {'availability_zone_count': ['${var.availability_zone_count}']}]}],
                         'node_to_node_encryption': [{'enabled': [False]}], 'vpc_options': [
                {'security_group_ids': [['${join("",aws_security_group.default.*.id)}']],
                 'subnet_ids': ['${var.subnet_ids}']}], 'snapshot_options': [
                {'automated_snapshot_start_hour': ['${var.automated_snapshot_start_hour}']}],
                         'log_publishing_options': [
                             {'enabled': ['${var.log_publishing_index_enabled}'], 'log_type': ['INDEX_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_index_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_search_enabled}'], 'log_type': ['SEARCH_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_search_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_application_enabled}'],
                              'log_type': ['ES_APPLICATION_LOGS'], 'cloudwatch_log_group_arn': [
                                 '${var.log_publishing_application_cloudwatch_log_group_arn}']}],
                         'tags': ['${module.label.tags}'], 'depends_on': [['${aws_iam_service_linked_role.default}']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_node_to_node_encryption_missing(self):
        resource_conf = {'count': ['${var.enabled ? 1 : 0}'], 'domain_name': ['${module.label.id}'],
                         'elasticsearch_version': ['${var.elasticsearch_version}'],
                         'advanced_options': ['${var.advanced_options}'], 'ebs_options': [
                {'ebs_enabled': ['${var.ebs_volume_size > 0 ? True : False}'],
                 'volume_size': ['${var.ebs_volume_size}'], 'volume_type': ['${var.ebs_volume_type}'],
                 'iops': ['${var.ebs_iops}']}],
                         'encrypt_at_rest': [{'enabled': [False], 'kms_key_id': ['${var.encrypt_at_rest_kms_key_id}']}],
                         'cluster_config': [{'instance_count': [3], 'instance_type': ['${var.instance_type}'],
                                             'dedicated_master_enabled': ['${var.dedicated_master_enabled}'],
                                             'dedicated_master_count': ['${var.dedicated_master_count}'],
                                             'dedicated_master_type': ['${var.dedicated_master_type}'],
                                             'zone_awareness_enabled': ['${var.zone_awareness_enabled}'],
                                             'zone_awareness_config': [
                                                 {'availability_zone_count': ['${var.availability_zone_count}']}]}],
                         'vpc_options': [
                             {'security_group_ids': [['${join("",aws_security_group.default.*.id)}']],
                              'subnet_ids': ['${var.subnet_ids}']}], 'snapshot_options': [
                {'automated_snapshot_start_hour': ['${var.automated_snapshot_start_hour}']}],
                         'log_publishing_options': [
                             {'enabled': ['${var.log_publishing_index_enabled}'], 'log_type': ['INDEX_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_index_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_search_enabled}'], 'log_type': ['SEARCH_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_search_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_application_enabled}'],
                              'log_type': ['ES_APPLICATION_LOGS'], 'cloudwatch_log_group_arn': [
                                 '${var.log_publishing_application_cloudwatch_log_group_arn}']}],
                         'tags': ['${module.label.tags}'], 'depends_on': [['${aws_iam_service_linked_role.default}']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'count': ['${var.enabled ? 1 : 0}'], 'domain_name': ['${module.label.id}'],
                         'elasticsearch_version': ['${var.elasticsearch_version}'],
                         'advanced_options': ['${var.advanced_options}'], 'ebs_options': [
                {'ebs_enabled': ['${var.ebs_volume_size > 0 ? True : False}'],
                 'volume_size': ['${var.ebs_volume_size}'], 'volume_type': ['${var.ebs_volume_type}'],
                 'iops': ['${var.ebs_iops}']}],
                         'encrypt_at_rest': [{'enabled': [True], 'kms_key_id': ['${var.encrypt_at_rest_kms_key_id}']}],
                         'cluster_config': [{'instance_count': [3], 'instance_type': ['${var.instance_type}'],
                                             'dedicated_master_enabled': ['${var.dedicated_master_enabled}'],
                                             'dedicated_master_count': ['${var.dedicated_master_count}'],
                                             'dedicated_master_type': ['${var.dedicated_master_type}'],
                                             'zone_awareness_enabled': ['${var.zone_awareness_enabled}'],
                                             'zone_awareness_config': [
                                                 {'availability_zone_count': ['${var.availability_zone_count}']}]}],
                         'node_to_node_encryption': [{'enabled': [True]}], 'vpc_options': [
                {'security_group_ids': [['${join("",aws_security_group.default.*.id)}']],
                 'subnet_ids': ['${var.subnet_ids}']}], 'snapshot_options': [
                {'automated_snapshot_start_hour': ['${var.automated_snapshot_start_hour}']}],
                         'log_publishing_options': [
                             {'enabled': ['${var.log_publishing_index_enabled}'], 'log_type': ['INDEX_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_index_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_search_enabled}'], 'log_type': ['SEARCH_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_search_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_application_enabled}'],
                              'log_type': ['ES_APPLICATION_LOGS'], 'cloudwatch_log_group_arn': [
                                 '${var.log_publishing_application_cloudwatch_log_group_arn}']}],
                         'tags': ['${module.label.tags}'], 'depends_on': [['${aws_iam_service_linked_role.default}']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_single_node(self):
        resource_conf = {'count': ['${var.enabled ? 1 : 0}'], 'domain_name': ['${module.label.id}'],
                         'elasticsearch_version': ['${var.elasticsearch_version}'],
                         'advanced_options': ['${var.advanced_options}'], 'ebs_options': [
                {'ebs_enabled': ['${var.ebs_volume_size > 0 ? True : False}'],
                 'volume_size': ['${var.ebs_volume_size}'], 'volume_type': ['${var.ebs_volume_type}'],
                 'iops': ['${var.ebs_iops}']}],
                         'encrypt_at_rest': [{'enabled': [True], 'kms_key_id': ['${var.encrypt_at_rest_kms_key_id}']}],
                         'cluster_config': [{'instance_count': [1], 'instance_type': ['${var.instance_type}'],
                                             'dedicated_master_enabled': ['${var.dedicated_master_enabled}'],
                                             'dedicated_master_count': ['${var.dedicated_master_count}'],
                                             'dedicated_master_type': ['${var.dedicated_master_type}'],
                                             'zone_awareness_enabled': ['${var.zone_awareness_enabled}'],
                                             'zone_awareness_config': [
                                                 {'availability_zone_count': ['${var.availability_zone_count}']}]}],
                         'node_to_node_encryption': [{'enabled': [False]}], 'vpc_options': [
                {'security_group_ids': [['${join("",aws_security_group.default.*.id)}']],
                 'subnet_ids': ['${var.subnet_ids}']}], 'snapshot_options': [
                {'automated_snapshot_start_hour': ['${var.automated_snapshot_start_hour}']}],
                         'log_publishing_options': [
                             {'enabled': ['${var.log_publishing_index_enabled}'], 'log_type': ['INDEX_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_index_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_search_enabled}'], 'log_type': ['SEARCH_SLOW_LOGS'],
                              'cloudwatch_log_group_arn': ['${var.log_publishing_search_cloudwatch_log_group_arn}']},
                             {'enabled': ['${var.log_publishing_application_enabled}'],
                              'log_type': ['ES_APPLICATION_LOGS'], 'cloudwatch_log_group_arn': [
                                 '${var.log_publishing_application_cloudwatch_log_group_arn}']}],
                         'tags': ['${module.label.tags}'], 'depends_on': [['${aws_iam_service_linked_role.default}']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
