import os
from unittest import mock

import pytest
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.aws import AwsTerraformProvider
from tests.graph_utils.utils import GRAPH_FRAMEWORKS, set_graph_by_graph_framework, \
    add_vertices_to_graph_by_graph_framework


@mock.patch.dict(os.environ, {"BC_ROOT_DIR": "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src"})
@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources_with_external_module(graph_framework):
    # given
    resource = {
        "file_path_": "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_job_definition.batch.tf",
        "__end_line__": 8,
        "__start_line__": 1,
        "container_definitions": [
            {
                "name": "first",
                "image": "nginx",
                "cpu": 10,
                "memory": 512,
                "essential": True,
                "portMappings": [{"containerPort": 80, "hostPort": 80}],
            },
            {
                "name": "second",
                "image": "python:3.9-alpine",
                "cpu": 10,
                "memory": 256,
                "essential": True,
                "portMappings": [{"containerPort": 443, "hostPort": 443}],
            },
        ],
        "resource_type": "aws_ecs_task_definition",
        "module_dependency_": "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf",
        "module_dependency_num_": "0",
        "id_": "aws_batch_job_definition.batch",
    }
    module_resource = {
        "block_name_": "batch",
        "block_type_": "module",
        "file_path_": "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf",
        "config_": {
            "batch": {
                "__end_line__": 21,
                "__resolved__": [
                    "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_compute_environment.batch.tf[/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf#0]",
                    "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_job_definition.batch.tf[/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf#0]",
                    "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_job_queue.batch.tf[/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf#0]",
                    "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_scheduling_policy.pike.tf[/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf#0]",
                    "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/outputs.tf[/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf#0]",
                    "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/variables.tf[/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/example/examplea/module.batch.tf#0]"
                ],
                "__start_line__": 1,
            }
        },
        "id": "5c440d2a1a5c656290cdf8f98e1d893b1c08f7d7bb7cb93ff97a1884b83c18cc"
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)
    add_vertices_to_graph_by_graph_framework(graph_framework, module_resource, graph, 2, 'batch', 'module')

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        aws_provider = AwsTerraformProvider(graph_connector=graph)
        images = aws_provider.extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path='/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_job_definition.batch.tf',
            name="nginx",
            start_line=1,
            end_line=8,
            related_resource_id='/aws_batch_job_definition.batch.tf:module.batch.aws_batch_job_definition.batch'
        ),
        Image(
            file_path='/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src/aws_batch_job_definition.batch.tf',
            name="python:3.9-alpine",
            start_line=1,
            end_line=8,
            related_resource_id='/aws_batch_job_definition.batch.tf:module.batch.aws_batch_job_definition.batch'
        ),
    ]


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources(graph_framework):
    # given
    resource = {
        "file_path_": "/ecs.tf",
        "__end_line__": 31,
        "__start_line__": 1,
        "container_definitions": [
            {
                "name": "first",
                "image": "nginx",
                "cpu": 10,
                "memory": 512,
                "essential": True,
                "portMappings": [{"containerPort": 80, "hostPort": 80}],
            },
            {
                "name": "second",
                "image": "python:3.9-alpine",
                "cpu": 10,
                "memory": 256,
                "essential": True,
                "portMappings": [{"containerPort": 443, "hostPort": 443}],
            },
        ],
        "resource_type": "aws_ecs_task_definition",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        aws_provider = AwsTerraformProvider(graph_connector=graph)
        images = aws_provider.extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/ecs.tf",
            name="nginx",
            start_line=1,
            end_line=31,
            related_resource_id='/ecs.tf:None'
        ),
        Image(
            file_path="/ecs.tf",
            name="python:3.9-alpine",
            start_line=1,
            end_line=31,
            related_resource_id='/ecs.tf:None'
        ),
    ]


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources_with_no_image(graph_framework):
    # given
    resource = {
        "file_path_": "/ecs.tf",
        "__end_line__": 31,
        "__start_line__": 1,
        "container_definitions": [
            {
                "name": "first",
                "cpu": 10,
                "memory": 512,
                "essential": True,
                "portMappings": [{"containerPort": 80, "hostPort": 80}],
            },
        ],
        "resource_type": "aws_ecs_task_definition",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        aws_provider = AwsTerraformProvider(graph_connector=graph)
        images = aws_provider.extract_images_from_resources()

    # then
    assert not images
