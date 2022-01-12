import os
import uuid
from abc import abstractmethod
from typing import Optional


class BaseGetter(object):
    def __init__(self, url: str) -> None:
        self.url = url
        self.temp_dir: Optional[str] = None

    def get(self) -> str:
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, str((uuid.uuid4()))[:8] + "_checks")
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        self.temp_dir = final_directory
        return self.do_get()

    @abstractmethod
    def do_get(self) -> str:
        raise NotImplementedError()
