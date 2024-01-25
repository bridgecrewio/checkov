import os
from contextlib import ExitStack as does_not_raise
from pathlib import Path
from unittest import mock

import pytest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.loaders.bitbucket_loader import BitbucketLoader # noqa
from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader # noqa
from checkov.terraform.module_loading.loaders.github_loader import GithubLoader # noqa
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry # noqa
from checkov.terraform.module_loading.loaders.github_access_token_loader import GithubAccessTokenLoader # noqa
from checkov.terraform.module_loading.loaders.bitbucket_access_token_loader import BitbucketAccessTokenLoader # noqa


@pytest.mark.parametrize(
    "source, source_version, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "terraform-aws-modules/security-group/aws",
            "4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/ff2efb814c924572d27280b99a799fc34d061109",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=ff2efb814c924572d27280b99a799fc34d061109",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=ff2efb814c924572d27280b99a799fc34d061109",
            "",
        ),
        (
            "terraform-aws-modules/security-group/aws//modules/http-80",
            "4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/ff2efb814c924572d27280b99a799fc34d061109/modules/http-80",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=ff2efb814c924572d27280b99a799fc34d061109",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=ff2efb814c924572d27280b99a799fc34d061109",
            "modules/http-80",
        )
    ],
    ids=["module_with_version", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_terraform_registry(
    git_getter,
    tmp_path: Path,
    source,
    source_version,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = tmp_path / "tf_registry"
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version=source_version)

    # then
    assert content.loaded()
    assert content.path() == str(Path(DEFAULT_EXTERNAL_MODULES_DIR) / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)


@pytest.mark.parametrize(
    "source, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "git::https://example.com/network.git",
            "example.com/network/HEAD",
            "https://example.com/network.git",
            "example.com/network/HEAD",
            "git::https://example.com/network.git",
            "",
        ),
        (
            "git::https://example.com/network.git?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "https://example.com/network.git?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "git::https://example.com/network.git?ref=v1.2.0",
            "",
        ),
        (
            "git::https://example.com/network.git//modules/vpc",
            "example.com/network/HEAD/modules/vpc",
            "https://example.com/network",
            "example.com/network/HEAD",
            "git::https://example.com/network",
            "modules/vpc",
        ),
        (
            "git::https://example.com/network.git//modules/vpc?ref=v1.2.0",
            "example.com/network/v1.2.0/modules/vpc",
            "https://example.com/network?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "git::https://example.com/network?ref=v1.2.0",
            "modules/vpc",
        ),
        (
            "git::ssh://username@example.com/network.git",
            "example.com/network/HEAD",
            "ssh://username@example.com/network.git",
            "example.com/network/HEAD",
            "git::ssh://username@example.com/network.git",
            "",
        ),
        (
            "git::ssh://username@example.com/network.git?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "ssh://username@example.com/network.git?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "git::ssh://username@example.com/network.git?ref=v1.2.0",
            "",
        ),
        (
            "git::username@example.com/network.git",
            "example.com/network/HEAD",
            "username@example.com/network.git",
            "example.com/network/HEAD",
            "git::username@example.com/network.git",
            "",
        ),
        (
            "git::username@example.com/network.git?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "username@example.com/network.git?ref=v1.2.0",
            "example.com/network/v1.2.0",
            "git::username@example.com/network.git?ref=v1.2.0",
            "",
        ),
        (
            "git::ssh://git@github.com/bridgecrewio/terragoat//modules/s3-encrypted",
            "git@github.com/bridgecrewio/terragoat/HEAD/modules/s3-encrypted",
            "ssh://git@github.com/bridgecrewio/terragoat",
            "git@github.com/bridgecrewio/terragoat/HEAD",
            "git::ssh://git@github.com/bridgecrewio/terragoat",
            "modules/s3-encrypted",
        ),
    ],
    ids=[
        "module",
        "module_with_version",
        "inner_module",
        "inner_module_with_version",
        "module_over_ssh",
        "module_over_ssh_with_version",
        "module_over_ssh_without_protocol",
        "module_over_ssh_without_protocol_with_version",
        "git_username",
    ],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_generic_git(
    git_getter,
    tmp_path: Path,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = tmp_path / "generic"
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(Path(DEFAULT_EXTERNAL_MODULES_DIR) / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)


@pytest.mark.parametrize(
    "source, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "github.com/terraform-aws-modules/terraform-aws-security-group",
            "github.com/terraform-aws-modules/terraform-aws-security-group/HEAD",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group",
            "github.com/terraform-aws-modules/terraform-aws-security-group/HEAD",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group",
            "",
        ),
        (
            "github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "",
        ),
        (
            "github.com/terraform-aws-modules/terraform-aws-security-group//modules/http-80",
            "github.com/terraform-aws-modules/terraform-aws-security-group/HEAD/modules/http-80",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group",
            "github.com/terraform-aws-modules/terraform-aws-security-group/HEAD",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group",
            "modules/http-80",
        ),
        (
            "github.com/terraform-aws-modules/terraform-aws-security-group//modules/http-80?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0/modules/http-80",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "modules/http-80",
        ),
    ],
    ids=["module", "module_with_version", "inner_module", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_github(
    git_getter,
    tmp_path: Path,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = tmp_path / "github"
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(Path(DEFAULT_EXTERNAL_MODULES_DIR) / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)


# TODO: create a dummy repo in bitbucket for more consitent tests
@pytest.mark.parametrize(
    "source, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/HEAD",
            "https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/HEAD",
            "git::https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha",
            "",
        ),
        (
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha?ref=v0.1.0",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/v0.1.0",
            "https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha?ref=v0.1.0",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/v0.1.0",
            "git::https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha?ref=v0.1.0",
            "",
        ),
        (
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha//rancher2-ha",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/HEAD/rancher2-ha",
            "https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/HEAD",
            "git::https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha",
            "rancher2-ha",
        ),
        (
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha//rancher2-ha?ref=v0.1.0",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/v0.1.0/rancher2-ha",
            "https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha?ref=v0.1.0",
            "bitbucket.org/nuarch/terraform-aws-rancher-server-ha/v0.1.0",
            "git::https://bitbucket.org/nuarch/terraform-aws-rancher-server-ha?ref=v0.1.0",
            "rancher2-ha",
        ),
    ],
    ids=["module", "module_with_version", "inner_module", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_bitbucket(
    git_getter,
    tmp_path: Path,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = tmp_path / "bitbucket"
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(Path(DEFAULT_EXTERNAL_MODULES_DIR) / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)


@pytest.mark.parametrize(
    "source, expected_content_path, expected_exception",
    [
        ("./loaders/resources", "loaders/resources", does_not_raise()),
        ("../module_loading/loaders/resources", "loaders/resources", does_not_raise()),
        ("./does_not_exist", "", pytest.raises(FileNotFoundError)),
    ],
    ids=["current_dir", "parent_dir", "not_exists"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_local_path(git_getter, tmp_path: Path, source, expected_content_path, expected_exception):
    # given
    current_dir = Path(__file__).parent
    registry = ModuleLoaderRegistry()
    registry.module_content_cache = {}

    # when
    with expected_exception:
        content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

        # then
        assert content.loaded()
        assert content.path() == str(current_dir / expected_content_path)

        git_getter.assert_not_called()


@pytest.mark.parametrize(
    "source, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "github.com/kartikp10/terraform-aws-s3-bucket1",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1",  # checkov:skip=CKV_SECRET_4 test secret
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1",
            "",
        ),
       (
            "git::https://github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "",
        ),
       (
           "git@github.com:kartikp10/terraform-aws-s3-bucket1.git",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "",
        ),
       (
           "git::ssh://git@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "github.com/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git",
            "",
        ),
        (
            "github.com/kartikp10/terraform-aws-security-group//modules/http-80",
            "github.com/kartikp10/terraform-aws-security-group/HEAD/modules/http-80",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-security-group",
            "github.com/kartikp10/terraform-aws-security-group/HEAD",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-security-group",
            "modules/http-80",
        ),
        (
            "git::ssh://git@github.com/kartikp10/terraform-aws-s3-bucket1.git?ref=v1.2.0",
            "github.com/kartikp10/terraform-aws-s3-bucket1/v1.2.0",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git?ref=v1.2.0",
            "github.com/kartikp10/terraform-aws-s3-bucket1/v1.2.0",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-s3-bucket1.git?ref=v1.2.0",
            "",
        ),
       (
           "git@github.com:kartikp10/terraform-aws-security-group.git//modules/http-80",
            "github.com/kartikp10/terraform-aws-security-group/HEAD",
            "https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-security-group",
            "github.com/kartikp10/terraform-aws-security-group/HEAD",
            "git::https://x-access-token:ghp_xxxxxxxxxxxxxxxxx@github.com/kartikp10/terraform-aws-security-group",
            "modules/http-80",
        )
    ],
    ids=["github_http_module", "generic_git_module", "ssh_github_module", "generic_ssh_module","github_http_module", "generic_ssh_module_version", "github_ssh_module_version"],
)
@mock.patch.dict(os.environ, {"GITHUB_PAT": "ghp_xxxxxxxxxxxxxxxxx"})
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_github_private(
    git_getter,
    tmp_path: Path,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    git_getter.side_effect = [Exception(), None]
    # given
    current_dir = tmp_path / "github_private"
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}

    # when
    registry.loaders = [GithubAccessTokenLoader()]
    registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    git_getter.assert_called_with(expected_git_url, create_clone_and_result_dirs=False)


@pytest.mark.parametrize(
    "source, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "bitbucket.org/kartikp10/terraform-aws-s3-bucket1",
            "bitbucket.org/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "https://x-token-auth:xxxxxxxxxxxxxxxxx@bitbucket.org/kartikp10/terraform-aws-s3-bucket1",  # checkov:skip=CKV_SECRET_4 test secret
            "bitbucket.org/kartikp10/terraform-aws-s3-bucket1/HEAD",
            "git::https://x-token-auth:xxxxxxxxxxxxxxxxx@bitbucket.org/kartikp10/terraform-aws-s3-bucket1",
            "",
        )
    ],
    ids=["module"],
)
@mock.patch.dict(os.environ, {"BITBUCKET_TOKEN": "xxxxxxxxxxxxxxxxx"})  # checkov:skip=CKV_SECRET_6 test secret
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_bitbucket_private(
    git_getter,
    tmp_path: Path,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    git_getter.side_effect = [Exception(), None]
    # given
    current_dir = tmp_path / "bitbucket_private"
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}

    # when
    registry.loaders = [BitbucketAccessTokenLoader()]
    registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    git_getter.assert_called_with(expected_git_url, create_clone_and_result_dirs=False)


def test_load_terraform_registry_with_real_download(tmp_path: Path):
    # given
    current_dir = str(tmp_path / "tf_download")
    registry = ModuleLoaderRegistry(download_external_modules=True, external_modules_folder_name=DEFAULT_EXTERNAL_MODULES_DIR)
    registry.module_content_cache = {}
    registry.root_dir = current_dir

    source = "terraform-aws-modules/security-group/aws"

    # when
    content = registry.load(current_dir=current_dir, source=source, source_version="~> 3.0")

    expected_content_path = os.path.join(
        current_dir,
        DEFAULT_EXTERNAL_MODULES_DIR,
        "github.com/terraform-aws-modules/terraform-aws-security-group",
    )

    assert content.loaded()
    content_path = content.path()
    assert content_path.startswith(f"{expected_content_path}/v3.") or \
           content_path.startswith(f"{expected_content_path}/2cd10c8aca557fd858f401616d5c3b27e2a7b595")


def test_load_terraform_registry_check_cache(tmp_path: Path):
    # given
    current_dir = str(tmp_path / "cache_check")
    registry = ModuleLoaderRegistry(download_external_modules=True)
    registry.module_content_cache = {}
    registry.root_dir = current_dir

    source1 = "git::https://github.com/bridgecrewio/checkov_not_working1.git"
    source2 = "git::https://github.com/bridgecrewio/checkov_not_working2.git"

    # when
    registry.load(current_dir=current_dir, source=source1, source_version="latest")

    assert source1 in registry.failed_urls_cache

    registry.load(current_dir=current_dir, source=source2, source_version="latest")

    # then
    assert source1 in registry.failed_urls_cache
    assert source2 in registry.failed_urls_cache


def test_loader_equality():
    githubLoaderOne = GithubLoader()
    githubLoaderTwo = GithubLoader()
    assert githubLoaderOne == githubLoaderTwo
    bitLoader = BitbucketLoader()
    assert githubLoaderOne != bitLoader
    genericLoader = GenericGitLoader()
    assert githubLoaderOne != genericLoader and bitLoader != genericLoader


def test_multiple_similar_loaders():
    registry = ModuleLoaderRegistry(download_external_modules=True)
    assert len(registry.loaders) == 7
    GithubLoader()
    GithubLoader()
    GenericGitLoader()
    BitbucketLoader()
    assert len(registry.loaders) == 7
