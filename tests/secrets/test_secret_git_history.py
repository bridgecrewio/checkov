from __future__ import annotations

import random
import string

from typing import Dict
from unittest import mock

from detect_secrets import SecretsCollection


from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter
from detect_secrets.settings import transient_settings
from checkov.common.output.secrets_record import COMMIT_REMOVED_STR, COMMIT_ADDED_STR

from checkov.secrets.scan_git_history import GitHistoryScanner


def mock_git_repo_commits1(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    """
        add secret (secret1 added) - +1
        move the secret to different line - 0
        modify the secret value (secret1 removed=update + secret2 added) - +1
        remove the secret (secret2 removed=update) - 0
        add file with new secret (secret3 added) - +1
    """
    return {
        "8a21fa691e17907afee57e93b7820c5943b12746":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -4,6 +4,8 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n COPY Pipfile Pipfile.lock ./\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n"
            },
        "d3249f33376b94a939b67a638aba4557b071875f":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,10 +1,9 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n COPY Pipfile Pipfile.lock ./\n \n"
            },
        "3d79bba03c6f0ddcfb8334f531701942c4be0f32":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,7 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n \n"
            },
        "7dff3b21fc2563f51655f34f0d3601cdf79d0d5e":
            {
                "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,7 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n \n"
            },
        "6941281550a12659bdbe87c9a537f88124f78fac":
            {
                "main.py": "diff --git a/None b/main.py\nindex 0000..0000 0000\n--- a/None\n+++ b/main.py\n@@ -0,0 +1,4 @@\n+AWS_ACCESS_TOKEN=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n+if __name__ == \"__main__\":\n+    print(AWS_ACCESS_TOKEN)\n\\ No newline at end of file\n"
            }
    }


def mock_git_repo_commits2(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    """
        add secret (secret1 added) - +1
        move the secret to different line - 0
        remove the secret (secret1 removed=update) - 0
        add secret (secret1 added - add the same secret - update) - 0
        move the secret to different line - 0
    """
    return {
        "11e59e4e578c6ebcb48aae1e5e078a54c62920eb": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -5,7 +5,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "c7c932ef4d31c487a921d2ce8544a4a468adf6b9": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -2,10 +2,10 @@\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n \n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "4b8321e46217a87e21240afd88cdc0f1a861c0f5": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -2,7 +2,6 @@\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n \n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n \n"
        },
        "7bb5c69d95b31bc2242bcf08ce25e74e953f9ae9": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -4,7 +4,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "2675bffd2662aae7025b7f3bb5fd384cdab355b1": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -1,10 +1,11 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        }
    }


def mock_git_repo_commits3(root_folder: str) -> Dict[str, Dict[str, str]]:
    """
            add secret (secret1 added) - +1
            move the secret to different line - 0
            add secret equal to secret1 - +1
            remove one secret (secret1 - update add remove_commit_hash) - 0
        """
    return {
        "900b1e8f6f336a92e8f5fca3babca764e32c3b3d": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -1,6 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n"
        },
        "4229974aec78152c426b40db8b6912ba098f3add": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -1,11 +1,11 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        },
        "3c8cb7eedb3986308c96713fc65b006adcf3bc44": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -6,7 +6,7 @@ FROM public.ecr.aws/lambda/python:3.9\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n-\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n  && pipenv run pip install -r requirements.txt --target \"${LAMBDA_TASK_ROOT}\" \\\n"
        },
        "697308e61171e33224757e620aaf67b1a877c99d": {
            "folder1/folder2/Dockerfile": "diff --git a/folder1/folder2/Dockerfile b/folder1/folder2/Dockerfile\nindex 0000..0000 0000\n--- a/folder1/folder2/Dockerfile\n+++ b/folder1/folder2/Dockerfile\n@@ -5,7 +5,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n COPY Pipfile Pipfile.lock ./\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && pipenv lock -r > requirements.txt \\\n"
        }
    }


