import re

DOCKERFILE_MASK = re.compile(r"^(?:.+\.)?[Dd]ockerfile(?:\..+)?$(?<!\.[Dd]ockerignore)")


def is_dockerfile(file: str) -> bool:
    return re.fullmatch(DOCKERFILE_MASK, file) is not None
