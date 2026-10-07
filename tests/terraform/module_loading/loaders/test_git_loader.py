import os
from pathlib import Path
from unittest import mock

import pytest

from checkov.terraform.module_loading.loaders.bitbucket_access_token_loader import BitbucketAccessTokenLoader
from checkov.terraform.module_loading.loaders.bitbucket_loader import BitbucketLoader
from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader, _validate_ref, _validate_subdir
from checkov.terraform.module_loading.loaders.github_access_token_loader import GithubAccessTokenLoader
from checkov.terraform.module_loading.loaders.github_loader import GithubLoader
from checkov.terraform.module_loading.module_params import ModuleParams

EXTERNAL_MODULES_FOLDER_NAME = ".external_modules"


@pytest.mark.parametrize("source, expected_root_module, expected_inner_module", [
    ("git::git@github.com:test-inner-module/out-module//inner-module?ref=main",
     "github.com:test-inner-module/out-module", "inner-module"),
    ("git::https://github.com:test-inner-module/out-module//inner-module?ref=main",
     "github.com:test-inner-module/out-module", "inner-module"),
    ("git::https://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("git::ssh://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("https://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("https://github.com:test-with-inner-module-no-git-prefix/out-module//in-module",
     "github.com:test-with-inner-module-no-git-prefix/out-module", "in-module")
]
                         )
def test__parse_module_source(source: str, expected_root_module: str, expected_inner_module: str) -> None:
    git_loader = GenericGitLoader()
    module_params = ModuleParams(
        root_dir="test",
        current_dir="test",
        source=source,
        source_version="source_version",
        dest_dir="test",
        external_modules_folder_name="test",
        inner_module="",
        tf_managed=False
    )
    module_source = git_loader._parse_module_source(module_params)
    assert module_source.root_module == expected_root_module
    assert module_source.inner_module == expected_inner_module


@pytest.fixture
def root_dir() -> Path:
    # these tests only compute paths and never write to disk, so a fixed (non existing) folder is enough.
    # avoids pytest's tmp_path, which crashes the xdist worker on python 3.9/3.10 (see verification/conftest.py)
    return Path(os.path.abspath("checkov_git_loader_test_root"))


def _module_params(root_dir: Path, source: str) -> ModuleParams:
    return ModuleParams(
        root_dir=str(root_dir),
        current_dir=str(root_dir),
        source=source,
        source_version=None,
        dest_dir="",
        external_modules_folder_name=EXTERNAL_MODULES_FOLDER_NAME,
    )


def _make_module_params(source: str) -> ModuleParams:
    """Helper to create a ModuleParams instance with default test values."""
    return ModuleParams(
        root_dir="test",
        current_dir="test",
        source=source,
        source_version="latest",
        dest_dir="test",
        external_modules_folder_name="test",
        inner_module="",
        tf_managed=False,
    )


def _is_inside(base: Path, path: str) -> bool:
    return os.path.commonpath([os.path.abspath(base), os.path.abspath(path)]) == os.path.abspath(base)


