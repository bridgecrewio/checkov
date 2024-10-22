from __future__ import annotations

import tempfile
from typing import Optional, Union


class ModuleContent:
    def __init__(
        self,
        dir: Optional[Union[tempfile.TemporaryDirectory[str], str]],
        next_url: Optional[str] = None,
        failed_url: Optional[str] = None,
    ) -> None:
        if isinstance(dir, tempfile.TemporaryDirectory):
            self.dir: tempfile.TemporaryDirectory[str] | str | None = dir
        else:
            self.dir = dir.replace("//", "/") if dir else None
        self.next_url = next_url
        self.failed_url = failed_url

    def loaded(self) -> bool:
        """
Indicates whether or not the module content could be loaded. If False is returned, `path()` will return None.
        """
        return self.dir is not None

    def path(self) -> Optional[str]:
        """
Returns the directory path containing module resources.
        """
        if isinstance(self.dir, tempfile.TemporaryDirectory):
            return self.dir.name
        else:
            return self.dir

    def cleanup(self) -> None:
        """
Clean up any temporary resources, if applicable.
        """
        if isinstance(self.dir, tempfile.TemporaryDirectory):
            self.dir.cleanup()

    def __repr__(self) -> str:
        return self.path() or ""
