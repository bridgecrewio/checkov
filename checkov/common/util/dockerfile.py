import re
import warnings

DOCKERFILE_MASK = re.compile(r"^(?:.+\.)?[Dd]ockerfile(?:\..+)?$(?<!\.[Dd]ockerignore)")


def is_dockerfile(file: str) -> bool:
    return re.fullmatch(DOCKERFILE_MASK, file) is not None


def is_docker_file(file: str) -> bool:
    warnings.warn("Please use is_dockerfile()", DeprecationWarning)
    return is_dockerfile(file)
