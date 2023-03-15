from __future__ import annotations

import random
import string

from typing import Dict


def mock_git_repo_commits1(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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


def mock_git_repo_commits2(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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


def mock_git_repo_commits3(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str]]:
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


def mock_git_repo_commits_remove_file(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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


def mock_remove_file_with_two_equal_secret(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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


def mock_remove_file_with_two_secret(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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


def mock_git_repo_commits_rename_file(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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


def mock_git_repo_commits_modify_and_rename_file(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
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
            "test2.py": "diff --git a/None b/test2.py\nindex 0000..0000 0000\n--- a/None\n+++ b/test2.py\n@@ -0,0 +1,3 @@\n+\n+if __name__ == '__main__':\n+    print('test')\n"
        }
    }


def mock_git_repo_multiline_json(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
        "6b99e255555eacbd5f79a4efe77dcacdc63ed10f": {
            "test-multiline-secrets.json": "diff --git a/None b/test-multiline-secrets.json\nindex 0000..0000 0000\n--- a/None\n+++ b/test-multiline-secrets.json\n@@ -0,0 +1,30 @@\n+{\n+  \"spec\": [\n+    {\n+      \"name\": \"SOME_NAME\",\n+      \"value\": \"some_value\"\n+    },\n+    {\n+      \"value\": \"Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE\",\n+      \"name\": \"TEST_PASSWORD_1\",\n+      \"name1\": \"TEST_PASSWORD_2\",\n+      \"value1\": \"1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35\"\n+    },\n+    {\n+      \"name\": \"TEST_PASSWORD_3\",\n+      \"value\": \"PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h\"\n+    },\n+    {\n+      \"name\": \"TEST_PASSWORD_4\",\n+      \"value\": \"emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z\"\n+    },\n+    {\n+      \"name\": \"TEST_PASSWORD_LONG_1\",\n+      \"value\": \"m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN\"\n+    },\n+    {\n+      \"name\": \"TEST_PASSWORD_no_password\",\n+      \"value\": \"RandomP@ssw0rd\"\n+    }\n+  ]\n+}\n\\ No newline at end of file\n"
        }
    }


def mock_git_repo_multiline_terraform(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
       "6bee3eb2f69e06095395ae1d54c810c3a2a99841": {
          "secret_test.tf": "diff --git a/secret_test.tf b/secret_test.tf\nindex 0000..0000 0000\n--- a/secret_test.tf\n+++ b/secret_test.tf\n@@ -0,0 +1,79 @@\n+resource \"kubernetes_pod_v1\" \"test\" {\n+  metadata {\n+    name = \"terraform-example\"\n+  }\n+\n+  spec {\n+    container {\n+      image = \"nginx:1.21.6\"\n+      name  = \"example\"\n+\n+      env {\n+        name  = \"SOME_NAME\"\n+        value = \"some_value\"\n+      }\n+      # name1 & value1 are not valid arguments\n+      env {\n+        value  = \"Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE\"\n+        name = \"TEST_PASSWORD_1\"\n+        name1 = \"TEST_PASSWORD_2\"\n+        value1 = \"1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35\"\n+      }\n+      env {\n+        name  = \"TEST_PASSWORD_3\"\n+        // comment 1\n+        // comment 2\n+        // comment 3\n+        value = \"PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h\"\n+      }\n+      env {\n+        value = \"emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z\"\n+        # comment 1\n+        name  = \"TEST_PASSWORD_4\"\n+      }\n+      env {\n+        name  = \"TEST_PASSWORD_LONG_1\"\n+        value = \"m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN\"\n+      }\n+      env {\n+        name  = \"TEST_PASSWORD_no_password\"\n+        value = \"RandomP@ssw0rd\"\n+      }\n+\n+      port {\n+        container_port = 80\n+      }\n+\n+      liveness_probe {\n+        http_get {\n+          path = \"/\"\n+          port = 80\n+\n+          http_header {\n+            name  = \"X-Custom-Header\"\n+            value = \"Awesome\"\n+          }\n+        }\n+\n+        initial_delay_seconds = 3\n+        period_seconds        = 3\n+      }\n+    }\n+\n+    dns_config {\n+      nameservers = [\"1.1.1.1\", \"8.8.8.8\", \"9.9.9.9\"]\n+      searches    = [\"example.com\"]\n+\n+      option {\n+        name  = \"ndots\"\n+        value = 1\n+      }\n+\n+      option {\n+        name = \"use-vc\"\n+      }\n+    }\n+\n+    dns_policy = \"None\"\n+  }\n+}\n"
       }
    }


def mock_git_repo_multiline_yml(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str | Dict[str, str]]]:
    return {
       "cee6ad9d172ff447bd0afe8a478348b3ed6d3734": {
          "test-multiline-secrets.yml": "diff --git a/None b/test-multiline-secrets.yml\nindex 0000..0000 0000\n--- a/None\n+++ b/test-multiline-secrets.yml\n@@ -0,0 +1,15 @@\n+spec:\n+  - name: SOME_NAME\n+    value: some_value\n+  - value: Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE\n+    name: TEST_PASSWORD_1\n+    name1: TEST_PASSWORD_2\n+    value1: 1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35\n+  - name: TEST_PASSWORD_3\n+    value: PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h\n+  - name: TEST_PASSWORD_4\n+    value: emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z\n+  - name: TEST_PASSWORD_LONG_1\n+    value: m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN\n+  - name: TEST_PASSWORD_no_password\n+    value: RandomP@ssw0rd\n"
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


def mock_git_repo_commits_too_much(root_folder: str, last_commit_sha: str) -> Dict[str, Dict[str, str]]:
    res: Dict[str, Dict[str, str]] = {}
    keys = [get_random_string(40) for _i in range(10000)]
    for k in keys:
        res[k] = mock_case()
    return res
