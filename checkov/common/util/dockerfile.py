import re

DOCKER_FILE_MASK = re.compile(r"^(?:.+\.)?[Dd]ockerfile(?:\..+)?$(?<!\.[Dd]ockerignore)")


def is_dockerfile(file: str) -> bool:
    return re.fullmatch(DOCKER_FILE_MASK, file) is not None
