import os
import shutil
import unittest
from contextlib import ExitStack as does_not_raise
from pathlib import Path
from unittest import mock

import pytest

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.module_loading.loaders.bitbucket_loader import BitbucketLoader
from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.loaders.github_loader import GithubLoader
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry


class TestModuleLoaderRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.current_dir = str(Path(__file__).parent / "tmp")

    def tearDown(self) -> None:
        if os.path.exists(self.current_dir):
            shutil.rmtree(self.current_dir)

    def test_load_terraform_registry(self):
        registry = ModuleLoaderRegistry(True, DEFAULT_EXTERNAL_MODULES_DIR)
        source = "terraform-aws-modules/security-group/aws"
        with registry.load(current_dir=self.current_dir, source=source, source_version="~> 3.0") as content:
            assert content.loaded()
            expected_content_path = os.path.join(
                self.current_dir,
                DEFAULT_EXTERNAL_MODULES_DIR,
                "github.com/terraform-aws-modules/terraform-aws-security-group",
            )
            self.assertRegexpMatches(content.path(), f"^{expected_content_path}/v3.*")

    def test_load_terraform_registry_check_cache(self):
        registry = ModuleLoaderRegistry(download_external_modules=True)
        source1 = "git::https://github.com/bridgecrewio/checkov_not_working1.git"
        registry.load(current_dir=self.current_dir, source=source1, source_version="latest")
        self.assertIn(source1, registry.failed_urls_cache)
        source2 = "git::https://github.com/bridgecrewio/checkov_not_working2.git"
        registry.load(current_dir=self.current_dir, source=source2, source_version="latest")
        self.assertIn(source1 in registry.failed_urls_cache and source2, registry.failed_urls_cache)


@pytest.mark.parametrize(
    "source, source_version, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "terraform-aws-modules/security-group/aws",
            "4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "",
        ),
        (
            "terraform-aws-modules/security-group/aws//modules/http-80",
            "4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0/modules/http-80",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "modules/http-80",
        ),
    ],
    ids=["module_with_version", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_terraform_registry(
    git_getter,
    source,
    source_version,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version=source_version)

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, GenericGitLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
    ],
    ids=["module", "module_with_version", "inner_module", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_generic_git(
    git_getter,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, GenericGitLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, GithubLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, BitbucketLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
def test_load_local_path(git_getter, source, expected_content_path, expected_exception):
    # given
    current_dir = Path(__file__).parent
    registry = ModuleLoaderRegistry()

    # when
    with expected_exception:
        content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

        # then
        assert content.loaded()
        assert content.path() == str(current_dir / expected_content_path)

        git_getter.assert_not_called()


@pytest.mark.parametrize(
    "source, source_version, expected_content_path, expected_git_url, expected_dest_dir, expected_module_source, expected_inner_module",
    [
        (
            "terraform-aws-modules/security-group/aws",
            "4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "",
        ),
        (
            "terraform-aws-modules/security-group/aws//modules/http-80",
            "4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0/modules/http-80",
            "https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "github.com/terraform-aws-modules/terraform-aws-security-group/v4.0.0",
            "git::https://github.com/terraform-aws-modules/terraform-aws-security-group?ref=v4.0.0",
            "modules/http-80",
        ),
    ],
    ids=["module_with_version", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_terraform_registry(
    git_getter,
    source,
    source_version,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version=source_version)

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, GenericGitLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
    ],
    ids=["module", "module_with_version", "inner_module", "inner_module_with_version"],
)
@mock.patch("checkov.terraform.module_loading.loaders.git_loader.GitGetter", autospec=True)
def test_load_generic_git(
    git_getter,
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, GenericGitLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, GithubLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
    source,
    expected_content_path,
    expected_git_url,
    expected_dest_dir,
    expected_module_source,
    expected_inner_module,
):
    # given
    current_dir = Path(__file__).parent / "tmp"
    registry = ModuleLoaderRegistry(download_external_modules=True)

    # when
    content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

    # then
    assert content.loaded()
    assert content.path() == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_content_path)

    git_getter.assert_called_once_with(expected_git_url, mock.ANY)

    git_loader = next(loader for loader in registry.loaders if isinstance(loader, BitbucketLoader))
    assert git_loader.dest_dir == str(current_dir / DEFAULT_EXTERNAL_MODULES_DIR / expected_dest_dir)
    assert git_loader.module_source == expected_module_source
    assert git_loader.inner_module == expected_inner_module


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
def test_load_local_path(git_getter, source, expected_content_path, expected_exception):
    # given
    current_dir = Path(__file__).parent
    registry = ModuleLoaderRegistry()

    # when
    with expected_exception:
        content = registry.load(current_dir=str(current_dir), source=source, source_version="latest")

        # then
        assert content.loaded()
        assert content.path() == str(current_dir / expected_content_path)

        git_getter.assert_not_called()
