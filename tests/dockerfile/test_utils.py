from checkov.common.util.dockerfile import is_docker_file

VALID_DOCKER_FILE_NAMES = ["Dockerfile", "dockerfile", "Dockerfile.prod", "Dockerfile.Product1", "dev.Dockerfile",
                           "team1.product.dockerfile"]
INVALID_DOCKER_FILE_NAMES = ["package.json", "dockerfil", "dockerfilee", ".dockerfile", "ddockerfile",
                             "ockerfile", "docker-file", "dockerfile1"]


def test_is_docker_file():
    assert all(is_docker_file(curr_name) for curr_name in VALID_DOCKER_FILE_NAMES)
    assert all(not is_docker_file(curr_name) for curr_name in INVALID_DOCKER_FILE_NAMES)
