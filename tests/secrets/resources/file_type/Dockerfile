FROM base:1

RUN apt install first_update_line \
&& apt update first_update_line
RUN apt update second_update_line
RUN apt update third_update_line
USER bob
ENV AWS_ACCESS_KEY_ID="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPL3KEY"
ENV AWS_SECRET_ACCESS_KEY="AKIAIOSFODNN7EXAMPL3"

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
~                                            
