from typing import Any

from .models.images import ImageCollection

class DockerClient:
    @classmethod
    def from_env(cls, **kwargs: Any) -> DockerClient: ...

    @property
    def images(self) -> ImageCollection: ...


from_env = DockerClient.from_env
