from networkx import DiGraph

from checkov.common.images.image_referencer import Image
from checkov.terraform.image_referencer.provider.gcp import GcpTerraformProvider


def extract_images_from_resources():
    # given
    resource = {
        "file_path_": "/cloud_run.tf",
        "__end_line__": 17,
        "__start_line__": 1,
        "template": {
            "spec": {
                "containers": {
                    "image": "gcr.io/cloudrun/hello",
                }
            }
        },
        "resource_type": "google_cloud_run_service",
    }
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    gcp_provider = GcpTerraformProvider(graph_connector=graph)
    images = gcp_provider.extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/cloud_run.tf",
            name="gcr.io/cloudrun/hello",
            start_line=1,
            end_line=17,
            related_resource_id="/cloud_run.tf:None",
        ),
    ]


def test_extract_images_from_resources_with_no_image():
    # given
    resource = {
        "file_path_": "/cloud_run.tf",
        "__end_line__": 17,
        "__start_line__": 1,
        "template": {
            "spec": {
                "containers": {
                    "working_dir": "/tmp",
                }
            }
        },
        "resource_type": "google_cloud_run_service",
    }
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    gcp_provider = GcpTerraformProvider(graph_connector=graph)
    images = gcp_provider.extract_images_from_resources()

    # then
    assert not images
