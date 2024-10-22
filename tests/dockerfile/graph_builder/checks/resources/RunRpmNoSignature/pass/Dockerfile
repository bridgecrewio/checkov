FROM fedora:rawhide
RUN rpm -i python3.rpm
RUN rpm -i python3.rpm | grep "--nosignature"
RUN rpm -i python3.rpm && rpm -V \
    python3
RUN rpm -i python3.rpm ;\
    echo "--nodigest"
RUN rpm -i python3.rpm ;\
    echo "--noverify"
RUN rpm -i python3.rpm ||\
    echo "--nofiledigest"
