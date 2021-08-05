import os
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
        self.assertEqual("my-git.com/repository-name", git_url, "Parsed source url should contain hostname ane path")
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

if __name__ == '__main__':
    unittest.main()
