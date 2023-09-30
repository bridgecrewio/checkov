FROM alpine:3.5
ENV ASDFGIT_SSL_NO_VERIFY=1
ENV ASDFGIT_SSL_NO_VERIFY 1
ENV ASDFGIT_SSL_NO_VERIFY Meteora
ARG GIT_SSL_NO_VERIFYASDF=1
ARG GIT_SSL_NO_VERIFYASDF 1
ARG GIT_SSL_NO_VERIFYASDF Meteora
ENV LP=Meteora ASDFGIT_SSL_NO_VERIFY=0
ENV ASDFGIT_SSL_NO_VERIFY=0 LP=Meteora
ENV LP=Meteora \
    ASDFGIT_SSL_NO_VERIFY=0
ENV LP=Meteora GIT_SSL_NO_VERIFYASDF=1

RUN unset GIT_SSL_NO_VERIFY
RUN git clone https://github.com/bridgecrewio/checkov.git awesome
RUN ASDFGIT_SSL_NO_VERIFY=1 git clone https://github.com/bridgecrewio/checkov.git awesome
RUN ASDFGIT_SSL_NO_VERIFY="1" git clone https://github.com/bridgecrewio/checkov.git awesome
RUN ASDFGIT_SSL_NO_VERIFY='1' git clone https://github.com/bridgecrewio/checkov.git awesome
RUN ASDFGIT_SSL_NO_VERIFY="0\"" git clone https://github.com/bridgecrewio/checkov.git awesome
RUN ASDFGIT_SSL_NO_VERIFY='0\'' git clone https://github.com/bridgecrewio/checkov.git awesome
RUN LP=Meteora \
    ASDFGIT_SSL_NO_VERIFY=0 git clone https://github.com/bridgecrewio/checkov.git awesome
RUN LP=Meteora GIT_SSL_NO_VERIFYASDF=1 git clone https://github.com/bridgecrewio/checkov.git awesome
RUN GIT_SSL_NO_VERIFYASDF=0 git clone https://github.com/bridgecrewio/checkov.git awesome
