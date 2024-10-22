from typing import Any


class Image:
    attrs: dict[str, Any]
    @property
    def id(self) -> str: ...  # is actually defined in its parent class 'Model'
    @property
    def short_id(self) -> str: ...


class ImageCollection:
    def get(self, name: str) -> Image: ...
    def pull(self, repository: str, tag: str | None= ..., all_tags: bool = ..., **kwargs: Any) -> Image: ...
