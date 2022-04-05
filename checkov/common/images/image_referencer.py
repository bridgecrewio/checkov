from abc import abstractmethod

import docker


class ImageReferencer:
    @abstractmethod
    def is_workflow_file(self, f):
        pass

    @abstractmethod
    def get_images(self, f):
        pass

    def build_image(self, f, buildargs):
        try:
            client = docker.from_env()
            image = client.images.build(dockerfile=f, buildargs=buildargs)
            return image.id
        except Exception:
            return None

    def pull_image(self, image_name):
        try:
            client = docker.from_env()
            image = client.images.pull(image_name)
            return image.short_id
        except Exception:
            return None
