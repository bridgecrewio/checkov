import re

DOCKERFILE_MASK = re.compile(r"^(?:.+\.)?[Dd]ockerfile(?:\..+)?$(?<!\.[Dd]ockerignore)")
DOCKERFILE_IGNORE_PATTERN_ENV_VAR = "DOCKERFILE_IGNORE_PATTERN"


def is_dockerfile(file: str) -> bool:
    if "ockerfile" not in file:
        # no need to check the full regex, if 'ockerfile' couldn't be found
        return False
    return re.fullmatch(DOCKERFILE_MASK, file) is not None
