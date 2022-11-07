from pathlib import Path
from checkov.common.bridgecrew.platform_integration import bc_integration, FileToPersist
from checkov.sca_package_2.runner import Runner

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_upload_scannable_files():
    # when
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    input_paths = Runner().upload_scannable_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
    )

    # expected
    expected_output = [
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/requirements.txt',
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/go.sum',
                      s3_file_key='go.sum'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package-lock.json',
                      s3_file_key='package-lock.json'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package.json',
                      s3_file_key='package.json')
    ]

    # then
    assert len(input_paths) == 4

    assert input_paths == expected_output


def test_upload_scannable_files_exclude_go_and_requirements():
    # when
    input_output_paths = Runner().upload_scannable_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
        excluded_file_names={"go.sum", "package-lock.json"}
    )
    # expected
    expected_output = [
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/requirements.txt',
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package.json',
                      s3_file_key='package.json')
    ]

    # then
    assert len(input_output_paths) == 2

    assert input_output_paths == expected_output


def test_upload_scannable_files_file_config():
    # when
    input_output_paths = Runner().upload_scannable_files(
        root_path=None,
        files=['/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/requirements.txt',
               '/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/go.sum',
               '/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package-lock.json',
               '/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package.json',
               '/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/go.mod',
               ],
        excluded_paths=set(),
        excluded_file_names=set()
    )
    # expected
    expected_output = [
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/requirements.txt',
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/go.sum',
                      s3_file_key='go.sum'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package-lock.json',
                      s3_file_key='package-lock.json'),
        FileToPersist(full_file_path='/Users/ajbara/dev2/checkov/tests/sca_package_2/examples/package.json',
                      s3_file_key='package.json')
    ]

    # then
    assert len(input_output_paths) == 4

    assert input_output_paths == expected_output