def mock_git_repo_commits_remove_file(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
        "63342dbee285973a37770bbb1ff4258a3184901e": {
            "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -4,6 +4,7 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n COPY Pipfile Pipfile.lock ./\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n"
        },
        "bca377900d08d442b1080893e50b8dc8276cfcc0": {
            "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -13,6 +13,7 @@ RUN pip install pipenv==${PIP_ENV_VERSION} \\\n  && rm -f requirements.txt Pipfile Pipfile.lock \\\n  && pip uninstall -y pipenv\n \n+\n COPY src/ \"${LAMBDA_TASK_ROOT}/src/\"\n COPY utilsPython/ \"${LAMBDA_TASK_ROOT}/utilsPython/\"\n \n"
        },
        "4bd08cd0b2874025ce32d0b1e9cd84ca20d59ce1": {
            "Dockerfile": "diff --git a/Dockerfile b/None\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/None\n@@ -1,20 +0,0 @@\n-#checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n-#checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n-FROM public.ecr.aws/lambda/python:3.9\n-\n-ENV PIP_ENV_VERSION=\"2022.1.8\"\n-\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n-COPY Pipfile Pipfile.lock ./\n-\n-RUN pip install pipenv==${PIP_ENV_VERSION} \\\n- && pipenv lock -r > requirements.txt \\\n- && pipenv run pip install -r requirements.txt --target \"${LAMBDA_TASK_ROOT}\" \\\n- && rm -f requirements.txt Pipfile Pipfile.lock \\\n- && pip uninstall -y pipenv\n-\n-\n-COPY src/ \"${LAMBDA_TASK_ROOT}/src/\"\n-COPY utilsPython/ \"${LAMBDA_TASK_ROOT}/utilsPython/\"\n-\n-CMD [\"src.secrets_setup.image.src.app.handler\"]\n"
        }
    }


def mock_remove_file_with_two_equal_secret(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
        "d76977ac656abdaa77a7791a11adfb96efb48a35": {
            "test3.py": "diff --git a/test3.py b/test3.py\nindex 0000..0000 0000\n--- a/test3.py\n+++ b/test3.py\n@@ -1,4 +1,4 @@\n-\n+AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n \n if __name__ == '__main__':\n     print('test')\n"
        },
        "c211bfc4ae4514627f104ce0bf664dd9521d9c16": {
            "test3.py": "diff --git a/test3.py b/test3.py\nindex 0000..0000 0000\n--- a/test3.py\n+++ b/test3.py\n@@ -1,4 +1,5 @@\n AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n \n if __name__ == '__main__':\n+    AWS_ACCESS_KEY_ID = \"AKIAZZZZZZZZZZZZZZZZ\"\n     print('test')\n"
        },
        "8d96e18c1c924ba396211bf2d4fdd8d2418b8420": {
            "test3.py": "diff --git a/test3.py b/None\nindex 0000..0000 0000\n--- a/test3.py\n+++ b/None\n@@ -1,5 +0,0 @@\n-AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n-\n-if __name__ == '__main__':\n-    AWS_ACCESS_KEY_ID = \"AKIAZZZZZZZZZZZZZZZZ\"\n-    print('test')\n"
        }
    }


def mock_remove_file_with_two_secret(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
        "f0d117c1d65e90d4d6d7a1b6aaf4e23f4fd33b82": {
            "main.py": "diff --git a/main.py b/main.py\nindex 0000..0000 0000\n--- a/main.py\n+++ b/main.py\n@@ -1,3 +1,4 @@\n+AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n if __name__ == '__main__':\n \n"
        },
        "1166ee830a03f6721fb8cba794496ee82895a0ba": {
            "main.py": "diff --git a/main.py b/main.py\nindex 0000..0000 0000\n--- a/main.py\n+++ b/main.py\n@@ -1,5 +1,5 @@\n AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n if __name__ == '__main__':\n-\n+    TEST_PASSWORD_1 = \"Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE\"\n     print('test')\n"
        },
        "bdb3678fc44702132fa7d661a1c425e65c1e9dde": {
            "main.py": "diff --git a/main.py b/None\nindex 0000..0000 0000\n--- a/main.py\n+++ b/None\n@@ -1,5 +0,0 @@\n-AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n-\n-if __name__ == '__main__':\n-    TEST_PASSWORD_1 = \"Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE\"\n-    print('test')\n"
        }
    }


