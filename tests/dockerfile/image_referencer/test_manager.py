from checkov.common.images.image_referencer import Image
from checkov.dockerfile.image_referencer.manager import DockerfileImageReferencerManager


def test_extract_images_from_resources():
    # given
    definitions = {
        "/Dockerfile": {
            "FROM": [
                {
                    "instruction": "FROM",
                    "startline": 0,
                    "endline": 0,
                    "content": "FROM php:7.1-apache\n",
                    "value": "php:7.1-apache",
                }
            ],
            "RUN": [
                {
                    "instruction": "RUN",
                    "startline": 2,
                    "endline": 2,
                    "content": "RUN apk --no-cache add nginx\n",
                    "value": "apk --no-cache add nginx",
                },
            ],
        },
    }

    # when
    images = DockerfileImageReferencerManager(definitions=definitions).extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/Dockerfile",
            name="php:7.1-apache",
            start_line=1,
            end_line=1,
            related_resource_id="/Dockerfile:/Dockerfile.FROM",
        ),
    ]
