from unittest import mock

import pytest
from checkov.kubernetes.image_referencer.manager import KubernetesImageReferencerManager
from checkov.common.images.image_referencer import Image
from tests.graph_utils.utils import set_graph_by_graph_framework, GRAPH_FRAMEWORKS, \
    add_vertices_to_graph_by_graph_framework


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_extract_images_from_resources(graph_framework):
    # given
    resource = {
        "file_path_": "/pod.yaml",
        "__endline__": 16,
        "__startline__": 1,
        "spec": {
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
        images = KubernetesImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/pod.yaml",
            name="nginx",
            start_line=1,
            end_line=16,
            related_resource_id="/pod.yaml:None",
        ),
    ]


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_no_duplications_while_extracting_image_names(graph_framework):
    resource = {
        "file_path_": "/pod.yaml",
        "__endline__": 16,
        "__startline__": 1,
        "spec": {
            "initContainers": [
                {
                    "name": "test-container",
                    "image": "nginx",
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
    add_vertices_to_graph_by_graph_framework(graph_framework, resource, graph, 1, 'duplicated_image')
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        manager = KubernetesImageReferencerManager(graph_connector=graph)
        images = manager.extract_images_from_resources()
    assert len(images) == 1
    image = images[0]
    assert image.name == 'nginx'
