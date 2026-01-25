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

# Upgrade pip and install Python dependencies (fixes CVE-2026-21441, CVE-2025-66471, CVE-2025-66418, GHSA-58pv-8j8x-9vj2)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir setuptools==79.0.0 urllib3==2.6.3

# Install Helm v3.17.2 (built with Go 1.25.5+ to fix CVE-2024-25621, CVE-2025-22869, CVE-2025-22868, and Go stdlib CVEs)
RUN HELM_VERSION="v3.17.2" \
    && curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o helm.tar.gz \
    && curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz.sha256sum" -o helm.sha256 \
    && cat helm.sha256 \
    && sha256sum helm.tar.gz \
    && grep $(sha256sum helm.tar.gz | awk '{print $1}') helm.sha256 \
    && tar -zxf helm.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    && rm -rf helm.tar.gz helm.sha256 linux-amd64

# Install Kustomize v5.7.1 (built with Go 1.25.5+ to fix Go stdlib CVEs: CVE-2025-47907, CVE-2025-58183, CVE-2025-61729)
RUN KUSTOMIZE_VERSION="v5.7.1" \
    && curl -fsSL "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz" -o kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz \
    && curl -fsSL "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/checksums.txt" -o kustomize.checksums.txt \
    && grep "kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz" kustomize.checksums.txt | sha256sum --check \
    && tar -zxf kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz \
    && mv kustomize /usr/bin/kustomize \
    && chmod +x /usr/bin/kustomize \
    && rm kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz kustomize.checksums.txt

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
