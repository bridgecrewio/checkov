FROM ubuntu

RUN apt install curl
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        git && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    cd /var/lib && \
    rm -rf apt dpkg cache log