def mock_git_repo_commits_rename_file(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
        "adef7360b86c62666f0a70521214220763b9c593": {
            "main.py": "diff --git a/main.py b/main.py\nindex 0000..0000 0000\n--- a/main.py\n+++ b/main.py\n@@ -1,3 +1,3 @@\n-\n+AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n if __name__ == '__main__':\n     print('test')\n"
        },
        "7b12f891358f690f254476c80988bfa837f36ac6": {
            "main.py": "diff --git a/main.py b/main.py\nindex 0000..0000 0000\n--- a/main.py\n+++ b/main.py\n@@ -1,3 +1,4 @@\n AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n if __name__ == '__main__':\n     print('test')\n"
        },
        "2e1a500e688990e065fc6f1202bc64ed0ba53027": {
            "main.py": {
                "rename_from": "main.py",
                "rename_to": "test.py"
            }
        }
    }


def mock_git_repo_commits_modify_and_rename_file(root_folder: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    """
    when we rename a file and modify it in the same commit it will consider as deleting the old file and creating a new file
    add secret to file +1
    rename the file and removed the secret- add removed_commit_hash
    """
    return {
        "62da8e5e04ec5c3a474467e9012bf3427cff0407": {
            "test.py": "diff --git a/test.py b/test.py\nindex 0000..0000 0000\n--- a/test.py\n+++ b/test.py\n@@ -1,4 +1,4 @@\n-\n+AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n if __name__ == '__main__':\n     print('test')\n"
        },
        "61ee79aea3d151a40c8e054295f330d233eaf7d5": {
            "test.py": "diff --git a/test.py b/None\nindex 0000..0000 0000\n--- a/test.py\n+++ b/None\n@@ -1,4 +0,0 @@\n-AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n-\n-if __name__ == '__main__':\n-    print('test')\n",
            "None": "diff --git a/None b/test2.py\nindex 0000..0000 0000\n--- a/None\n+++ b/test2.py\n@@ -0,0 +1,3 @@\n+\n+if __name__ == '__main__':\n+    print('test')\n"
        }
    }


def get_random_string(length: int) -> str:
    chars = string.ascii_lowercase + string.ascii_letters
    result_str = ''.join(random.choice(chars) for _i in range(length))
    return result_str


def mock_case() -> Dict[str, str]:
    cases = [
        {
            "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -4,6 +4,8 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+\n COPY Pipfile Pipfile.lock ./\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n"
        },
        {
            "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,10 +1,9 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-\n+ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n \n COPY Pipfile Pipfile.lock ./\n \n"
        },
        {
            "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,7 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"\n+ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n \n"
        },
        {
            "Dockerfile": "diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -1,7 +1,7 @@\n #checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers\n #checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime\n FROM public.ecr.aws/lambda/python:3.9\n-ENV AWS_ACCESS_KEY_ID=\"AKIAZZZZZZZZZZZZZZZZ\"\n+\n ENV PIP_ENV_VERSION=\"2022.1.8\"\n \n \n"
        }
    ]
    return random.choice(cases)


def mock_git_repo_commits_too_much(root_folder: str) -> Dict[str, Dict[str, str]]:
    res: Dict[str, Dict[str, str]] = {}
    keys = [get_random_string(40) for _i in range(10000)]
    for k in keys:
        res[k] = mock_case()
    return res


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits1)
def test_scan_git_history() -> None:
    valid_dir_path = "test"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 3
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0
    for failed_check in report.failed_checks:
        assert failed_check.added_commit_hash or failed_check.removed_commit_hash


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits1)
def test_scan_history_secrets() -> None:
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        GitHistoryScanner(valid_dir_path, secrets).scan_history()
    assert len(secrets.data) == 3


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits2)
def test_scan_git_history_merge_added_removed() -> None:
    """
    add, move, remove, add, move = secret with the first added_commit_hash and not removed_commit_hash
    """
    valid_dir_path = "test"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 1
    for failed_check in report.failed_checks:
        assert failed_check.removed_commit_hash is None
        assert failed_check.added_commit_hash == '11e59e4e578c6ebcb48aae1e5e078a54c62920eb'


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits2)
def test_scan_history_secrets_merge_added_removed() -> None:
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        GitHistoryScanner(valid_dir_path, secrets).scan_history()
    assert len(secrets.data) == 1


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits3)
def test_scan_git_history_merge_added_removed2() -> None:
    """
        add, move, add, remove one = 2 secret one with removed_commit_hash && added_commit_hash
        and one with only added_commit_hash
    """
    valid_dir_path = "/Users/lshindelman/development/test2"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert ((report.failed_checks[0].removed_commit_hash == '697308e61171e33224757e620aaf67b1a877c99d'
             and report.failed_checks[1].removed_commit_hash is None)
            or (report.failed_checks[1].removed_commit_hash == '697308e61171e33224757e620aaf67b1a877c99d'
                and report.failed_checks[0].removed_commit_hash is None))
    assert ((report.failed_checks[0].added_commit_hash == '900b1e8f6f336a92e8f5fca3babca764e32c3b3d'
             and report.failed_checks[1].added_commit_hash == '3c8cb7eedb3986308c96713fc65b006adcf3bc44')
            or (report.failed_checks[1].added_commit_hash == '900b1e8f6f336a92e8f5fca3babca764e32c3b3d'
                and report.failed_checks[0].added_commit_hash == '3c8cb7eedb3986308c96713fc65b006adcf3bc44'))
    # print testing
    assert_for_commit_str(report.failed_checks[0].to_string() + report.failed_checks[1].to_string(),
                          commit_type=COMMIT_REMOVED_STR,
                          commit_hash='697308e61171e33224757e620aaf67b1a877c99d')
    assert_for_commit_str(report.failed_checks[0].to_string() + report.failed_checks[1].to_string(),
                          commit_type=COMMIT_ADDED_STR,
                          commit_hash='3c8cb7eedb3986308c96713fc65b006adcf3bc44')
    assert_for_commit_str(report.failed_checks[0].to_string() + report.failed_checks[1].to_string(),
                          commit_type=COMMIT_ADDED_STR,
                          commit_hash='900b1e8f6f336a92e8f5fca3babca764e32c3b3d')


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits_too_much)
def test_scan_history_secrets_timeout() -> None:
    """
    add way too many cases to check in 1 second
    """
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        finished = GitHistoryScanner(valid_dir_path, secrets, 1).scan_history()

    assert finished is False


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits_remove_file)
def test_scan_git_history_remove_file() -> None:
    valid_dir_path = "remove_file"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 1
    assert (report.failed_checks[0].removed_commit_hash == '4bd08cd0b2874025ce32d0b1e9cd84ca20d59ce1' and
            report.failed_checks[0].added_commit_hash == '63342dbee285973a37770bbb1ff4258a3184901e')


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits_rename_file)
def test_scan_git_history_rename_file() -> None:
    valid_dir_path = "/test/git/history/rename/file"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert (report.failed_checks[0].removed_commit_hash is None and
            report.failed_checks[0].added_commit_hash == '2e1a500e688990e065fc6f1202bc64ed0ba53027')
    assert (report.failed_checks[1].removed_commit_hash == '2e1a500e688990e065fc6f1202bc64ed0ba53027' and
            report.failed_checks[1].added_commit_hash == 'adef7360b86c62666f0a70521214220763b9c593')


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits_modify_and_rename_file)
def test_scan_git_history_modify_and_rename_file() -> None:
    valid_dir_path = "test_scan_git_history_modify_and_rename_file"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 1
    assert (report.failed_checks[0].removed_commit_hash == '61ee79aea3d151a40c8e054295f330d233eaf7d5' and
            report.failed_checks[0].added_commit_hash == '62da8e5e04ec5c3a474467e9012bf3427cff0407')


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_remove_file_with_two_equal_secret)
def test_scan_git_history_rename_file_with_two_equal_secrets() -> None:
    valid_dir_path = "test_scan_git_history_rename_file_with_two_equal_secrets"
    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert (report.failed_checks[0].removed_commit_hash == report.failed_checks[1].removed_commit_hash and
            report.failed_checks[1].removed_commit_hash is not None)


@mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_remove_file_with_two_secret)
def test_scan_git_history_rename_file_with_two_secrets() -> None:
    valid_dir_path = "test_scan_git_history_rename_file_with_two_secrets"
    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert (report.failed_checks[0].removed_commit_hash == report.failed_checks[1].removed_commit_hash and
            report.failed_checks[1].removed_commit_hash is not None)


def assert_for_commit_str(report_str: [str], commit_type: str, commit_hash: str, found: bool = True) -> None:
    to_find = f'; {commit_type}: {commit_hash}'
    assert (to_find in report_str) == found
