import re

DOCKERFILE_MASK = re.compile(r"^(?:.+\.)?(?:[Dd]ockerfile|[Cc]ontainerfile)(?:\..+)?$(?<!\.[Dd]ockerignore)")


def is_dockerfile(file: str) -> bool:
    if "ockerfile" not in file and "ontainerfile" not in file:
        # no need to check the full regex, if neither 'ockerfile' nor 'ontainerfile' could be found
        return False
    return re.fullmatch(DOCKERFILE_MASK, file) is not None
