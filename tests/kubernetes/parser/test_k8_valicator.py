import pytest

from checkov.kubernetes.parser.validatior import K8sValidator


@pytest.fixture
def template_valid_fields():
    return {
      "apiVersion": "v1",
      "kind": "Pod",
      "metadata": {
        "name": "nginx-demo"
      },
      "spec": {
        "containers": [
          {
            "name": "nginx",
            "image": "nginx:1.14.2",
            "ports": [
              {
                "containerPort": 80
              }
            ]
          }
        ]
      }
    }


@pytest.fixture
def template_invalid_name():
    return {
      "apiVersion": "v1",
      "kind": "Pod",
      "metadata": {
        "name": "nginx-demo"
      },
      "spec": {
        "containers": [
          {
            "name": "#{nginx}",
            "image": "nginx:1.14.2",
            "ports": [
              {
                "containerPort": 80
              }
            ]
          }
        ]
      }
    }


def test_k8s_template_has_required_fields(template_valid_fields):
    is_valid, reason = K8sValidator.is_valid_template(template_valid_fields)
    assert is_valid


def test_k8s_template_is_name_valid(template_invalid_name):
    is_valid, reason = K8sValidator.is_valid_template(template_invalid_name)
    assert not is_valid
