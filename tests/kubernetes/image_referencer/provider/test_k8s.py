from unittest import mock

import pytest
from checkov.kubernetes.image_referencer.provider.k8s import KubernetesProvider
from checkov.common.images.image_referencer import Image
from tests.graph_utils.utils import GRAPH_FRAMEWORKS, set_graph_by_graph_framework, \
    add_vertices_to_graph_by_graph_framework


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources(graph_framework):
    # given
    resource = {
        "file_path_": "/pod.yaml",
        "__endline__": 16,
        "__startline__": 1,
        "spec": {
            "initContainers": [
                {
                    "name": "init-sysctl",
                    "image": "busybox",
                },
            ],
            "containers": [
                {
                    "name": "test-container",
                    "image": "nginx",
                },
            ],
        },
        "resource_type": "Pod",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        provider = KubernetesProvider(graph_connector=graph)
        images = provider.extract_images_from_resources()

    # then
    assert len(images) == 2
    nginx_image = Image(
            file_path="/pod.yaml",
            name="nginx",
            start_line=1,
            end_line=16,
            related_resource_id="/pod.yaml:None",
        )
    busybox_image = Image(file_path="/pod.yaml", name="busybox", start_line=1, end_line=16,
                          related_resource_id="/pod.yaml:None")
    assert nginx_image in images
    assert busybox_image in images


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources_with_no_image(graph_framework):
    # given
    resource = {
        "file_path_": "/pod.yaml",
        "__endline__": 16,
        "__startline__": 1,
        "spec": {
            "containers": [
                {
                    "name": "test-container",
                },
            ],
        },
        "resource_type": "Pod",
    }
    graph = set_graph_by_graph_framework(graph_framework)
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph)

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        provider = KubernetesProvider(graph_connector=graph)
        images = provider.extract_images_from_resources()

    # then
    assert not images
