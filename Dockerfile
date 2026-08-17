FROM python:3.11-slim

ENV RUN_IN_DOCKER=True

RUN set -eux; \
    apt-get update; \
    apt-get -y upgrade; \
    apt-get install -y --no-install-recommends \
            ca-certificates \
            git \
            curl \
            openssh-client \
    ; \
    \
    pip install setuptools==78.1.1 urllib3==2.2.2;  \
    curl -fL --retry 5 --retry-all-errors --retry-delay 3 -sSo get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3; \
    chmod 700 get_helm.sh; \
    helm_ok=0; for i in 1 2 3; do if VERIFY_CHECKSUM=true ./get_helm.sh; then helm_ok=1; break; else echo "get-helm-3 attempt $i failed, retrying..."; sleep 5; fi; done; [ "$helm_ok" = "1" ] || { echo "get-helm-3 failed after retries"; exit 1; }; \
    rm ./get_helm.sh; \
    \
    curl -fL --retry 5 --retry-all-errors --retry-delay 3 -sSo get_kustomize.sh https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh; \
    chmod 700 get_kustomize.sh; \
    k_ok=0; for i in 1 2 3; do if ./get_kustomize.sh; then k_ok=1; break; else echo "install_kustomize.sh attempt $i failed, retrying..."; rm -f /kustomize; sleep 5; fi; done; [ "$k_ok" = "1" ] || { echo "install_kustomize.sh failed after retries"; exit 1; }; mv /kustomize /usr/bin/kustomize; \
    rm ./get_kustomize.sh; \
    \
    apt-get remove -y curl; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -U checkov

COPY ./github_action_resources/entrypoint.sh /entrypoint.sh
COPY ./github_action_resources/checkov-problem-matcher.json /usr/local/lib/checkov-problem-matcher.json
COPY ./github_action_resources/checkov-problem-matcher-softfail.json /usr/local/lib/checkov-problem-matcher-softfail.json

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
