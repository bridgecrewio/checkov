import unittest

from unittest.mock import patch, Mock, mock_open
import shutil
import os

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

    def test_parse_shortened_commit_id(self):
        """Test parsing of shortened git commit IDs (5-39 characters)."""
        url = "https://my-git.com/owner/repository-name?ref=aa218"
        getter = GitGetter(url)
        git_url = getter.extract_git_ref(url)

        self.assertEqual(
            "https://my-git.com/owner/repository-name", git_url, "Parsed source url is wrong for 5-char commit"
        )
        self.assertEqual("aa218", getter.commit_id, "Parsed source commit_id is wrong for 5-char commit")

    @patch('checkov.common.goget.github.get_git.Repo')
    @patch('shutil.copytree')
    @patch('os.makedirs')
    def test_do_get_success_with_create_dirs(self, mock_makedirs, mock_copytree, mock_repo):
        """
        Test do_get when create_clone_and_result_dirs is True.
        """
        # Arrange
        url = "https://my-git.com/repo"
        getter = GitGetter(url, create_clone_and_result_dirs=True)
        getter.temp_dir = "/tmp/test"
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance

        # Act
        result_dir = getter.do_get()

        # Assert
        self.assertEqual("/tmp/test/result/", result_dir)
        mock_repo.clone_from.assert_called_once_with(url, "/tmp/test/clone/", depth=1)
        mock_copytree.assert_called_once_with("/tmp/test/clone/", "/tmp/test/result/")
        mock_makedirs.assert_not_called()

    @patch('checkov.common.goget.github.get_git.Repo')
    @patch('shutil.copytree')
    @patch('os.makedirs')
    def test_do_get_success_without_create_dirs(self, mock_makedirs, mock_copytree, mock_repo):
        """
        Test do_get when create_clone_and_result_dirs is False.
        """
        # Arrange
        url = "https://my-git.com/repo"
        getter = GitGetter(url, create_clone_and_result_dirs=False)
        getter.temp_dir = "/tmp/test"
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance

        # Act
        result_dir = getter.do_get()

        # Assert
        self.assertEqual("/tmp/test", result_dir)
        mock_repo.clone_from.assert_called_once_with(url, "/tmp/test", depth=1)
        mock_copytree.assert_not_called()
        mock_makedirs.assert_not_called()

    @patch('checkov.common.goget.github.get_git.git_import_error', ImportError("Mock git import error"))
    def test_do_get_import_error(self):
        """Test the case where the git module fails to import."""
        url = "https://my-git.com/repo"
        getter = GitGetter(url)
        with self.assertRaises(ImportError) as context:
            getter.do_get()
        self.assertEqual("Unable to load git module (is the git executable available?)", str(context.exception))

    @patch('checkov.common.goget.github.get_git.Repo')
    @patch('checkov.common.goget.github.get_git.env_vars_config')
    def test_clone_with_bc_ca_bundle(self, mock_env_vars_config, mock_repo):
        """Test that BC_CA_BUNDLE env var sets GIT_SSL_CAINFO for git clone."""
        # Arrange
        mock_env_vars_config.BC_CA_BUNDLE = '/path/to/ca-bundle.crt'
        mock_env_vars_config.PROXY_URL = None

        url = "https://my-git.com/repo"
        getter = GitGetter(url, create_clone_and_result_dirs=False)
        getter.temp_dir = "/tmp/test"
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance

        captured_env = {}

        def capture_env(*args, **kwargs):
            captured_env['GIT_SSL_CAINFO'] = os.environ.get('GIT_SSL_CAINFO')
            return mock_repo_instance

        mock_repo.clone_from.side_effect = capture_env

        # Act
        getter.do_get()

        # Assert
        self.assertEqual('/path/to/ca-bundle.crt', captured_env.get('GIT_SSL_CAINFO'))
        mock_repo.clone_from.assert_called_once()

    @patch('checkov.common.goget.github.get_git.Repo')
    @patch('checkov.common.goget.github.get_git.env_vars_config')
    def test_clone_without_bc_ca_bundle(self, mock_env_vars_config, mock_repo):
        """Test that clone works without BC_CA_BUNDLE env var."""
        # Arrange
        mock_env_vars_config.BC_CA_BUNDLE = None
        mock_env_vars_config.PROXY_URL = None

        url = "https://my-git.com/repo"
        getter = GitGetter(url, create_clone_and_result_dirs=False)
        getter.temp_dir = "/tmp/test"
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance

        captured_env = {}

        def capture_env(*args, **kwargs):
            captured_env['GIT_SSL_CAINFO'] = os.environ.get('GIT_SSL_CAINFO')
            return mock_repo_instance

        mock_repo.clone_from.side_effect = capture_env

        # Act
        getter.do_get()

        # Assert
        self.assertIsNone(captured_env.get('GIT_SSL_CAINFO'))
        mock_repo.clone_from.assert_called_once()

    @patch('checkov.common.goget.github.get_git.Repo')
    @patch('checkov.common.goget.github.get_git.env_vars_config')
    def test_clone_proxy_takes_precedence_over_bc_ca_bundle(self, mock_env_vars_config, mock_repo):
        """Test that PROXY_URL settings take precedence over BC_CA_BUNDLE."""
        # Arrange
        mock_env_vars_config.PROXY_URL = 'http://proxy.example.com:8080'
        mock_env_vars_config.PROXY_CA_PATH = '/path/to/proxy-ca.crt'
        mock_env_vars_config.PROXY_HEADER_KEY = 'X-Custom-Header'
        mock_env_vars_config.PROXY_HEADER_VALUE = 'custom-value'
        mock_env_vars_config.BC_CA_BUNDLE = '/path/to/ca-bundle.crt'

        url = "https://my-git.com/repo"
        getter = GitGetter(url, create_clone_and_result_dirs=False)
        getter.temp_dir = "/tmp/test"
        mock_repo_instance = Mock()
        mock_repo.clone_from.return_value = mock_repo_instance

        captured_env = {}

        def capture_env(*args, **kwargs):
            captured_env['GIT_SSL_CAINFO'] = os.environ.get('GIT_SSL_CAINFO')
            captured_env['https_proxy'] = os.environ.get('https_proxy')
            return mock_repo_instance

        mock_repo.clone_from.side_effect = capture_env

        # Act
        getter.do_get()

        # Assert - PROXY_CA_PATH should be used, not BC_CA_BUNDLE
        self.assertEqual('/path/to/proxy-ca.crt', captured_env.get('GIT_SSL_CAINFO'))
        self.assertEqual('http://proxy.example.com:8080', captured_env.get('https_proxy'))
        mock_repo.clone_from.assert_called_once()


if __name__ == '__main__':
    unittest.main()
