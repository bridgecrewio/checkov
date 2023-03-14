FROM fedora:rawhide
RUN yum install python3
RUN dnf install -y python3
RUN tdnf install python3
RUN yum install python3 | grep "--nogpgcheck"
RUN dnf install python3 | grep "--nogpgcheck"
RUN tdnf install python3 | grep "--nogpgcheck"
RUN yum update && yum upgrade \
    python3
RUN dnf update && dnf upgrade \
    python3
RUN tdnf update && tdnf upgrade \
    python3
RUN yum update &&\
    echo "--nogpgcheck"
RUN dnf update ||\
    echo "--nogpgcheck"
RUN tdnf update ||\
    echo "--nogpgcheck"
