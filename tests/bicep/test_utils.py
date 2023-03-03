from pathlib import Path

from checkov.bicep.utils import get_scannable_file_paths


def test_get_scannable_file_paths(tmp_path: Path):
    # given
    (tmp_path / "storage.json").touch()
    (tmp_path / "storage.bicep").touch()

    (tmp_path / ".bicep").mkdir()
    (tmp_path / ".bicep/main.bicep").touch()

    # when
    file_paths = get_scannable_file_paths(root_folder=tmp_path)

    # then
    assert file_paths == {
        tmp_path / "storage.bicep",
        tmp_path / ".bicep/main.bicep",
    }
