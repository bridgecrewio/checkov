import logging
import re
import shutil

TAG_PATTERN = re.compile(r'\?(ref=)(?P<tag>v\d+.\d+.\d+)')
try:
    from git import Repo
    git_import_error = None
except ImportError as e:
    git_import_error = e


from checkov.common.goget.base_getter import BaseGetter


class GitGetter(BaseGetter):
    def __init__(self, url, create_clone_and_result_dirs=True):
        self.logger = logging.getLogger(__name__)
        self.create_clone_and_res_dirs = create_clone_and_result_dirs
        self.tag = ''

        search_tag = re.search(TAG_PATTERN, url)
        if search_tag:
            self.tag = search_tag.groupdict().get('tag')
        url = re.sub(TAG_PATTERN, '', url)

        super().__init__(url)

    def do_get(self):
        if git_import_error is not None:
            raise ImportError("Unable to load git module (is the git executable available?)") \
                from git_import_error

        clone_dir = self.temp_dir + "/clone/" if self.create_clone_and_res_dirs else self.temp_dir
        result_dir = self.temp_dir + "/result/"

        if ".git//" in self.url:
            git_url, internal_dir = self.url.split(".git//")
            self._clone(git_url + ".git", clone_dir, result_dir, internal_dir)
        else:
            self._clone(self.url, clone_dir, result_dir)

        return result_dir

    def _clone(self, git_url, clone_dir, result_dir, internal_dir=''):
        self.logger.debug("cloning {} to {}".format(self.url, clone_dir))
        if self.tag:
            Repo.clone_from(git_url, clone_dir, b=self.tag)
        else:
            Repo.clone_from(git_url, clone_dir)
        if self.create_clone_and_res_dirs:
            shutil.copytree(clone_dir + internal_dir, result_dir)
