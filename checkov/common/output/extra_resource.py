from __future__ import annotations

from typing import Any


class ExtraResource:
    __slots__ = ("file_abs_path", "file_path", "resource", "vulnerability_details")

    def __init__(
        self, file_abs_path: str, file_path: str, resource: str, vulnerability_details: dict[str, Any] | None = None
    ) -> None:
        self.file_abs_path = file_abs_path
        self.file_path = file_path
        self.resource = resource  # resource ID
        self.vulnerability_details = vulnerability_details  # only set for SCA resources

    def __lt__(self, other: ExtraResource) -> bool:
        return (self.file_abs_path, self.resource) < (other.file_abs_path, other.resource)
