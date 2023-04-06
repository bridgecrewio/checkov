FROM fedora:rawhide
RUN yum-config-manager --disable updates
RUN yum-config-manager --disable sslverify
RUN yum-config-manager --disable \* &> /dev/null
RUN yum-config-manager --setopt=install_weak_deps=False --save
RUN yum-config-manager --save --setopt=proxy=http://example.com >/dev/null
RUN yum-config-manager --save --setopt=something-base.sslverify=1
RUN yum-config-manager --save --setopt=something-base.sslverify=true
RUN yum-config-manager --save --setopt=something-base.sslverify=on
RUN yum-config-manager --save --setopt=sslverify=1
RUN yum-config-manager --save --setopt=sslverify=true
RUN yum-config-manager --save --setopt=sslverify=yes
RUN yum-config-manager --save --setopt=notthedroids=0
RUN yum-config-manager --save --setopt=yourelookingfor=false
RUN yum-config-manager --save --setopt=thesearenot=no
RUN yum-config-manager --setopt=sslverify=yes --add-repo https://example.com/yummy.repo
RUN yum-config-manager --save --setopt=install_weak_deps=False | echo "--setopt=something-base.sslverify=0"
RUN yum-config-manager --save --setopt=install_weak_deps=False && echo "--setopt=main.sslverify=0"
RUN yum-config-manager --save --setopt=install_weak_deps=False || echo "--setopt=sslverify=0"