@pytest.mark.parametrize(
    "source, expected_dest_dir, expected_module_path",
    [
        (
            "git::https://github.com/org/repo.git?ref=v1.0.0",
            "github.com/org/repo/v1.0.0",
            "github.com/org/repo/v1.0.0",
        ),
        (
            "git::https://github.com/org/repo.git?ref=valid-tag-v1.0",
            "github.com/org/repo/valid-tag-v1.0",
            "github.com/org/repo/valid-tag-v1.0",
        ),
        (
            "git::https://github.com/org/repo.git?ref=feature/with/slashes",
            "github.com/org/repo/feature/with/slashes",
            "github.com/org/repo/feature/with/slashes",
        ),
        (
            "git::https://github.com/org/repo.git?ref=heads/release..1",
            "github.com/org/repo/heads/release..1",
            "github.com/org/repo/heads/release..1",
        ),
        (
            "git::https://github.com/org/repo.git//modules/vpc?ref=v2",
            "github.com/org/repo/v2",
            "github.com/org/repo/v2/modules/vpc",
        ),
        (
            "git::https://github.com/org/repo.git",
            "github.com/org/repo/HEAD",
            "github.com/org/repo/HEAD",
        ),
        (
            "git::file:///srv/git/repo.git?ref=v1",
            "srv/git/repo/v1",
            "srv/git/repo/v1",
        ),
        (
            "git::https://github.com/org/repo.git?ref=a1b2c3d4e5f6a7b8c9d0a1b2c3d4e5f6a7b8c9d0",
            "github.com/org/repo/a1b2c3d4e5f6a7b8c9d0a1b2c3d4e5f6a7b8c9d0",
            "github.com/org/repo/a1b2c3d4e5f6a7b8c9d0a1b2c3d4e5f6a7b8c9d0",
        ),
        (
            "git::https://github.com/org/repo.git//modules/../vpc?ref=v2",
            "github.com/org/repo/v2",
            "github.com/org/repo/v2/modules/../vpc",
        ),
        (
            "git::https://github.com/org/repo.git//modules/vpc/?ref=v2",
            "github.com/org/repo/v2",
            "github.com/org/repo/v2/modules/vpc",
        ),
        (
            "git::https://dev.azure.com/org/project/_git/repo?ref=v1",
            "dev.azure.com/org/project/_git/repo/v1",
            "dev.azure.com/org/project/_git/repo/v1",
        ),
    ],
    ids=[
        "tag", "tag_with_dash", "branch_with_slashes", "dots_inside_segment", "inner_module", "no_ref",
        "local_file_repo", "commit_sha", "inner_module_with_inner_dotdot", "inner_module_trailing_slash", "azure_devops",
    ],
)
def test_valid_sources_stay_in_external_modules_dir(
    root_dir: Path, source: str, expected_dest_dir: str, expected_module_path: str
) -> None:
    external_modules_dir = root_dir / EXTERNAL_MODULES_FOLDER_NAME
    loader = GenericGitLoader()

    module_path = loader._find_module_path(_module_params(root_dir, source))
    module_params = _module_params(root_dir, source)
    loader._process_generic_git_repo(module_params)

    assert module_params.dest_dir == str(external_modules_dir / expected_dest_dir)
    assert module_path == str(external_modules_dir / expected_module_path)


@pytest.mark.parametrize(
    "source",
    [
        "git::https://github.com/some/repo.git?ref=../../../../../../tmp/target",
        "git::https://github.com/some/repo.git?ref=..",
        "git::https://github.com/some/repo.git?ref=v1/../../../../target",
        "git::https://github.com/some/repo.git?ref=/tmp/target",
        "git::https://github.com/some/repo.git?ref=..\\\\..\\\\target",
        "git::https://github.com/some/repo.git//../../../../../../tmp?ref=v1",
        "git::https://github.com/some/repo.git//modules/../../../../../../../tmp?ref=v1",
        "git::https://github.com/some/repo.git//..?ref=v1",
        "git::https://github.com/some/repo.git///tmp/target?ref=v1",
        "git::https://github.com/../../../../../../tmp/target",
        "git::file:///../../../../tmp/target",
    ],
    ids=[
        "ref_relative_traversal",
        "ref_parent_dir",
        "ref_nested_traversal",
        "ref_absolute_path",
        "ref_backslash_traversal",
        "inner_module_traversal",
        "inner_module_nested_traversal",
        "inner_module_parent_dir",
        "inner_module_absolute_path",
        "root_module_traversal",
        "local_file_repo_traversal",
    ],
)
def test_path_traversal_in_source_is_rejected(root_dir: Path, source: str) -> None:
    loader = GenericGitLoader()

    with pytest.raises(ValueError):
        loader._process_generic_git_repo(_module_params(root_dir, source))
    with pytest.raises(ValueError):
        loader._find_module_path(_module_params(root_dir, source))


