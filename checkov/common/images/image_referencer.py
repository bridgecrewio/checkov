from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Iterable
from typing import cast, Any

import docker


class Image:
    def __init__(self, file_path: str, name: str, start_line: int, end_line: int) -> None:
        """

        :param file_path: example: 'checkov/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml'
        :param name: example: 'node:14.16'
        :param image_id: example: 'sha256:6a353e22ce'
        :param start_line: example: 8
        :param end_line: example: 16
        """
        self.end_line = end_line
        self.start_line = start_line
        self.name = name
        self.file_path = file_path

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.file_path, self.name, self.start_line, self.end_line))


class ImageReferencer:
    @abstractmethod
    def is_workflow_file(self, file_path: str) -> bool:
        """

        :param file_path: path of file to validate if it is a file that contains might images (example: CI workflow file)
        :return: True if contains images

        """
        return False

    @abstractmethod
    def get_images(self, file_path: str) -> Iterable[Image]:
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected
        :return: List of container images objects mentioned in the file.
        """
        return []

    @staticmethod
    def inspect(image_name: str) -> str:
        """

        :param image_name: name of the image to be inspected locally using a "docker inspect X". If image does not exist try to pull it locally.
        :return: short image id sha that is inspected. In case inspect has failed None will be returned.
        """
        try:
            logging.info("Inspecting docker image {}".format(image_name))
            client = docker.from_env()
            try:
                image = client.images.get(image_name)
            except Exception:
                image = client.images.pull(image_name)
                return cast(str, image.short_id)
            return cast(str, image.short_id)
        except Exception:
            logging.debug(f"failed to pull docker image={image_name}", exc_info=True)
            return ""
