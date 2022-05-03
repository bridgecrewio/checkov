import tarfile


def convert_to_unix_path(path: str) -> str:
    return path.replace('\\', '/')


def extract_tar_archive(source_path: str, dest_path: str) -> None:
    tar = tarfile.open(source_path)
    tar.extractall(path=dest_path)
    tar.close()
