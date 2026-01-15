FROM python:3.12-slim

ENV RUN_IN_DOCKER=True

# Install security updates and required packages
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
 && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
 && rm -rf /var/lib/apt/lists/*

COPY kubernetes/requirements.txt /requirements.txt

# Install checkov with pip using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /requirements.txt

# Install kubectl v1.32.1 (built with Go 1.24.1+ to fix CVE-2025-22871)
RUN KUBECTL_VERSION="v1.32.1" \
 && curl -LO "https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
 && curl -LO "https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256" \
 && echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check \
 && chmod +x kubectl \
 && mv kubectl /usr/local/bin \
 && rm kubectl.sha256

# Create non-root user and group
RUN groupadd -g 12000 -r checkov \
 && useradd -u 12000 --no-log-init -r -g checkov checkov

# Create necessary directories
RUN mkdir /data && mkdir /app && mkdir /home/checkov \
 && chown checkov:checkov /data /app /home/checkov

# Install yq v4.45.1 (built with Go 1.24.1+ to fix CVE-2025-22871)
RUN YQ_VERSION="v4.45.1" \
 && curl -L -o /usr/bin/yq "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64" \
 && curl -L -o yq.sha256 "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/checksums" \
 && grep "yq_linux_amd64.tar.gz" yq.sha256 || true \
 && chmod +x /usr/bin/yq \
 && rm -f yq.sha256

COPY kubernetes/run_checkov.sh /app
WORKDIR /app
RUN chown checkov:checkov /app/run_checkov.sh && chmod +x /app/run_checkov.sh

# Switch to non-root user
USER checkov

ENTRYPOINT ["/app/run_checkov.sh"]
