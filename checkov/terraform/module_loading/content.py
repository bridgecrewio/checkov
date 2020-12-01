import tempfile
from typing import Optional, Union


class ModuleContent(object):
    def __init__(self, dir: Optional[Union[tempfile.TemporaryDirectory, str]], next_url=None, failed_url=None) -> None:
        self.dir = dir.replace('//', '/') if dir else None
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

    def cleanup(self):
        """
Clean up any temporary resources, if applicable.
        """
        if isinstance(self.dir, tempfile.TemporaryDirectory):
            self.dir.cleanup()

    def __repr__(self) -> str:
        return self.path()

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        self.cleanup()