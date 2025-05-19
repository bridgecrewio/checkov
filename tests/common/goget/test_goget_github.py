import unittest

from checkov.common.goget.github.get_git import GitGetter


class TestGitGetter(unittest.TestCase):
    def test_parse_source(self):
        url = "https://my-git.com/repository-name/"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("https://my-git.com/repository-name/", git_url, "Parsed source url should contain hostname and path")
        self.assertEqual("", subdir, "Parsed source subdirectory should be empty")

    def test_parse_source_and_subdirectory(self):
        url = "https://my-git.com/repository-name.git//sub/path"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("https://my-git.com/repository-name.git", git_url, "Parsed source url should contain hostname and path")
        self.assertEqual("/sub/path", subdir, "Parsed source subdirectory should contain absolute (sub)path")

    def test_parse_source_and_subdirectory_without_git(self):
        url = "https://my-git.com/repository-name//sub/path"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("https://my-git.com/repository-name", git_url, "Parsed source url should contain hostname and path")
        self.assertEqual("/sub/path", subdir, "Parsed source subdirectory should contain absolute (sub)path")

    def test_parse_source_with_query(self):
        url = "https://my-git.com/repository-name?key=value"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("https://my-git.com/repository-name?key=value", git_url, "Parsed source url should contain hostname, path and query")
        self.assertEqual("", subdir, "Parsed source subdirectory should be empty")

    def test_parse_source_and_subdirectory_with_query(self):
        url = "https://my-git.com/repository-name//sub/path?key=value"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("https://my-git.com/repository-name?key=value", git_url, "Parsed source url should contain hostname, path and query")
        self.assertEqual("/sub/path", subdir, "Parsed source subdirectory should contain absolute (sub)path")

    def test_parse_source_without_scheme(self):
        url = "my-git.com/repository-name"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("my-git.com/repository-name", git_url, "Parsed source url should contain hostname and path")
        self.assertEqual("", subdir, "Parsed source subdirectory should be empty")

    def test_parse_source_and_subdirectory_without_scheme(self):
        url = "my-git.com/repository-name//sub/path"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("my-git.com/repository-name", git_url, "Parsed source url should contain hostname and path")
        self.assertEqual("/sub/path", subdir, "Parsed source subdirectory should contain absolute (sub)path")

    def test_parse_source_with_query_without_scheme(self):
        url = "my-git.com/repository-name?key=value"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("my-git.com/repository-name?key=value", git_url, "Parsed source url should contain hostname, path and query")
        self.assertEqual("", subdir, "Parsed source subdirectory should be empty")

    def test_parse_source_and_subdirectory_with_query_without_scheme(self):
        url = "my-git.com/repository-name//sub/path?key=value"
        getter = GitGetter(url)
        git_url, subdir = getter._source_subdir()
        self.assertEqual("my-git.com/repository-name?key=value", git_url, "Parsed source url should contain hostname, path and query")
        self.assertEqual("/sub/path", subdir, "Parsed source subdirectory should contain absolute (sub)path")

    def test_parse_tag(self):
        url = "https://my-git.com/owner/repository-name?ref=tags/v1.2.3"
        getter = GitGetter(url)
        git_url = getter.extract_git_ref(url)

        self.assertEqual("https://my-git.com/owner/repository-name", git_url,
                         "Parsed source url is wrong")
        self.assertEqual("v1.2.3", getter.tag, "Parsed source tag is wrong")

    def test_parse_tag_backward_compat(self):
        url = "https://my-git.com/owner/repository-name?ref=v1.2.3"
        getter = GitGetter(url)
        git_url = getter.extract_git_ref(url)

        self.assertEqual("https://my-git.com/owner/repository-name", git_url,
                         "Parsed source url is wrong")
        self.assertEqual("v1.2.3", getter.tag, "Parsed source tag is wrong")

    def test_parse_branch(self):
        url = "https://my-git.com/owner/repository-name?ref=heads/omryBranch"
        getter = GitGetter(url)
        git_url = getter.extract_git_ref(url)

        self.assertEqual("https://my-git.com/owner/repository-name", git_url,
                         "Parsed source url is wrong")
        self.assertEqual("omryBranch", getter.branch, "Parsed source branch is wrong")

    def test_parse_commit_id(self):
        url = "https://my-git.com/owner/repository-name?ref=aa218f56b14c9653891f9e74264a383fa43fefbd"
        getter = GitGetter(url)
        git_url = getter.extract_git_ref(url)

        self.assertEqual("https://my-git.com/owner/repository-name", git_url,
                         "Parsed source url is wrong")
        self.assertEqual("aa218f56b14c9653891f9e74264a383fa43fefbd", getter.commit_id,
                         "Parsed source commit_id is wrong")


if __name__ == '__main__':
    unittest.main()
