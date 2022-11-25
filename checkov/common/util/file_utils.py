import tarfile
import base64
import gzip
import io
import logging


def convert_to_unix_path(path: str) -> str:
    return path.replace('\\', '/')


def extract_tar_archive(source_path: str, dest_path: str) -> None:
    with tarfile.open(source_path) as tar:
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=dest_path)


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
