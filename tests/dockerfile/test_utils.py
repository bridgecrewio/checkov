from checkov.dockerfile.utils import is_docker_file

VALIID_DOCKER_FILE_NAME = ["Dockerfile", "dockerfile", "Dockerfile.prod", "Dockerfile.Product1", "dev.Dockerfile",
                           "team1.product.dockerfile"]
INVALIID_DOCKER_FILE_NAME = ["package.json", "dockerfil", "dockerfilee", ".dockerfile", "ddockerfile",
                             "ockerfile", "docker-file", "dockerfile1"]


def test_is_docker_file():
    assert all(is_docker_file(curr_name) for curr_name in VALIID_DOCKER_FILE_NAME)
    assert all(not is_docker_file(curr_name) for curr_name in INVALIID_DOCKER_FILE_NAME)
