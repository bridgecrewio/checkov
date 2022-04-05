import logging
from abc import abstractmethod

import docker


class ImageReferencer:

    @abstractmethod
    def is_workflow_file(self, f):
        pass

    @abstractmethod
    def get_images(self, f):
        pass

    def pull_image(self, image_name):
        try:
            client = docker.from_env()
            image = client.images.pull(image_name)
            return image.short_id
        except Exception as e:
            logging.debug("failed to pull docker image={}", image_name)
            logging.debug(e)
            return None
