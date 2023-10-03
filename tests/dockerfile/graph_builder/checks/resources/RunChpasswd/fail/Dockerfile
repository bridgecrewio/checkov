FROM ubuntu:20.04
RUN echo 'root:root' | chpasswd
RUN echo 'root:' | chpasswd
RUN apt-get update && echo "someuser:somepasswd" | chpasswd && echo "lol"
RUN apt-get update ;\
    apt-get clean ; \
    echo 'root:root' | chpasswd
RUN chpasswd < input.txt