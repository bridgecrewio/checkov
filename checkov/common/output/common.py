from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SCADetails:
    package_types: dict[str, str] = field(default_factory=dict)


@dataclass
class ImageDetails(SCADetails):
    distro: str = ''
    distro_release: str = ''
    image_id: str = ''
    name: str | None = ''
    related_resource_id: str | None = ''
