FROM python:3.11-slim

ENV RUN_IN_DOCKER=True

RUN apt-get update \
 && apt-get install -y --no-install-recommends git curl  \
 && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
 && rm -rf /var/lib/apt/lists/*;

COPY kubernetes/requirements.txt /requirements.txt

# Install checkov
RUN pip install -r /requirements.txt

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl \
    && chmod +x kubectl && mv kubectl /usr/local/bin
RUN groupadd -g 12000 -r checkov && useradd -u 12000 --no-log-init -r -g checkov checkov
RUN mkdir /data && mkdir /app && mkdir /home/checkov
RUN chown checkov:checkov /data /app /home/checkov
RUN curl -L -o /usr/bin/yq https://github.com/mikefarah/yq/releases/download/v4.16.2/yq_linux_amd64 \
    && chmod +x /usr/bin/yq

COPY kubernetes/run_checkov.sh /app
WORKDIR /app
RUN chown checkov:checkov /app/run_checkov.sh && chmod +x /app/run_checkov.sh

ENTRYPOINT ["/app/run_checkov.sh"]
