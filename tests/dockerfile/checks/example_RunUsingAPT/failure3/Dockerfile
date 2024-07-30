FROM ubuntu

RUN apt update && \
    apt-get install --yes --no-install-recommends \
        git && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    cd /var/lib && \
    rm -rf apt dpkg cache log