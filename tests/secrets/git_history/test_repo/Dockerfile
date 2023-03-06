#checkov:skip=CKV_DOCKER_2:Healthcheck is not relevant for ephemral containers
#checkov:skip=CKV_DOCKER_3:User is created automatically by lambda runtime
FROM public.ecr.aws/lambda/python:3.9

ENV PIP_ENV_VERSION="2022.1.8"


COPY Pipfile Pipfile.lock ./

RUN pip install pipenv==${PIP_ENV_VERSION} \
 && pipenv lock -r > requirements.txt \
 && pipenv run pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" \
 && rm -f requirements.txt Pipfile Pipfile.lock \
 && pip uninstall -y pipenv

COPY src/ "${LAMBDA_TASK_ROOT}/src/"
COPY utilsPython/ "${LAMBDA_TASK_ROOT}/utilsPython/"

CMD ["src.secrets_setup.image.src.app.handler"]
