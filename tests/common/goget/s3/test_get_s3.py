import os
from pathlib import Path
from unittest import mock

import pytest

from checkov.common.goget.s3.get_s3 import S3Getter, DEFAULT_REGION


class TestS3UrlParsing:
    """Test S3 URL parsing for various URL formats."""

    def test_path_style_with_region(self) -> None:
        url = "https://s3-eu-west-1.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "eu-west-1"

    def test_path_style_no_region(self) -> None:
        url = "https://s3.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == DEFAULT_REGION

    def test_path_style_new_format_with_region(self) -> None:
        url = "https://s3.eu-west-1.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "eu-west-1"

    def test_path_style_us_east_1(self) -> None:
        url = "https://s3-us-east-1.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "us-east-1"

    def test_virtual_hosted_style_with_region(self) -> None:
        url = "https://my-bucket.s3-eu-west-1.amazonaws.com/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "eu-west-1"

    def test_virtual_hosted_style_new_format_with_region(self) -> None:
        url = "https://my-bucket.s3.eu-west-1.amazonaws.com/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "eu-west-1"

    def test_virtual_hosted_style_no_region(self) -> None:
        url = "https://my-bucket.s3.amazonaws.com/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == DEFAULT_REGION

    def test_virtual_hosted_style_dotted_bucket_name(self) -> None:
        url = "https://my.bucket.name.s3.eu-west-1.amazonaws.com/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my.bucket.name"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "eu-west-1"

    def test_virtual_hosted_style_dotted_bucket_no_region(self) -> None:
        url = "https://my.bucket.name.s3.amazonaws.com/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my.bucket.name"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == DEFAULT_REGION

    def test_nested_key_path(self) -> None:
        url = "https://s3-eu-west-1.amazonaws.com/my-bucket/path/to/modules/vpc.tar.gz"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "path/to/modules/vpc.tar.gz"
        assert getter.region == "eu-west-1"

    @mock.patch.dict(os.environ, {"S3_MODULE_AWS_REGION": "ap-southeast-1"})
    def test_region_override_via_env_var(self) -> None:
        url = "https://s3.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        assert getter.bucket == "my-bucket"
        assert getter.key == "modules/vpc.zip"
        assert getter.region == "ap-southeast-1"

    def test_invalid_url_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Unable to parse S3 URL"):
            S3Getter("https://example.com/not-an-s3-url")


class TestS3GetterArchiveExtension:
    """Test archive extension detection."""

    @pytest.mark.parametrize(
        "key, expected_extension",
        [
            ("modules/vpc.zip", "zip"),
            ("modules/vpc.tar.gz", "tar.gz"),
            ("modules/vpc.tar.bz2", "tar.bz2"),
            ("modules/vpc.tgz", "tgz"),
            ("modules/vpc.tar.xz", "tar.xz"),
            ("modules/vpc.txz", "txz"),
            ("modules/vpc.txt", None),
            ("modules/vpc", None),
        ],
        ids=["zip", "tar.gz", "tar.bz2", "tgz", "tar.xz", "txz", "unsupported", "no_extension"],
    )
    def test_archive_extension_detection(self, key: str, expected_extension: str) -> None:
        url = f"https://s3.amazonaws.com/my-bucket/{key}"
        getter = S3Getter(url)
        assert getter._get_archive_extension() == expected_extension


