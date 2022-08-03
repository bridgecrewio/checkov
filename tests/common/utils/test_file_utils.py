from pathlib import Path
import os

from checkov.common.util.file_utils import compress_file_gzip_base64


EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_compress_file_gzip_base64_is_deterministic():
    # given
    input_file = os.path.join(EXAMPLES_DIR, 'requirements.txt')
    expected_compression_output = "H4sIAAAAAAAC/0vJSsxLz7e1NdQz4krLSSzOtrU10DPjKkotLE0tLim2tTXSMzLTM+ACAGAyEUwoAAAA"

    # when
    compression_output = compress_file_gzip_base64(input_file)

    # then
    assert compression_output == expected_compression_output
