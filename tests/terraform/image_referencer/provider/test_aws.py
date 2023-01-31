import os
from unittest import mock

import igraph
import pytest
from networkx import DiGraph

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.aws import AwsTerraformProvider


@mock.patch.dict(os.environ, {"BC_ROOT_DIR": "/tmp/checkov/cshayner/cshayner/terraform-aws-batch/master/src"})
@pytest.mark.parametrize("graph_framework", ['NETWORKX', 'IGRAPH'])
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

    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=resource[
                CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in resource else None,
            attr=resource,
        )
        graph.add_vertex(
            name='batch',
            block_type_='module',
            resource_type=module_resource[
                CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in module_resource else None,
            attr=module_resource,
        )
    else:
        graph = DiGraph()
        graph.add_node(1, **resource)
        graph.add_node(2, **module_resource)

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


@pytest.mark.parametrize("graph_framework", ['NETWORKX', 'IGRAPH'])
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

    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=resource[
                CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in resource else None,
            attr=resource,
        )
    else:
        graph = DiGraph()
        graph.add_node(1, **resource)

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


@pytest.mark.parametrize("graph_framework", ['NETWORKX', 'IGRAPH'])
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
    if graph_framework == 'IGRAPH':
        graph = igraph.Graph()
        graph.add_vertex(
            name='1',
            block_type_='resource',
            resource_type=resource[
                CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in resource else None,
            attr=resource,
        )
    else:
        graph = DiGraph()
        graph.add_node(1, **resource)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        aws_provider = AwsTerraformProvider(graph_connector=graph)
        images = aws_provider.extract_images_from_resources()

    # then
    assert not images
