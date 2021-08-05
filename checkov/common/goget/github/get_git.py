import logging
import re
import shutil

TAG_PATTERN = re.compile(r'\?(ref=)(?P<tag>(.*))')
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
            #remove tag/ or tags/ from ref= to get actual branch name
            self.tag = re.sub('tag.*/','', self.tag)   
        url = re.sub(TAG_PATTERN, '', url)

        super().__init__(url)

    def do_get(self):
        if git_import_error is not None:
            raise ImportError("Unable to load git module (is the git executable available?)") \
                from git_import_error

        git_url, internal_dir = self._source_subdir()

        clone_dir = self.temp_dir + "/clone/" if self.create_clone_and_res_dirs else self.temp_dir
        self._clone(git_url, clone_dir)

        if internal_dir:
            clone_dir = clone_dir + internal_dir

        if self.create_clone_and_res_dirs:
            result_dir = self.temp_dir + "/result/"
            shutil.copytree(clone_dir, result_dir)
            return result_dir

        return clone_dir

    def _clone(self, git_url, clone_dir):
        self.logger.debug("cloning {} to {}".format(self.url, clone_dir))
        if self.tag:
            Repo.clone_from(git_url, clone_dir, b=self.tag)
        else:
            Repo.clone_from(git_url, clone_dir)

    # Split source url into Git url and subdirectory path e.g. test.com/repo//repo/subpath becomes 'test.com/repo', '/repo/subpath')
    # Also see reference implementation @ go-getter https://github.com/hashicorp/go-getter/blob/main/source.go
    def _source_subdir(self):
        stop = len(self.url)
        
        query_index = self.url.find("?")
        if query_index > -1:
            stop = query_index
        
        start = 0
        scheme_index = self.url.find("://", start, stop)
        if scheme_index > -1:
            start = scheme_index + 3

        subdir_index = self.url.find("//", start, stop)
        if subdir_index == -1:
            return (self.url, "")

        internal_dir = self.url[subdir_index + 1:stop] # Note: Internal dir is expected to start with /
        git_url = self.url[:subdir_index] + self.url[stop:]

        return (git_url, internal_dir)
