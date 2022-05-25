import re

DOCKER_FILE_MASK = re.compile(r"^(?:.+\.)?[Dd]ockerfile(?:\..+)?$")


def is_docker_file(file: str) -> bool:
    return re.fullmatch(DOCKER_FILE_MASK, file) is not None
