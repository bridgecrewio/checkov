FROM debian:bullseye
RUN apt-get install python3
RUN apt-get install python3 | grep "--force-yes"
RUN apt-get update && apt-get install \
    python3
RUN apt-get update &&\
    echo "--force-yes"
