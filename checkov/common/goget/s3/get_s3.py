from __future__ import annotations

import logging
import os
import re
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from checkov.common.goget.base_getter import BaseGetter
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.file_utils import extract_tar_archive, extract_zip_archive

# Regex patterns for parsing S3 URLs
# Path-style: https://s3-<region>.amazonaws.com/<bucket>/<key>
# Path-style (no region): https://s3.amazonaws.com/<bucket>/<key>
# Path-style (new format): https://s3.<region>.amazonaws.com/<bucket>/<key>
# Virtual-hosted-style: https://<bucket>.s3-<region>.amazonaws.com/<key>
# Virtual-hosted-style (new format): https://<bucket>.s3.<region>.amazonaws.com/<key>
# Virtual-hosted-style (no region): https://<bucket>.s3.amazonaws.com/<key>

PATH_STYLE_PATTERN = re.compile(
    r"https?://s3[.-](?P<region>[a-z0-9-]+)?\.?amazonaws\.com/(?P<bucket>[^/]+)/(?P<key>.+)"
)
PATH_STYLE_NO_REGION_PATTERN = re.compile(
    r"https?://s3\.amazonaws\.com/(?P<bucket>[^/]+)/(?P<key>.+)"
)
VIRTUAL_HOSTED_PATTERN = re.compile(
    r"https?://(?P<bucket>.+)\.s3[.-](?P<region>[a-z0-9-]+)?\.?amazonaws\.com/(?P<key>.+)"
)
VIRTUAL_HOSTED_NO_REGION_PATTERN = re.compile(
    r"https?://(?P<bucket>.+)\.s3\.amazonaws\.com/(?P<key>.+)"
)

# Supported archive extensions (same as registry loader)
ARCHIVE_EXTENSIONS = ["zip", "tar.bz2", "tar.gz", "tgz", "tar.xz", "txz"]

DEFAULT_REGION = "us-east-1"


class S3Getter(BaseGetter):
    def __init__(self, url: str, create_clone_and_result_dirs: bool = False) -> None:
        self.logger = logging.getLogger(__name__)
        add_resource_code_filter_to_logger(self.logger)
        self.create_clone_and_res_dirs = create_clone_and_result_dirs
        self.bucket: str = ""
        self.key: str = ""
        self.region: str = DEFAULT_REGION
        super().__init__(url)
        self._parse_s3_url(url)

    def _parse_s3_url(self, url: str) -> None:
        """Parse an S3 HTTP URL to extract bucket, key, and region.

        Supports both path-style and virtual-hosted-style URLs.
        """
        # Try path-style with no region first (more specific match)
        match = PATH_STYLE_NO_REGION_PATTERN.match(url)
        if match:
            self.bucket = match.group("bucket")
            self.key = match.group("key")
            self.region = os.getenv("S3_MODULE_AWS_REGION", DEFAULT_REGION)
            return

        # Try path-style with region
        match = PATH_STYLE_PATTERN.match(url)
        if match:
            self.bucket = match.group("bucket")
            self.key = match.group("key")
            region = match.group("region")
            if region and region not in ("amazonaws", ""):
                self.region = region
            else:
                self.region = os.getenv("S3_MODULE_AWS_REGION", DEFAULT_REGION)
            return

        # Try virtual-hosted-style with no region
        match = VIRTUAL_HOSTED_NO_REGION_PATTERN.match(url)
        if match:
            self.bucket = match.group("bucket")
            self.key = match.group("key")
            self.region = os.getenv("S3_MODULE_AWS_REGION", DEFAULT_REGION)
            return

        # Try virtual-hosted-style with region
        match = VIRTUAL_HOSTED_PATTERN.match(url)
        if match:
            self.bucket = match.group("bucket")
            self.key = match.group("key")
            region = match.group("region")
            if region and region not in ("amazonaws", ""):
                self.region = region
            else:
                self.region = os.getenv("S3_MODULE_AWS_REGION", DEFAULT_REGION)
            return

        raise ValueError(f"Unable to parse S3 URL: {url}")

    def do_get(self) -> str:
        """Download the S3 object and extract it to the destination directory."""
        dest_path = self.temp_dir
        archive_extension = self._get_archive_extension()

        if not archive_extension:
            raise ValueError(
                f"Unsupported archive format for S3 module source: {self.key}. "
                f"Supported formats: {', '.join(ARCHIVE_EXTENSIONS)}"
            )

        download_path = os.path.join(dest_path, f"module_source.{archive_extension}")

        try:
            aws_profile = os.getenv("AWS_PROFILE")
            session = boto3.Session(
                region_name=self.region,
                profile_name=aws_profile if aws_profile else None,
            )
            s3_client = session.client("s3")

            os.makedirs(dest_path, exist_ok=True)
            self.logger.debug(f"Downloading s3://{self.bucket}/{self.key} to {download_path}")
            s3_client.download_file(self.bucket, self.key, download_path)
        except NoCredentialsError:
            self.logger.warning(
                "AWS credentials not found. Please configure AWS credentials to download S3 modules. "
                "See https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html"
            )
            raise
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            self.logger.warning(
                f"Failed to download s3://{self.bucket}/{self.key}: "
                f"AWS error {error_code} - {e}"
            )
            raise

        # Extract the archive
        if archive_extension == "zip":
            extract_zip_archive(source_path=download_path, dest_path=dest_path)
        else:
            extract_tar_archive(source_path=download_path, dest_path=dest_path)

        os.remove(download_path)
        return dest_path

    def _get_archive_extension(self) -> Optional[str]:
        """Determine the archive extension from the S3 key."""
        for extension in ARCHIVE_EXTENSIONS:
            if self.key.endswith(f".{extension}"):
                return extension
        return None
