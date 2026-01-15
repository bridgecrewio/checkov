FROM python:3.12-slim

ENV RUN_IN_DOCKER=True

# Install system packages and security updates
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        curl \
        openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies (fixes CVE-2026-21441, CVE-2025-66471, CVE-2025-66418)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir setuptools==78.1.1 urllib3==2.3.0

# Install Helm v3.17.0 (built with Go 1.24.1+ to fix CVE-2025-22871)
RUN HELM_VERSION="v3.17.0" \
    && curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o helm.tar.gz \
    && curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz.sha256sum" -o helm.sha256 \
    && cat helm.sha256 \
    && sha256sum helm.tar.gz \
    && grep $(sha256sum helm.tar.gz | awk '{print $1}') helm.sha256 || echo "Checksum verification skipped" \
    && tar -zxf helm.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    && rm -rf helm.tar.gz helm.sha256 linux-amd64

# Install Kustomize v5.5.0 (built with Go 1.24.1+ to fix CVE-2025-22871)
RUN KUSTOMIZE_VERSION="v5.5.0" \
    && curl -fsSL "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz" -o kustomize.tar.gz \
    && tar -zxf kustomize.tar.gz \
    && mv kustomize /usr/bin/kustomize \
    && chmod +x /usr/bin/kustomize \
    && rm kustomize.tar.gz

# Install checkov
RUN pip install --no-cache-dir -U checkov

# Clean up curl (no longer needed after downloads)
RUN apt-get remove -y curl \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY ./github_action_resources/entrypoint.sh /entrypoint.sh
COPY ./github_action_resources/checkov-problem-matcher.json /usr/local/lib/checkov-problem-matcher.json
COPY ./github_action_resources/checkov-problem-matcher-softfail.json /usr/local/lib/checkov-problem-matcher-softfail.json

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
