import os
from pathlib import Path
from unittest import mock

import pytest

from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.loaders.s3_loader import S3Loader
from checkov.terraform.module_loading.module_params import ModuleParams
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry


class TestS3LoaderIsMatchingLoader:
    """Test the _is_matching_loader method."""

    def setup_method(self) -> None:
        self.loader = S3Loader()

    def _make_params(self, source: str, tmp_path: Path) -> ModuleParams:
        return ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source=source,
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
        )

    def test_matches_s3_prefix(self, tmp_path: Path) -> None:
        params = self._make_params("s3::https://s3-eu-west-1.amazonaws.com/bucket/module.zip", tmp_path)
        assert self.loader._is_matching_loader(params) is True

    def test_matches_s3_prefix_virtual_hosted(self, tmp_path: Path) -> None:
        params = self._make_params("s3::https://bucket.s3-eu-west-1.amazonaws.com/module.zip", tmp_path)
        assert self.loader._is_matching_loader(params) is True

    def test_does_not_match_git(self, tmp_path: Path) -> None:
        params = self._make_params("git::https://github.com/org/repo.git", tmp_path)
        assert self.loader._is_matching_loader(params) is False

    def test_does_not_match_github(self, tmp_path: Path) -> None:
        params = self._make_params("github.com/org/repo", tmp_path)
        assert self.loader._is_matching_loader(params) is False

    def test_does_not_match_registry(self, tmp_path: Path) -> None:
        params = self._make_params("terraform-aws-modules/security-group/aws", tmp_path)
        assert self.loader._is_matching_loader(params) is False

    def test_does_not_match_local(self, tmp_path: Path) -> None:
        params = self._make_params("./modules/vpc", tmp_path)
        assert self.loader._is_matching_loader(params) is False


class TestS3LoaderProcessSource:
    """Test the _process_s3_source method for inner module handling."""

    def setup_method(self) -> None:
        self.loader = S3Loader()

    def _make_params(self, source: str, tmp_path: Path) -> ModuleParams:
        return ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source=source,
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
        )

    def test_simple_source_no_inner_module(self, tmp_path: Path) -> None:
        params = self._make_params("s3::https://s3-eu-west-1.amazonaws.com/bucket/module.zip", tmp_path)
        self.loader._process_s3_source(params)
        assert params.inner_module is None
        assert "s3-eu-west-1.amazonaws.com" in params.dest_dir
        assert "bucket" in params.dest_dir

    def test_source_with_inner_module(self, tmp_path: Path) -> None:
        params = self._make_params(
            "s3::https://s3-eu-west-1.amazonaws.com/bucket/module.zip//modules/vpc", tmp_path
        )
        self.loader._process_s3_source(params)
        assert params.inner_module == "modules/vpc"
        assert params.module_source == "s3::https://s3-eu-west-1.amazonaws.com/bucket/module.zip"

    def test_dest_dir_strips_archive_extension(self, tmp_path: Path) -> None:
        params = self._make_params("s3::https://s3.amazonaws.com/bucket/modules/vpc.zip", tmp_path)
        self.loader._process_s3_source(params)
        assert not params.dest_dir.endswith(".zip")
        assert "vpc" in params.dest_dir


class TestS3LoaderFindModulePath:
    """Test the _find_module_path method."""

    def setup_method(self) -> None:
        self.loader = S3Loader()

    def test_find_module_path_simple(self, tmp_path: Path) -> None:
        params = ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source="s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip",
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
        )
        path = self.loader._find_module_path(params)
        assert ".external_modules" in path
        assert "s3-eu-west-1.amazonaws.com" in path
        assert "bucket" in path
        assert "vpc" in path
        assert not path.endswith(".zip")

    def test_find_module_path_with_inner_module(self, tmp_path: Path) -> None:
        params = ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source="s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip",
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
            inner_module="submodules/network",
        )
        path = self.loader._find_module_path(params)
        assert path.endswith("submodules/network")


