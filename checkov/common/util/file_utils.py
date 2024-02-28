from __future__ import annotations

import os.path
import tarfile
import base64
import gzip
import io
import logging
from pathlib import Path
from typing import Dict
from zipfile import ZipFile

from charset_normalizer import from_path

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def convert_to_unix_path(path: str) -> str:
    return path.replace('\\', '/')


def extract_tar_archive(source_path: str, dest_path: str) -> None:
    with tarfile.open(source_path) as tar:
        tar.extractall(path=dest_path)  # nosec  # only trusted source


def extract_zip_archive(source_path: str, dest_path: str) -> None:
    with ZipFile(source_path) as zip:
        zip.extractall(path=dest_path)  # nosec  # only trusted source


def compress_file_gzip_base64(input_path: str) -> str:
    try:
        with open(input_path, 'rb') as json_results_file:
            data = json_results_file.read()
        zip_file = gzip.compress(data)  # to gzip - return in bytes
        base64_bytes = base64.b64encode(zip_file)  # to base64
        base64_string = base64_bytes.decode("utf-8")
        return base64_string
    except Exception:
        logging.exception("failed to open and load results file")
        raise


def decompress_file_gzip_base64(compressed_file_body: str) -> bytes:
    try:
        # 1. convert string to bytes
        # 2. decode base64 data
        # 3. wrap decoded binary data with BytesIO to enable reading
        # 4. gunzip compressed data
        base64_bytes = compressed_file_body.encode("utf-8")
        decoded_base64 = base64.b64decode(base64_bytes)
        with gzip.open(io.BytesIO(decoded_base64), 'rb') as file_extracted_body:
            return file_extracted_body.read()
    except Exception:
        logging.exception("failed to extract package file")
        raise


def compress_string_io_tar(string_io: io.StringIO) -> io.BytesIO:
    file_io = io.BytesIO()
    str_data = string_io.getvalue().encode('utf8')
    bio = io.BytesIO(str_data)
    try:
        with tarfile.open(fileobj=file_io, mode='w:gz') as tar:
            info = tar.tarinfo(name='logs_file.txt')
            bio.seek(0)
            info.size = string_io.tell()
            tar.addfile(info, bio)
        file_io.seek(0)
        return file_io
    except Exception:
        logging.exception("failed to compress logging file")
        raise


def compress_multiple_strings_ios_tar(logs_streams: Dict[str, io.StringIO]) -> io.BytesIO:
    tar_stream = io.BytesIO()
    try:
        with tarfile.open(fileobj=tar_stream, mode='w:gz') as tar:
            for filename, stringio in logs_streams.items():
                bytes_io = io.BytesIO(stringio.getvalue().encode())

                tarinfo = tarfile.TarInfo(name=f'{filename}.log')
                tarinfo.size = len(bytes_io.getvalue())

                bytes_io.seek(0)
                tar.addfile(tarinfo, fileobj=bytes_io)

        tar_stream.seek(0)
        return tar_stream
    except Exception:
        logging.exception("failed to compress logging file")
        raise


def read_file_safe(file_path: str) -> str:
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content
    except Exception:
        logging.warning(
            "Could not open file",
            extra={"file_path": file_path}
        )
        return ""


def get_file_size_safe(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logging.warning(
            f"Could not obtain file size, {str(e)}",
            extra={"file_path": file_path}
        )
        return -1


def read_file_with_any_encoding(file_path: str | Path) -> str:
    """Read the file with the system encoding and then try to detect it"""

    file_path = file_path if isinstance(file_path, Path) else Path(file_path)

    try:
        content = file_path.read_text()
    except UnicodeDecodeError:
        logger.info(f"Encoding for file {file_path} is not UTF-8, trying to detect it")
        content = str(from_path(file_path).best())

    return content
