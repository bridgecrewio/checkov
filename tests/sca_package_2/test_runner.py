from pathlib import Path
from checkov.common.bridgecrew.platform_integration import bc_integration, FileToPersist
from checkov.sca_package_2.runner import Runner

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_upload_scannable_files():
    # when
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    input_paths = Runner().upload_package_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
    )

    # expected
    expected_output = {
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'requirements.txt'),
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.sum'),
                      s3_file_key='go.sum'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package-lock.json'),
                      s3_file_key='package-lock.json'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package.json'),
                      s3_file_key='package.json')
    }

    # then
    assert len(input_paths) == 4

    assert set(input_paths) == expected_output


def test_upload_scannable_files_exclude_go_and_requirements():
    # when
    input_output_paths = Runner().upload_package_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
        excluded_file_names={"go.sum", "package-lock.json"}
    )
    # expected
    expected_output = {
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'requirements.txt'),
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package.json'),
                      s3_file_key='package.json')
    }

    # then
    assert len(input_output_paths) == 2

    assert set(input_output_paths) == expected_output


def test_upload_scannable_files_file_config():
    # when
    input_output_paths = Runner().upload_package_files(
        root_path=None,
        files=[
            str(EXAMPLES_DIR / 'requirements.txt'),
            str(EXAMPLES_DIR / 'go.sum'),
            str(EXAMPLES_DIR / 'package-lock.json'),
            str(EXAMPLES_DIR / 'package.json'),
            str(EXAMPLES_DIR / 'go.mod'),
        ],
        excluded_paths=set(),
        excluded_file_names=set()
    )
    # expected
    expected_output = {
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'requirements.txt'),
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.sum'),
                      s3_file_key='go.sum'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package-lock.json'),
                      s3_file_key='package-lock.json'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package.json'),
                      s3_file_key='package.json')
    }

    # then
    assert len(input_output_paths) == 4

    assert set(input_output_paths) == expected_output
