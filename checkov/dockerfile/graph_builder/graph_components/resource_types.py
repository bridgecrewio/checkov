from enum import Enum


class ResourceType(str, Enum):
    ADD = "ADD"
    ARG = "ARG"
    CMD = "CMD"
    COPY = "COPY"
    ENTRYPOINT = "ENTRYPOINT"
    ENV = "ENV"
    EXPOSE = "EXPOSE"
    FROM = "FROM"
    HEALTHCHECK = "HEALTHCHECK"
    LABEL = "LABEL"
    MAINTAINER = "MAINTAINER"
    ONBUILD = "ONBUILD"
    RUN = "RUN"
    SHELL = "SHELL"
    STOPSIGNAL = "STOPSIGNAL"
    USER = "USER"
    VOLUME = "VOLUME"
    WORKDIR = "WORKDIR"

    def __str__(self) -> str:
        # needed, because of a Python 3.11 change
        return self.value
