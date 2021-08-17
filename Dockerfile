FROM python:3.7-alpine

ARG UID=1000
ARG GID=1000
ARG USERNAME=checkov

RUN apk update && apk add --no-cache git util-linux bash openssl

RUN pip install --no-cache-dir -U checkov
RUN wget -q -O get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3; chmod 700 get_helm.sh; VERIFY_CHECKSUM=true ./get_helm.sh; rm ./get_helm.sh

RUN addgroup -S -g ${GID} ${USERNAME} && \
    adduser -S -D -u ${UID} -G ${USERNAME} ${USERNAME} 

COPY --chown=${UID}:${GID} ./github_action_resources/entrypoint.sh /entrypoint.sh
COPY --chown=${UID}:${GID} ./github_action_resources/checkov-problem-matcher.json /usr/local/lib/checkov-problem-matcher.json
COPY --chown=${UID}:${GID} ./github_action_resources/checkov-problem-matcher-softfail.json /usr/local/lib/checkov-problem-matcher-softfail.json

USER ${UID}

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
