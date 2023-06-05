from checkov.common.images.image_referencer import Image
from checkov.dockerfile.image_referencer.provider import DockerfileProvider


def test_extract_images_from_resources():
    # given
    definitions = {
        "/Dockerfile": {
            "FROM": [
                {
                    "instruction": "FROM",
                    "startline": 0,
                    "endline": 0,
                    "content": "FROM maven:3.8-openjdk-17-slim AS build\n",
                    "value": "maven:3.8-openjdk-17-slim AS build",
                },
                {
                    "instruction": "FROM",
                    "startline": 4,
                    "endline": 4,
                    "content": "FROM amazonlinux:2 AS run\n",
                    "value": "amazonlinux:2",
                },
            ],
            "RUN": [
                {
                    "instruction": "RUN",
                    "startline": 2,
                    "endline": 2,
                    "content": "RUN apt-get install -y curl\n",
                    "value": "apt-get install -y curl",
                },
            ],
        },
    }

    # when
    provider = DockerfileProvider(definitions=definitions)
    images = provider.extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/Dockerfile",
            name="amazonlinux:2",
            start_line=5,
            end_line=5,
            related_resource_id="/Dockerfile:/Dockerfile.FROM",
        ),
    ]


def test_extract_images_from_resources_with_no_image():
    # given
    definitions = {
        "/Dockerfile": {
            "RUN": [
                {
                    "instruction": "RUN",
                    "startline": 2,
                    "endline": 2,
                    "content": "RUN apt-get install -y curl\n",
                    "value": "apt-get install -y curl",
                },
            ],
        },
    }

    # when
    provider = DockerfileProvider(definitions=definitions)
    images = provider.extract_images_from_resources()

    # then
    assert not images
