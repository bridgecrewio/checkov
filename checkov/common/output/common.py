from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ImageDetails:
    distro: str = ''
    distro_release: str = ''
    image_id: str = ''
    package_types: dict[str, str] = field(default_factory=dict)
