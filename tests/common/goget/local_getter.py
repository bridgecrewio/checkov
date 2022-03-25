import logging

from checkov.common.goget.base_getter import BaseGetter


class LocalGetter(BaseGetter):
    def __init__(self, url):
        self.logger = logging.getLogger(__name__)
        super().__init__(url)

    def do_get(self):

        return self.temp_dir
