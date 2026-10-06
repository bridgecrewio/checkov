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


def _module_params(root_dir: Path, source: str) -> ModuleParams:
    return ModuleParams(
        root_dir=str(root_dir),
        current_dir=str(root_dir),
        source=source,
        source_version=None,
        dest_dir="",
        external_modules_folder_name=EXTERNAL_MODULES_FOLDER_NAME,
    )


def _is_inside(base: Path, path: str) -> bool:
    return os.path.commonpath([os.path.realpath(base), os.path.realpath(path)]) == os.path.realpath(base)


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
    tmp_path: Path, source: str, expected_dest_dir: str, expected_module_path: str
) -> None:
    external_modules_dir = tmp_path / EXTERNAL_MODULES_FOLDER_NAME
    loader = GenericGitLoader()

    module_path = loader._find_module_path(_module_params(tmp_path, source))
    module_params = _module_params(tmp_path, source)
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
        "git::https://github.com/some/repo.git?ref=..\\..\\target",
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
def test_path_traversal_in_source_is_rejected(tmp_path: Path, source: str) -> None:
    loader = GenericGitLoader()

    with pytest.raises(ValueError):
        loader._process_generic_git_repo(_module_params(tmp_path, source))
    with pytest.raises(ValueError):
        loader._find_module_path(_module_params(tmp_path, source))


def test_traversal_in_inner_module_param_is_rejected(tmp_path: Path) -> None:
    module_params = _module_params(tmp_path, "git::https://github.com/org/repo.git?ref=v1")
    module_params.inner_module = "../../../../../tmp"

    with pytest.raises(ValueError):
        GenericGitLoader()._find_module_path(module_params)


def test_dest_dir_outside_external_modules_dir_is_rejected(tmp_path: Path) -> None:
    # defense in depth - even if parsing returns an unexpected value, never use a folder outside the modules folder
    loader = GenericGitLoader()
    with mock.patch.object(GenericGitLoader, "_get_module_dir", return_value=tmp_path / "outside"):
        with pytest.raises(ValueError):
            loader._process_generic_git_repo(_module_params(tmp_path, "git::https://github.com/org/repo.git"))
        with pytest.raises(ValueError):
            loader._find_module_path(_module_params(tmp_path, "git::https://github.com/org/repo.git"))


TRAVERSAL_REF = "?ref=../../../../../../../../tmp/target"


@pytest.mark.parametrize(
    "loader_class, source, env",
    [
        (GenericGitLoader, f"git::https://github.com/org/repo.git{TRAVERSAL_REF}", {}),
        (GenericGitLoader, f"git::ssh://git@example.com/org/repo.git{TRAVERSAL_REF}", {}),
        (GithubLoader, f"github.com/org/repo{TRAVERSAL_REF}", {}),
        (GithubLoader, f"git@github.com:org/repo.git{TRAVERSAL_REF}", {}),
        (GithubLoader, f"git::git@github.com:org/repo.git{TRAVERSAL_REF}", {}),
        (GithubAccessTokenLoader, f"github.com/org/repo{TRAVERSAL_REF}", {"GITHUB_PAT": "test"}),
        (GithubAccessTokenLoader, f"git@github.com:org/repo.git{TRAVERSAL_REF}", {"GITHUB_PAT": "test"}),
        (BitbucketLoader, f"bitbucket.org/org/repo{TRAVERSAL_REF}", {}),
        (BitbucketAccessTokenLoader, f"bitbucket.org/org/repo{TRAVERSAL_REF}", {"BITBUCKET_TOKEN": "test"}),
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
    git_getter, tmp_path: Path, loader_class, source: str, env: dict
) -> None:
    with mock.patch.dict(os.environ, env):
        loader = loader_class()
        module_params = _module_params(tmp_path, source)
        loader.discover(module_params)
        assert loader._is_matching_loader(module_params)

        with pytest.raises(ValueError):
            loader.load(_module_params(tmp_path, source))
        content = loader._load_module(module_params)

    assert not content.loaded()
    git_getter.assert_not_called()
    assert not module_params.dest_dir or _is_inside(tmp_path / EXTERNAL_MODULES_FOLDER_NAME, module_params.dest_dir)


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
