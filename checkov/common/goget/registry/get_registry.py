import logging
import requests
import os

from checkov.common.goget.base_getter import BaseGetter
from checkov.common.util.file_utils import extract_tar_archive


class RegistryGetter(BaseGetter):
    def __init__(self, url: str, create_clone_and_result_dirs: bool = False) -> None:
        self.logger = logging.getLogger(__name__)
        self.create_clone_and_res_dirs = create_clone_and_result_dirs
        super().__init__(url)

    def do_get(self) -> str:
        # get dest dir
        download_path = os.path.join(self.temp_dir, 'module_source.tar.gz')
        # download zip
        dest_path = os.path.dirname(download_path)
        with requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            os.makedirs(dest_path, exist_ok=True)
            with open(download_path, 'wb+') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        # extract
        extract_tar_archive(source_path=download_path, dest_path=dest_path)
        os.remove(download_path)

        return dest_path