def test_traversal_in_inner_module_param_is_rejected(root_dir: Path) -> None:
    module_params = _module_params(root_dir, "git::https://github.com/org/repo.git?ref=v1")
    module_params.inner_module = "../../../../../tmp"

    with pytest.raises(ValueError):
        GenericGitLoader()._find_module_path(module_params)


def test_dest_dir_outside_external_modules_dir_is_rejected(root_dir: Path) -> None:
    # defense in depth - even if parsing returns an unexpected value, never use a folder outside the modules folder
    loader = GenericGitLoader()
    with mock.patch.object(GenericGitLoader, "_get_module_dir", return_value=root_dir / "outside"):
        with pytest.raises(ValueError):
            loader._process_generic_git_repo(_module_params(root_dir, "git::https://github.com/org/repo.git"))
        with pytest.raises(ValueError):
            loader._find_module_path(_module_params(root_dir, "git::https://github.com/org/repo.git"))


TRAVERSAL_REF = "?ref=../../../../../../../../tmp/target"


@pytest.mark.parametrize(
    "loader_class, source, env",
    [
        (GenericGitLoader, f"git::https://github.com/org/repo.git{TRAVERSAL_REF}", {}),
        (GenericGitLoader, f"git::ssh://git@example.com/org/repo.git{TRAVERSAL_REF}", {}),
        (GithubLoader, f"github.com/org/repo{TRAVERSAL_REF}", {}),
        (GithubLoader, f"git@github.com:org/repo.git{TRAVERSAL_REF}", {}),
        (GithubLoader, f"git::git@github.com:org/repo.git{TRAVERSAL_REF}", {}),
        (GithubAccessTokenLoader, f"github.com/org/repo{TRAVERSAL_REF}", {"GITHUB_PAT": "test", "GITHUB_PAT_ALLOWED_ORGS": "*"}),
        (GithubAccessTokenLoader, f"git@github.com:org/repo.git{TRAVERSAL_REF}", {"GITHUB_PAT": "test", "GITHUB_PAT_ALLOWED_ORGS": "*"}),
        (BitbucketLoader, f"bitbucket.org/org/repo{TRAVERSAL_REF}", {}),
        (BitbucketAccessTokenLoader, f"bitbucket.org/org/repo{TRAVERSAL_REF}", {"BITBUCKET_TOKEN": "test", "BITBUCKET_ALLOWED_WORKSPACES": "*"}),
    ],
    ids=[
        "generic_git_https",
        "generic_git_ssh",
        "github",
        "github_ssh",
        "github_git_ssh",
        "github_access_token",
        "github_access_token_ssh",
        "bitbucket",
        "bitbucket_access_token",
    ],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_git_based_loaders_do_not_clone_outside_external_modules_dir(
    git_getter, root_dir: Path, loader_class, source: str, env: dict
) -> None:
    with mock.patch.dict(os.environ, env):
        loader = loader_class()
        module_params = _module_params(root_dir, source)
        loader.discover(module_params)
        assert loader._is_matching_loader(module_params)

        with pytest.raises(ValueError):
            loader.load(_module_params(root_dir, source))
        content = loader._load_module(module_params)

    assert not content.loaded()
    git_getter.assert_not_called()
    assert not module_params.dest_dir or _is_inside(root_dir / EXTERNAL_MODULES_FOLDER_NAME, module_params.dest_dir)


@pytest.mark.parametrize(
    "ref",
    ["v1.0.0", "valid-tag-v1.0", "feature/with/slashes", "heads/main", "tags/v1.2.3", "release..1", "a.b", "HEAD",
     "a1b2c3d", "user@feature", "feature.v2"],
)
def test_validate_ref_allows_valid_git_refs(ref: str) -> None:
    _validate_ref(ref)


@pytest.mark.parametrize("ref", ["..", "../x", "x/..", "x/../../y", "/abs", "/", "a\\b", "..\\x", "a\0b"])
def test_validate_ref_rejects_traversal(ref: str) -> None:
    with pytest.raises(ValueError):
        _validate_ref(ref)


@pytest.mark.parametrize(
    "subdir", ["", "modules/vpc", "modules/vpc/", "./modules/vpc", "modules/../vpc", "a/b/../../c", "modules//vpc", "v1..2"]
)
def test_validate_subdir_allows_paths_inside_package(subdir: str) -> None:
    _validate_subdir(subdir)


@pytest.mark.parametrize("subdir", ["..", "../x", "x/../..", "a/b/../../../c", "/abs", "/", "a\0b"])
def test_validate_subdir_rejects_paths_outside_package(subdir: str) -> None:
    with pytest.raises(ValueError):
        _validate_subdir(subdir)


class TestCredentialScoping:
    """Tests for VCS credential injection scoping.

    Credentials should only be injected when VCS_BASE_URL is configured
    and the module source host matches the VCS_BASE_URL host.
    """

    def test_credentials_not_injected_when_vcs_base_url_not_set(self) -> None:
        """When VCS_BASE_URL is not set, credentials should not be injected."""
        with mock.patch.dict(os.environ, {"VCS_TOKEN": "test-token", "VCS_USERNAME": "test-user"}, clear=False):
            loader = GenericGitLoader()
            module_params = _make_module_params("git::https://some-server.example.com/org/repo")
            loader.discover(module_params)
            result = loader._is_matching_loader(module_params)
            assert result is True
            assert "test-token" not in module_params.module_source
            assert "test-user" not in module_params.module_source

    def test_credentials_injected_when_vcs_base_url_matches(self) -> None:
        """When VCS_BASE_URL matches the module source host, credentials should be injected."""
        with mock.patch.dict(os.environ, {
            "VCS_TOKEN": "test-token",
            "VCS_USERNAME": "test-user",
            "VCS_BASE_URL": "https://gitlab.example.com",
        }, clear=False):
            loader = GenericGitLoader()
            module_params = _make_module_params("git::https://gitlab.example.com/org/repo")
            loader.discover(module_params)
            result = loader._is_matching_loader(module_params)
            assert result is True
            assert "test-token" in module_params.module_source
            assert "test-user" in module_params.module_source

    def test_credentials_not_injected_when_vcs_base_url_does_not_match(self) -> None:
        """When VCS_BASE_URL does not match the module source host, credentials should not be injected."""
        with mock.patch.dict(os.environ, {
            "VCS_TOKEN": "test-token",
            "VCS_USERNAME": "test-user",
            "VCS_BASE_URL": "https://gitlab.example.com",
        }, clear=False):
            loader = GenericGitLoader()
            module_params = _make_module_params("git::https://other-server.example.com/org/repo")
            loader.discover(module_params)
            result = loader._is_matching_loader(module_params)
            assert result is True
            assert "test-token" not in module_params.module_source
            assert "test-user" not in module_params.module_source

    def test_credentials_injected_when_host_matches_default_prefix(self) -> None:
        """When VCS_BASE_URL host matches the source host, credentials should be injected."""
        with mock.patch.dict(os.environ, {
            "VCS_TOKEN": "test-token",
            "VCS_USERNAME": "test-user",
            "VCS_BASE_URL": "https://gitlab.example.com",
        }, clear=False):
            loader = GenericGitLoader()
            module_params = _make_module_params("git::https://gitlab.example.com/org/repo.git?ref=v1")
            loader.discover(module_params)
            result = loader._is_matching_loader(module_params)
            assert result is True
            assert "test-token" in module_params.module_source

    def test_credentials_not_injected_when_host_differs_default_prefix(self) -> None:
        """When VCS_BASE_URL host differs from source host, credentials should not be injected."""
        with mock.patch.dict(os.environ, {
            "VCS_TOKEN": "test-token",
            "VCS_USERNAME": "test-user",
            "VCS_BASE_URL": "https://gitlab.example.com",
        }, clear=False):
            loader = GenericGitLoader()
            module_params = _make_module_params("git::https://other.example.com/org/repo.git?ref=v1")
            loader.discover(module_params)
            result = loader._is_matching_loader(module_params)
            assert result is True
            assert "test-token" not in module_params.module_source