class TestS3GetterDoGet:
    """Test the do_get method with mocked boto3."""

    @mock.patch("checkov.common.goget.s3.get_s3.boto3")
    @mock.patch("checkov.common.goget.s3.get_s3.extract_zip_archive")
    def test_do_get_zip(self, mock_extract_zip: mock.MagicMock, mock_boto3: mock.MagicMock, tmp_path: Path) -> None:
        # given
        url = "https://s3-eu-west-1.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        getter.temp_dir = str(tmp_path)

        mock_session = mock.MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_s3_client = mock.MagicMock()
        mock_session.client.return_value = mock_s3_client

        # Create a dummy file to simulate download
        download_path = tmp_path / "module_source.zip"
        download_path.touch()

        # when
        result = getter.do_get()

        # then
        assert result == str(tmp_path)
        mock_boto3.Session.assert_called_once_with(region_name="eu-west-1", profile_name=None)
        mock_session.client.assert_called_once_with("s3")
        mock_s3_client.download_file.assert_called_once_with(
            "my-bucket", "modules/vpc.zip", str(download_path)
        )
        mock_extract_zip.assert_called_once_with(
            source_path=str(download_path), dest_path=str(tmp_path)
        )

    @mock.patch("checkov.common.goget.s3.get_s3.boto3")
    @mock.patch("checkov.common.goget.s3.get_s3.extract_tar_archive")
    def test_do_get_tar_gz(self, mock_extract_tar: mock.MagicMock, mock_boto3: mock.MagicMock, tmp_path: Path) -> None:
        # given
        url = "https://s3-eu-west-1.amazonaws.com/my-bucket/modules/vpc.tar.gz"
        getter = S3Getter(url)
        getter.temp_dir = str(tmp_path)

        mock_session = mock.MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_s3_client = mock.MagicMock()
        mock_session.client.return_value = mock_s3_client

        # Create a dummy file to simulate download
        download_path = tmp_path / "module_source.tar.gz"
        download_path.touch()

        # when
        result = getter.do_get()

        # then
        assert result == str(tmp_path)
        mock_extract_tar.assert_called_once_with(
            source_path=str(download_path), dest_path=str(tmp_path)
        )

    @mock.patch.dict(os.environ, {"AWS_PROFILE": "my-profile"})
    @mock.patch("checkov.common.goget.s3.get_s3.boto3")
    @mock.patch("checkov.common.goget.s3.get_s3.extract_zip_archive")
    def test_do_get_with_aws_profile(
        self, mock_extract_zip: mock.MagicMock, mock_boto3: mock.MagicMock, tmp_path: Path
    ) -> None:
        # given
        url = "https://s3.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        getter.temp_dir = str(tmp_path)

        mock_session = mock.MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_s3_client = mock.MagicMock()
        mock_session.client.return_value = mock_s3_client

        download_path = tmp_path / "module_source.zip"
        download_path.touch()

        # when
        getter.do_get()

        # then
        mock_boto3.Session.assert_called_once_with(region_name=DEFAULT_REGION, profile_name="my-profile")

    def test_do_get_unsupported_format_raises_error(self, tmp_path: Path) -> None:
        url = "https://s3.amazonaws.com/my-bucket/modules/vpc.txt"
        getter = S3Getter(url)
        getter.temp_dir = str(tmp_path)

        with pytest.raises(ValueError, match="Unsupported archive format"):
            getter.do_get()

    @mock.patch("checkov.common.goget.s3.get_s3.boto3")
    def test_do_get_no_credentials(self, mock_boto3: mock.MagicMock, tmp_path: Path) -> None:
        from botocore.exceptions import NoCredentialsError

        url = "https://s3.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        getter.temp_dir = str(tmp_path)

        mock_session = mock.MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_s3_client = mock.MagicMock()
        mock_session.client.return_value = mock_s3_client
        mock_s3_client.download_file.side_effect = NoCredentialsError()

        with pytest.raises(NoCredentialsError):
            getter.do_get()

    @mock.patch("checkov.common.goget.s3.get_s3.boto3")
    def test_do_get_client_error(self, mock_boto3: mock.MagicMock, tmp_path: Path) -> None:
        from botocore.exceptions import ClientError

        url = "https://s3.amazonaws.com/my-bucket/modules/vpc.zip"
        getter = S3Getter(url)
        getter.temp_dir = str(tmp_path)

        mock_session = mock.MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_s3_client = mock.MagicMock()
        mock_session.client.return_value = mock_s3_client
        mock_s3_client.download_file.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}}, "GetObject"
        )

        with pytest.raises(ClientError):
            getter.do_get()
