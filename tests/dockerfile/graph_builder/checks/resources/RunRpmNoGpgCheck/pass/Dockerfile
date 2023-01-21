FROM fedora:rawhide
RUN yum install python3
RUN dnf install -y python3
RUN rpm -i python3.rpm
RUN yum install python3 | grep "--nogpgcheck"
RUN dnf install python3 | grep "--nogpgcheck"
RUN rpm -i python3.rpm | grep "--nogpgcheck"
RUN yum update && yum upgrade \
    python3
RUN dnf update && dnf upgrade \
    python3
RUN rpm -i python3.rpm && rpm -V \
    python3
RUN yum update &&\
    echo "--nogpgcheck"
RUN dnf update ||\
    echo "--nogpgcheck"
RUN rpm -i python3.rpm ;\
    echo "--nogpgcheck"

