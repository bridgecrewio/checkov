FROM base:1

RUN apt install first_update_line \
&& apt update first_update_line
RUN apt update second_update_line
RUN apt update third_update_line

USER bob

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
~                                            