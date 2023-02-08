FROM alpine:3.5
RUN pip install checkov
RUN pip3 install checkov
RUN pip install checkov | grep "--trusted-host"
RUN pip3 install checkov; grep "--trusted-host"
RUN pip install checkov &&\
    echo "--trusted-host"
RUN pip3 install checkov ||\
    grep "--trusted-host" /etc/passwd