class TestS3LoaderLoadModule:
    """Test the _load_module method with mocked S3Getter."""

    @mock.patch("checkov.terraform.module_loading.loaders.s3_loader.S3Getter")
    def test_load_module_success(self, mock_s3_getter_cls: mock.MagicMock, tmp_path: Path) -> None:
        # given
        loader = S3Loader()
        params = ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source="s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip",
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
        )

        mock_getter_instance = mock.MagicMock()
        mock_s3_getter_cls.return_value = mock_getter_instance

        # when
        content = loader._load_module(params)

        # then
        mock_s3_getter_cls.assert_called_once_with(
            "https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip",
            create_clone_and_result_dirs=False,
        )
        mock_getter_instance.do_get.assert_called_once()
        assert content.loaded()

    @mock.patch("checkov.terraform.module_loading.loaders.s3_loader.S3Getter")
    def test_load_module_with_inner_module(self, mock_s3_getter_cls: mock.MagicMock, tmp_path: Path) -> None:
        # given
        loader = S3Loader()
        params = ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source="s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip//modules/network",
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
        )

        mock_getter_instance = mock.MagicMock()
        mock_s3_getter_cls.return_value = mock_getter_instance

        # _is_matching_loader processes the source (extracts inner module, sets dest_dir)
        # This mirrors the base class load() flow
        assert loader._is_matching_loader(params) is True
        assert params.inner_module == "modules/network"
        assert params.module_source == "s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip"

        # when
        content = loader._load_module(params)

        # then
        assert content.loaded()
        # The content path should include the inner module
        assert content.path().endswith("modules/network")

    @mock.patch("checkov.terraform.module_loading.loaders.s3_loader.S3Getter")
    def test_load_module_failure(self, mock_s3_getter_cls: mock.MagicMock, tmp_path: Path) -> None:
        # given
        loader = S3Loader()
        params = ModuleParams(
            root_dir=str(tmp_path),
            current_dir=str(tmp_path),
            source="s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip",
            source_version=None,
            dest_dir=str(tmp_path / "dest"),
            external_modules_folder_name=".external_modules",
        )

        mock_getter_instance = mock.MagicMock()
        mock_s3_getter_cls.return_value = mock_getter_instance
        mock_getter_instance.do_get.side_effect = Exception("Download failed")

        # when
        content = loader._load_module(params)

        # then
        assert not content.loaded()
        assert content.failed_url == "s3::https://s3-eu-west-1.amazonaws.com/bucket/modules/vpc.zip"


class TestS3LoaderIntegrationWithRegistry:
    """Test S3 loader integration with the ModuleLoaderRegistry."""

    @mock.patch("checkov.terraform.module_loading.loaders.s3_loader.S3Getter")
    def test_registry_routes_to_s3_loader(self, mock_s3_getter_cls: mock.MagicMock, tmp_path: Path) -> None:
        # given
        registry = ModuleLoaderRegistry(download_external_modules=True)
        registry.module_content_cache = {}
        registry.root_dir = str(tmp_path)

        mock_getter_instance = mock.MagicMock()
        mock_s3_getter_cls.return_value = mock_getter_instance

        source = "s3::https://s3-eu-west-1.amazonaws.com/my-bucket/modules/vpc.zip"

        # when
        content = registry.load(current_dir=str(tmp_path), source=source, source_version="latest")

        # then
        assert content.loaded()
        mock_s3_getter_cls.assert_called_once()

    @mock.patch("checkov.terraform.module_loading.loaders.s3_loader.S3Getter")
    def test_registry_does_not_route_s3_to_other_loaders(
        self, mock_s3_getter_cls: mock.MagicMock, tmp_path: Path
    ) -> None:
        """Ensure S3 sources don't accidentally match git or registry loaders."""
        # given
        registry = ModuleLoaderRegistry(download_external_modules=True)
        registry.module_content_cache = {}
        registry.root_dir = str(tmp_path)

        mock_getter_instance = mock.MagicMock()
        mock_s3_getter_cls.return_value = mock_getter_instance

        source = "s3::https://s3.amazonaws.com/my-bucket/modules/vpc.zip"

        # when
        content = registry.load(current_dir=str(tmp_path), source=source, source_version="latest")

        # then
        assert content.loaded()
        # S3Getter should be called, not GitGetter
        mock_s3_getter_cls.assert_called_once()


class TestS3LoaderCount:
    """Test that the S3 loader is properly registered."""

    def test_s3_loader_registered(self) -> None:
        registry = ModuleLoaderRegistry(download_external_modules=True)
        loader_types = [type(loader).__name__ for loader in registry.loaders]
        assert "S3Loader" in loader_types

    def test_loader_count_with_s3(self) -> None:
        registry = ModuleLoaderRegistry(download_external_modules=True)
        # Should be 8 loaders now (was 7 before S3Loader)
        assert len(registry.loaders) == 8
