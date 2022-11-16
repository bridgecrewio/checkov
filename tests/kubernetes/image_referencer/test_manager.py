from networkx import DiGraph

from checkov.kubernetes.image_referencer.manager import KubernetesImageReferencerManager
from checkov.common.images.image_referencer import Image


def test_extract_images_from_resources():
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
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
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
