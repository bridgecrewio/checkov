FROM python:3.10-alpine

ENV RUN_IN_DOCKER=True

RUN apk add --no-cache git util-linux bash openssl curl

RUN apk add --no-cache --virtual .build_deps build-base libffi-dev \
 && pip install --no-cache-dir -U checkov \
 && apk del .build_deps

RUN wget -q -O get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3; chmod 700 get_helm.sh; VERIFY_CHECKSUM=true ./get_helm.sh; rm ./get_helm.sh
RUN wget -q -O get_kustomize.sh https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh; chmod 700 get_kustomize.sh; ./get_kustomize.sh; mv /kustomize /usr/bin/kustomize; rm ./get_kustomize.sh

COPY ./github_action_resources/entrypoint.sh /entrypoint.sh
COPY ./github_action_resources/checkov-problem-matcher.json /usr/local/lib/checkov-problem-matcher.json
COPY ./github_action_resources/checkov-problem-matcher-softfail.json /usr/local/lib/checkov-problem-matcher-softfail.json

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
