import logging
import shutil
from git import Repo

from checkov.common.goget.base_getter import BaseGetter


class GitGetter(BaseGetter):
    def __init__(self, url):
        self.logger = logging.getLogger(__name__)
        super().__init__(url)

    def do_get(self):
        clone_dir = self.temp_dir + "/clone/"
        result_dir = self.temp_dir + "/result/"


        if ".git//" in self.url:
            git_url, internal_dir = self.url.split(".git//")
            git_url = git_url + ".git"
            self.logger.debug("cloning {} to {}".format(git_url,clone_dir))
            Repo.clone_from(git_url, clone_dir)

            shutil.copytree(clone_dir + internal_dir, result_dir)
        else:
            self.logger.debug("cloning {} to {}".format(self.url,clone_dir))
            Repo.clone_from(self.url, clone_dir)
            shutil.copytree(clone_dir, result_dir)
        return result_dir

