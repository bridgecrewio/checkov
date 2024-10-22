from checkov.secrets.utils import filter_excluded_paths


def test_filter_excluded_paths():
    # given
    root_dir = "path/to"
    names = ["test", "node_modules", ".github", ".projen", ".git", "coverage", ".idea", "src"]

    # when
    filter_excluded_paths(root_dir=root_dir, names=names, excluded_paths=[])

    # then
    assert names.sort() == ["test", ".github", ".projen", "coverage", "src"].sort()


def test_filter_excluded_paths_with_extra_paths():
    # given
    root_dir = "path/to"
    names = ["test", "node_modules", ".github", ".projen", ".git", "coverage", ".idea", "src"]
    excluded_paths = [".projen'"]

    # when
    filter_excluded_paths(root_dir=root_dir, names=names, excluded_paths=excluded_paths)

    # then
    assert names.sort() == ["test", ".github", "coverage", "src"].sort()
