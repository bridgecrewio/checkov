import logging
from abc import abstractmethod

import docker


class ImageReferencer:

    @abstractmethod
    def is_workflow_file(self, file_path: str) -> bool:
        """

        :param file_path: path of file to validate if it is a file that contains might images (example: CI workflow file)
        :return: True if contains images

        """
        return False

    @abstractmethod
    def get_images(self, file_path: str) -> [str]:
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected
        :return: List of container image short ids mentioned in the file.
        """
        return []

    def pull_image(self, image_name: str) -> str:
        """

        :param image_name: name of the image to be pulled locally using a "docker pull X" command
        :return: short image id sha that is pulled locally. In case pull has failed None will be returned.
        """
        try:
            logging.info("Pulling docker image {}", image_name)
            client = docker.from_env()
            image = client.images.pull(image_name)
            return image.short_id
        except Exception:
            logging.debug(f"failed to pull docker image={image_name}", exc_info=True)
            return ""
