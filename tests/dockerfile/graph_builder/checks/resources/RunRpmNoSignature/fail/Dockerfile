FROM fedora:rawhide
RUN rpm -i --nodigest --nosignature --noverify python3.rpm
RUN rpm -i --nodigest python3.rpm
RUN rpm -i --nosignature python3.rpm
RUN rpm -i --noverify python3.rpm
RUN rpm \
    --nodigest \
    --nosignature \
    --noverify \
    -i python3.rpm
RUN rpm \
    -i python3.rpm \
    --nodigest \
    --nosignature \
    --noverify
RUN echo "prodsec" && rpm --nodigest --nosignature --noverify -i python3.rpm
