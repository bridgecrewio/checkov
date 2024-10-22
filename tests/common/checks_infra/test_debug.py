from __future__ import annotations

from textwrap import dedent

import pytest
from _pytest.capture import CaptureFixture

from checkov.common.graph.checks_infra.debug import attribute_block, graph_check, connection_block
from checkov.common.graph.checks_infra.enums import Operators
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.env_vars_config import env_vars_config


@pytest.fixture
def enable_graph_debug():
    env_vars_config.EXPERIMENTAL_GRAPH_DEBUG = True
    yield
    env_vars_config.EXPERIMENTAL_GRAPH_DEBUG = False


def test_no_output_on_default(capfd: CaptureFixture[str]):
    # given/when
    graph_check(check_id="CKV_EXAMPLE_1", check_name="Example")

    # then
    assert not capfd.readouterr().out


def test_attribute_block(capfd: CaptureFixture[str], enable_graph_debug):
    # given
    resource_types = ["aws_s3_bucket"]
    attribute = "lifecycle_rule"
    operator = Operators.EXISTS
    value = None
    resource = {
        CustomAttributes.ID: "aws_s3_bucket.example",
        CustomAttributes.CONFIG: {
            "aws_s3_bucket": {
                "example": {
                    "__end_line__": 3,
                    "__start_line__": 1,
                    "bucket": ["example"],
                    "__address__": "aws_s3_bucket.example",
                }
            }
        },
    }
    status = "failed"

    # when
    attribute_block(
        resource_types=resource_types,
        attribute=attribute,
        operator=operator,
        value=value,
        resource=resource,
        status=status,
    )

    # then
    assert capfd.readouterr().out == dedent(
        """
        Evaluated block:
        
        - cond_type: attribute
          resource_types:
          - aws_s3_bucket
          attribute: lifecycle_rule
          operator: exists
        
        and got:
        
        Resource "aws_s3_bucket.example" failed:
        {
          "aws_s3_bucket": {
            "example": {
              "__end_line__": 3,
              "__start_line__": 1,
              "bucket": [
                "example"
              ],
              "__address__": "aws_s3_bucket.example"
            }
          }
        }
        """
    )


def test_connection_block(capfd: CaptureFixture[str], enable_graph_debug):
    # given
    resource_types = ["aws_s3_bucket"]
    connected_resource_types = ["aws_s3_bucket_lifecycle_configuration"]
    operator = Operators.EXISTS
    value = None
    passed_resources = [
        {
            CustomAttributes.ID: "aws_s3_bucket.good",
        },
        {
            CustomAttributes.ID: "aws_s3_bucket_lifecycle_configuration.good",
        },
    ]
    failed_resources = [
        {
            CustomAttributes.ID: "aws_s3_bucket.bad",
        }
    ]

    # when
    connection_block(
        resource_types=resource_types,
        connected_resource_types=connected_resource_types,
        operator=operator,
        passed_resources=passed_resources,
        failed_resources=failed_resources,
    )

    # then
    assert capfd.readouterr().out == dedent(
        """
        Evaluated blocks:
        
        - cond_type: connection
          resource_types:
          - aws_s3_bucket
          connected_resource_types:
          - aws_s3_bucket_lifecycle_configuration
          operator: exists
        
        and got:
        
        Passed resources: "aws_s3_bucket.good", "aws_s3_bucket_lifecycle_configuration.good"
        Failed resources: "aws_s3_bucket.bad"
        """
    )
