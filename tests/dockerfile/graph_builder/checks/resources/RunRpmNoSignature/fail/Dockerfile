FROM fedora:rawhide
RUN rpm -i --nodigest --nosignature --noverify --nofiledigest python3.rpm
RUN rpm -i --nodigest python3.rpm
RUN rpm -i --nosignature python3.rpm
RUN rpm -i --noverify python3.rpm
RUN rpm -i --nofiledigest python3.rpm
RUN rpm \
    --nodigest \
    --nosignature \
    --noverify \
    --nofiledigest \
    -i python3.rpm
RUN rpm \
    -i python3.rpm \
    --nodigest \
    --nosignature \
    --nofiledigest \
    --noverify
RUN echo "prodsec" && rpm --nodigest --nosignature --noverify --nofiledigest -i python3.rpm
