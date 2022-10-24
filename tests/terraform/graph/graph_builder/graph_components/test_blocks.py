from unittest import TestCase
import os

from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestBlocks(TestCase):
    def test_update_inner_attribute_1(self):
        config = {
            "aws_security_group": {
                "test": {
                    "name": ["test"],
                    "vpc_id": ["${aws_vpc.vpc_main.id}"],
                    "tags": [{"Name": "test"}],
                    "description": ["test - Elasticsearch Cluster"],
                    "ingress": [
                        {
                            "from_port": [443],
                            "to_port": [443],
                            "protocol": ["tcp"],
                            "security_groups": [
                                ["${aws_security_group.test.id}", "${data.aws_security_group.test.id}"]
                            ],
                        }
                    ],
                }
            }
        }

        block = TerraformBlock(
            name="aws_security_group.test",
            config=config,
            path="test_path",
            block_type=BlockType.RESOURCE,
            attributes=config["aws_security_group"]["test"],
        )

        block.update_inner_attribute(
            attribute_key="ingress.security_groups.0", nested_attributes=block.attributes, value_to_update="sg-0"
        )
        block.update_inner_attribute(
            attribute_key="ingress.security_groups.1", nested_attributes=block.attributes, value_to_update="sg-1"
        )

        self.assertEqual(
            "sg-0",
            block.attributes["ingress.security_groups.0"],
            f"failed to update ingress.security_groups.0, got {block.attributes['ingress.security_groups.0']}",
        )
        self.assertEqual(
            "sg-1",
            block.attributes["ingress.security_groups.1"],
            f"failed to update ingress.security_groups.1, got {block.attributes['ingress.security_groups.1']}",
        )
        self.assertEqual(
            "sg-0",
            block.attributes["ingress"]["security_groups"][0],
            f"failed to update block.attributes['ingress']['security_groups'][0], got {block.attributes['ingress']['security_groups'][0]}",
        )
        self.assertEqual(
            "sg-1",
            block.attributes["ingress"]["security_groups"][1],
            f"failed to update block.attributes['ingress']['security_groups'][1], got {block.attributes['ingress']['security_groups'][1]}",
        )

    def test_update_inner_attribute_2(self):
        config = {
            "aws_security_group": {
                "test": {
                    "name": ["test"],
                    "vpc_id": ["${aws_vpc.vpc_main.id}"],
                    "ingress": [
                        {
                            "from_port": [53],
                            "to_port": [53],
                            "protocol": ["udp"],
                            "security_groups": [
                                [
                                    "${data.test1.id}",
                                    "${data.test2.id}",
                                    "${data.test3.id}",
                                    "${data.test4.id}",
                                    "${data.test5.id}",
                                    "${data.test6.id}",
                                ]
                            ],
                            "cidr_blocks": [["test1", "${var.test2}", "${var.test4}"]],
                        },
                        {
                            "from_port": [53],
                            "to_port": [53],
                            "protocol": ["tcp"],
                            "security_groups": [
                                [
                                    "${data.test1.id}",
                                    "${data.test2.id}",
                                    "${data.test3.id}",
                                    "${data.test4.id}",
                                    "${data.test5.id}",
                                    "${data.test6.id}",
                                ]
                            ],
                            "cidr_blocks": [["test", "${var.test}", "${var.v3}"]],
                        },
                    ],
                }
            }
        }

        block = TerraformBlock(
            name="aws_security_group.test",
            config=config,
            path="test_path",
            block_type=BlockType.RESOURCE,
            attributes=config["aws_security_group"]["test"],
        )

        block.update_inner_attribute(
            attribute_key="ingress.0.cidr_blocks.1", nested_attributes=block.attributes, value_to_update="sg-1"
        )

        self.assertEqual(
            "sg-1",
            block.attributes["ingress.0.cidr_blocks.1"],
            f"failed to update ingress.0.cidr_blocks.1, got {block.attributes['ingress.0.cidr_blocks.1']}",
        )
        self.assertEqual(
            "sg-1",
            block.attributes["ingress"][0]["cidr_blocks"][1],
            f"failed to update block.attributes['ingress'][0]['cidr_blocks'][1], got {block.attributes['ingress'][0]['cidr_blocks'][1]}",
        )

    def test_update_inner_attribute_3(self):
        config = {
            "aws_iam_policy_document": {
                "vcs_webhook_step_function_execution_policy": {
                    "statement": [
                        {
                            "actions": [["events:DescribeRule", "events:PutRule", "events:PutTargets"]],
                            "effect": ["Allow"],
                            "resources": [
                                [
                                    "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                                    "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
                                ]
                            ],
                        },
                        {
                            "actions": [["states:StartExecution"]],
                            "effect": ["Allow"],
                            "resources": [
                                [
                                    "arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:${module.consts.bc_checkov_scanner_step_function_name}*"
                                ]
                            ],
                        },
                        {
                            "actions": [["lambda:InvokeFunction"]],
                            "effect": ["Allow"],
                            "resources": [
                                "${formatlist(\"%s%s\",\"arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:\",concat(['${local.vcs_webhook_lambda_name}', '${local.customer_api_lambda}']))}"
                            ],
                        },
                    ]
                }
            }
        }
        block = TerraformBlock(
            name="aws_iam_policy_document.vcs_webhook_step_function_execution_policy",
            config=config,
            path="test_path",
            block_type=BlockType.DATA,
            attributes=config["aws_iam_policy_document"]["vcs_webhook_step_function_execution_policy"],
        )
        block.update_inner_attribute(
            attribute_key="statement.1.resources.0",
            nested_attributes={
                "statement": [
                    {
                        "actions": ["events:DescribeRule", "events:PutRule", "events:PutTargets"],
                        "effect": "Allow",
                        "resources": [
                            "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                            "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
                        ],
                    },
                    {
                        "actions": "states:StartExecution",
                        "effect": "Allow",
                        "resources": "arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:bc-vcs-scanner-sfn*",
                    },
                    {
                        "actions": "lambda:InvokeFunction",
                        "effect": "Allow",
                        "resources": "${formatlist(\"%s%s\",\"arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:\",concat(['${local.vcs_webhook_lambda_name}', '${local.customer_api_lambda}']))}",
                    },
                ],
                "statement.0": {
                    "actions": ["events:DescribeRule", "events:PutRule", "events:PutTargets"],
                    "effect": "Allow",
                    "resources": [
                        "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                        "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
                    ],
                },
                "statement.0.actions": ["events:DescribeRule", "events:PutRule", "events:PutTargets"],
                "statement.0.actions.0": "events:DescribeRule",
                "statement.0.actions.1": "events:PutRule",
                "statement.0.actions.2": "events:PutTargets",
                "statement.0.effect": "Allow",
                "statement.0.resources": [
                    "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                    "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
                ],
                "statement.0.resources.0": "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                "statement.0.resources.1": "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
                "statement.1": {
                    "resources": "arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:bc-vcs-scanner-sfn*"
                },
                "statement.1.actions": "states:StartExecution",
                "statement.1.actions.0": "states:StartExecution",
                "statement.1.effect": "Allow",
                "statement.1.resources": "arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:bc-vcs-scanner-sfn*",
                "statement.1.resources.0": "arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:bc-vcs-scanner-sfn*",
                "statement.2": {
                    "actions": "lambda:InvokeFunction",
                    "effect": "Allow",
                    "resources": "${formatlist(\"%s%s\",\"arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:\",concat(['${local.vcs_webhook_lambda_name}', '${local.customer_api_lambda}']))}",
                },
                "statement.2.actions": "lambda:InvokeFunction",
                "statement.2.actions.0": "lambda:InvokeFunction",
                "statement.2.effect": "Allow",
                "statement.2.resources": "${formatlist(\"%s%s\",\"arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:\",concat(['${local.vcs_webhook_lambda_name}', '${local.customer_api_lambda}']))}",
            },
            value_to_update="arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:bc-vcs-scanner-sfn*",
        )
        self.assertIn(
            block.attributes["statement.0.resources.1"],
            [
                "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
            ],
        )
        self.assertIn(
            block.attributes["statement.0.resources.0"],
            [
                "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForECSTaskRule",
                "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
            ],
        )

    def test_update_complex_key(self):
        config = {
            "labels": [
                {
                    "app.kubernetes.io/name": "${local.name}",
                    "app.kubernetes.io/instance": "hpa",
                    "app.kubernetes.io/version": "1.0.0",
                    "app.kubernetes.io/managed-by": "terraform",
                }
            ]
        }
        attributes = {
            "labels": {
                "app.kubernetes.io/name": "${local.name}",
                "app.kubernetes.io/instance": "hpa",
                "app.kubernetes.io/version": "1.0.0",
                "app.kubernetes.io/managed-by": "terraform",
            },
            "labels.app.kubernetes.io/name": "${local.name}",
            "labels.app.kubernetes.io/instance": "hpa",
            "labels.app.kubernetes.io/version": "1.0.0",
            "labels.app.kubernetes.io/managed-by": "terraform",
        }
        block = TerraformBlock(
            name="test_local_name", config=config, path="", block_type=BlockType.LOCALS, attributes=attributes
        )

        block.update_inner_attribute(
            attribute_key="labels.app.kubernetes.io/name", nested_attributes=attributes, value_to_update="dummy value"
        )
        self.assertEqual("dummy value", block.attributes["labels.app.kubernetes.io/name"])

    def test_update_complex_key2(self):
        config = {}
        attributes = {
            "var.owning_account": {
                "route_to": None,
                "route_to_cidr_blocks": "${local.allowed_cidrs}",
                "static_routes": None,
                "subnet_ids": "${local.own_vpc.private_subnet_ids}",
                "subnet_route_table_ids": "${local.own_vpc.private_route_table_ids}",
                "transit_gateway_vpc_attachment_id": None,
                "vpc_cidr": "${local.own_vpc.vpc_cidr}",
                "vpc_id": "${local.own_vpc.vpc_id}",
            }
        }
        block = TerraformBlock(
            name="test_local_name", config=config, path="", block_type=BlockType.LOCALS, attributes=attributes
        )
        value_to_update = "test"
        block.update_inner_attribute(
            attribute_key="var.owning_account.vpc_cidr", nested_attributes=attributes, value_to_update=value_to_update
        )
        self.assertDictEqual(
            {"var.owning_account": block.attributes["var.owning_account"]},
            {
                "var.owning_account": {
                    "route_to": None,
                    "route_to_cidr_blocks": "${local.allowed_cidrs}",
                    "static_routes": None,
                    "subnet_ids": "${local.own_vpc.private_subnet_ids}",
                    "subnet_route_table_ids": "${local.own_vpc.private_route_table_ids}",
                    "transit_gateway_vpc_attachment_id": None,
                    "vpc_cidr": "test",
                    "vpc_id": "${local.own_vpc.vpc_id}",
                }
            },
        )

    def test_update_inner_attribute_bad_index(self):
        config = {"aws_security_group": {"test": {}}}

        nested_attributes = {
            "provisioner/remote-exec.connection": {"private_key": "${file(var.ssh_key_path)}", "user": "ec2-user"},
            "provisioner/remote-exec.connection.private_key": "${file(var.ssh_key_path)}",
            "provisioner/remote-exec.connection.user": "ec2-user",
            "provisioner/remote-exec.inline": ["command"],
            "provisioner/remote-exec.inline.0": "command0",
            "provisioner/remote-exec.inline.1": "command1",
            "provisioner/remote-exec.inline.2": "command2",
            "provisioner/remote-exec.inline.3": "command3",
            "provisioner/remote-exec.inline.4": "command4",
        }
        block = TerraformBlock(
            name="aws_security_group.test",
            config=config,
            path="test_path",
            block_type=BlockType.RESOURCE,
            attributes=nested_attributes,
        )

        block.update_inner_attribute(
            attribute_key="provisioner/remote-exec.inline.3",
            nested_attributes=nested_attributes,
            value_to_update="new_command_3",
        )

        self.assertEqual(
            "new_command_3",
            block.attributes["provisioner/remote-exec.inline.3"],
            f"failed to update provisioner/remote-exec.inline.3, got {block.attributes['provisioner/remote-exec.inline.3']}",
        )

    def test_update_inner_attribute_bad_map_entry(self):
        config = {"aws_security_group": {"test": {}}}

        nested_attributes = {
            "triggers": {
                "change_endpoint_name": '${md5("my_dev_endpoint")}',
                "change_extra_jars_s3_path": "${md5()}",
                "change_extra_python_libs_s3_path": "${md5()}",
                "change_number_of_nodes": '${md5("2")}',
                "change_public_keys": '${md5("${var.glue_endpoint_public_keys}")}',
                "change_region": '${md5("us-east-1")}',
                "change_role": '${md5("arn:aws:iam::111111111111:role/my_role")}',
                "change_security_configuration": "${md5()}",
                "change_security_group_ids": '${md5("${var.glue_endpoint_security_group_ids}")}',
                "change_subnet_id": "${md5()}",
            },
            "provisioner/local-exec": {
                "command": "echo 'info: destroy ignored because part of apply'",
                "when": "destroy",
            },
            "provisioner/local-exec.command": "echo 'info: destroy ignored because part of apply'",
            "provisioner/local-exec.environment": {
                "endpoint_name": "${var.glue_endpoint_name}",
                "extra_jars_s3_path": "${var.glue_endpoint_extra_jars_libraries}",
                "extra_python_libs_s3_path": "${var.glue_endpoint_extra_python_libraries}",
                "number_of_nodes": "${var.glue_endpoint_number_of_dpus}",
                "public_keys": '${join(",",var.glue_endpoint_public_keys)}',
                "region": "${var.aws_region}",
                "role_arn": "${var.glue_endpoint_role}",
                "security_configuration": "${var.glue_endpoint_security_configuration}",
                "security_group_ids": '${join(",",var.glue_endpoint_security_group_ids)}',
                "subnet_id": "${var.glue_endpoint_subnet_id}",
            },
            "provisioner/local-exec.environment.endpoint_name": "my_dev_endpoint",
            "provisioner/local-exec.environment.extra_jars_s3_path": "",
            "provisioner/local-exec.environment.extra_python_libs_s3_path": "",
            "provisioner/local-exec.environment.number_of_nodes": 2,
            "provisioner/local-exec.environment.public_keys": '${join(",",var.glue_endpoint_public_keys)}',
            "provisioner/local-exec.environment.region": "us-east-1",
            "provisioner/local-exec.environment.role_arn": "arn:aws:iam::111111111111:role/my_role",
            "provisioner/local-exec.environment.security_configuration": "",
            "provisioner/local-exec.environment.security_group_ids": '${join(",",var.glue_endpoint_security_group_ids)}',
            "provisioner/local-exec.environment.subnet_id": "",
            "provisioner/local-exec.when": "destroy",
            "resource_type": ["null_resource"],
            "triggers.change_endpoint_name": '${md5("my_dev_endpoint")}',
            "triggers.change_extra_jars_s3_path": "${md5()}",
            "triggers.change_extra_python_libs_s3_path": "${md5()}",
            "triggers.change_number_of_nodes": '${md5("2")}',
            "triggers.change_public_keys": '${md5("${var.glue_endpoint_public_keys}")}',
            "triggers.change_region": '${md5("us-east-1")}',
            "triggers.change_role": '${md5("arn:aws:iam::111111111111:role/my_role")}',
            "triggers.change_security_configuration": "${md5()}",
            "triggers.change_security_group_ids": '${md5("${var.glue_endpoint_security_group_ids}")}',
            "triggers.change_subnet_id": "${md5()}",
        }
        block = TerraformBlock(
            name="null_resource.glue_endpoint_apply",
            config=config,
            path="test_path",
            block_type=BlockType.RESOURCE,
            attributes=nested_attributes,
        )
        attribute_key = "provisioner/local-exec.environment.security_configuration"
        block.update_inner_attribute(
            attribute_key=attribute_key, nested_attributes=nested_attributes, value_to_update=""
        )

        self.assertEqual(
            "",
            block.attributes[attribute_key],
            f"failed to update provisioner/remote-exec.inline.3, got {block.attributes[attribute_key]}",
        )

    def test_malformed_provider_block(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../../resources/malformed_provider')

        graph_manager = TerraformGraphManager(db_connector=NetworkxConnector())
        graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir)

        expected_num_of_provider_nodes = 0
        vertices_by_block_type = graph.vertices_by_block_type
        self.assertEqual(expected_num_of_provider_nodes, len(vertices_by_block_type[BlockType.PROVIDER]))
