import tempfile
from types import TracebackType
from typing import Optional, Union, Type


class ModuleContent(object):
    def __init__(
        self,
        dir: Optional[Union[tempfile.TemporaryDirectory, str]],
        next_url: Optional[str] = None,
        failed_url: Optional[str] = None,
    ) -> None:
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

    def __enter__(self) -> "ModuleContent":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.cleanup()
